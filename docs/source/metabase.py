"""
A Sphinx builder putting documentation on Metabase.

"""

import json
import os
from pathlib import Path
import re
import time
from typing import Any, Dict, List, Optional, Union

import sphinx.writers.text
import requests
from docutils.core import publish_string
from sphinx.application import Sphinx
from sphinx.builders.dummy import DummyBuilder
from sphinx.errors import ConfigError
from sphinx.util import logging
from sphinx.writers.text import TextTranslator, TextWriter

logger = logging.getLogger(__name__)

# Such a shame to depend on globals…
sphinx.writers.text.MAXWIDTH = float('inf')


class MetabaseBuilder(DummyBuilder):
    """Sphinx builder used to deploy descriptions on Metabase."""
    name = 'metabase'
    epilog = 'Metabase documentation has been updated.'
    default_translator_class = TextTranslator

    def init(self) -> None:
        self.tables: dict = {}
        self.session: requests.Session = self._create_session()

        # Either an API key or username/password are required.
        if (
            not self.config.metabase_api_key and
            not (self.config.metabase_username and self.config.metabase_password)
        ):
            raise ConfigError(
                'Either metabase_api_key or metabase_username and metabase_password '
                'must be set for the metabase builder'
            )

    def _get(self, path: str) -> Dict[str, Any]:
        """Launch a GET requests on Metabase API."""
        with self.session.get(f'{self.config.metabase_url}/{path}') as response:
            response.raise_for_status()
            return response.json()

    def _put(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """Launch a PUT requests on Metabase API."""
        with self.session.put(f'{self.config.metabase_url}/{path}', json=json) as response:
            response.raise_for_status()
            return response.json()

    def _create_session(self) -> requests.Session:
        session = requests.Session()
        session.headers['Content-Type'] = 'application/json'

        # Prefer an API key.
        if self.config.metabase_api_key:
            session.headers['X-API-Key'] = self.config.metabase_api_key
            return session

        # Gather session data.
        session_data = self._read_session_data()
        if not session_data:
            json = {
                'username': self.config.metabase_username,
                'password': self.config.metabase_password,
            }
            logger.debug('Creating new Metabase session')
            with session.post(f'{self.config.metabase_url}/session', json=json) as response:
                response.raise_for_status()
                session_data = response.json()
            self._store_session_data(session_data)

        session.headers['X-Metabase-Session'] = session_data['id']

        return session

    def _session_cache_path(self) -> Path:
        xdg_cache_home = Path(os.environ.get('XDG_CACHE_HOME', '~/.cache')).expanduser()
        return xdg_cache_home / 'sphinx-metabase-session.json'

    def _store_session_data(self, data: Dict) -> None:
        path = self._session_cache_path()
        logger.debug(f'Storing Metabase session data at {path}')
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with path.open('r') as f:
                full_data = json.load(f)
        except FileNotFoundError:
            full_data = {}

        full_data[self.config.metabase_url] = {
            'data': data,
            'created': int(time.time()),
        }
        with path.open('w') as f:
            json.dump(full_data, f, indent=2)
        path.chmod(0o600)

    def _read_session_data(self) -> Optional[Dict]:
        path = self._session_cache_path()

        logger.debug(f'Reading Metabase session data from {path}')
        try:
            with path.open('r') as f:
                full_data = json.load(f)
        except FileNotFoundError:
            logger.debug(f'No Metabase session data at {path}')
            return None

        entry = full_data.get(self.config.metabase_url)
        if not entry:
            logger.debug(f'No entry for Metabase {self.config.metabase_url} in {path}')
            return None

        # By default, metabase sessions are valid for 2 weeks. However, that's configurable, so
        # reuse the session data for 1 week.
        #
        # https://www.metabase.com/learn/administration/metabase-api#authenticate-your-requests-with-a-session-token
        max_age = 60 * 60 * 24 * 7
        age = time.time() - entry.get('created', 0)
        if age > max_age:
            logger.debug(f'Ignoring session data in {path} older than 1 week')
            return None

        return entry.get('data')

    @staticmethod
    def _none_if_blank(value: str) -> Union[str, None]:
        """Return the value with whitespace stripped or None if it's blank."""
        value = value.strip()
        if len(value) == 0:
            return None
        return value

    def format_description(self, lines: List[str]) -> str:
        """Format tables and fields descriptions from ReST to plain text."""

        # Unwrap lines
        unwrapped_lines = []
        for line in lines:
            empty = not unwrapped_lines or not unwrapped_lines[-1] or not line
            list_item = line and line.startswith('- ')
            block_start = (
                line and line.startswith('  ') and
                not empty and not unwrapped_lines[-1].startswith('  '))
            if empty or list_item or block_start:
                unwrapped_lines.append(line)
            else:
                unwrapped_lines[-1] += ' ' + line.lstrip()

        # Manually format and remove useless information
        clean_lines = []
        for line in unwrapped_lines:
            line = line.replace(':class:', '')
            if not line:
                if clean_lines and clean_lines[-1]:
                    clean_lines.append(line)
                continue
            elif re.match('^:[A-Za-z ]*:', line):
                continue
            elif line.startswith('.. versionadded::'):
                continue
            elif line.startswith('See '):
                continue
            clean_lines.append(line)
        source = '\n'.join(clean_lines).strip()

        # Transform ReST into plain text
        writer = TextWriter(self)
        plain_text = publish_string(source=source.encode('utf-8'), writer=writer).decode('utf-8')
        plain_text = plain_text.replace('\n\n* ', '\n− ')  # Use hyphens as list bullets

        # Split description and points of interest
        lines = plain_text.split('\n')
        if len(lines) > 2 and lines[1] == '':
            description = self._none_if_blank(lines[0])
            points_of_interest = self._none_if_blank('\n'.join(lines[2:]))
        else:
            description = self._none_if_blank('\n'.join(lines))
            points_of_interest = None

        return description, points_of_interest

    def finish(self) -> None:
        """Finish the Sphinx building process."""

        # Use real table names as self.tables keys
        self.tables = {table['obj'].__tablename__: table for table in self.tables.values()}

        # Tables and database ID
        logger.info('\nUpdating tables\n')
        tables = [table for table in self._get('table') if table['db']['name'] == 'Azafea']
        db_id = None
        for i, table in enumerate(tables, start=1):
            progress = f'({i}/{len(tables)})'

            # Ignore tables not included in documentation
            if table['name'] not in self.tables:
                logger.info(f'{progress} Ignoring table {table["name"]}')
                continue

            # Set database ID for fields
            db_id = table['db_id']

            # Store documentation for tables
            logger.info(f'{progress} Updating table {table["name"]}')
            description, points_of_interest = self.format_description(
                self.tables[table['name']]['lines'])
            path = f'table/{table["id"]}'
            data = {
                'description': description,
                'points_of_interest': points_of_interest,
            }
            if self.config.metabase_dry_run:
                logger.info(
                    f'Dry run, not updating table {table["id"]} with data {data}'
                )
            else:
                self._put(path, json=data)

        # Quit early if no table has been found
        if db_id is None:
            return

        # Fields
        logger.info('\nUpdating fields\n')
        db_fields = self._get(f'database/{db_id}/fields')
        for i, db_field in enumerate(db_fields, start=1):
            # Get details about field
            field = self._get(f'field/{db_field["id"]}')
            progress = f'({i}/{len(db_fields)})'

            # Ignore unknown fields and fields from unknown tables
            if field['table']['name'] not in self.tables:
                logger.info(f'{progress} Ignoring fields from table {field["table"]["name"]}')
                continue
            if field['name'] not in self.tables[field['table']['name']]['fields']:
                logger.info(f'{progress} Ignoring field {field["table"]["name"]}.{field["name"]}')
                continue

            # Store documentation for fields
            logger.info(f'{progress} Updating field {field["table"]["name"]}.{field["name"]}')
            description, points_of_interest = self.format_description(
                self.tables[field['table']['name']]['fields'][field['name']])
            path = f'field/{field["id"]}'
            data = {
                'description': description,
                'points_of_interest': points_of_interest,
            }
            if self.config.metabase_dry_run:
                logger.info(
                    f'Dry run, not updating field {field["id"]} with data {data}'
                )
            else:
                self._put(path, json=data)


def process_docstring(app: Sphinx, type_: str, name: str, obj: Any, data: Dict[str, Any],
                      lines: List[str]) -> None:
    """Find and store useful information when docstrings are processed."""
    # Ignore other builders
    if app.builder.name != 'metabase':
        return

    # Find tables and fields in documentation
    tables = app.builder.tables
    if type_ == 'class' and hasattr(obj, '__tablename__'):
        tables[obj.__name__] = {'obj': obj, 'fields': {}, 'lines': lines}
    elif type_ == 'attribute':
        _, class_name, field_name = name.rsplit('.', 2)
        if class_name not in app.builder.tables:
            logger.error(f'Unknown field {name}')
        tables[class_name]['fields'][field_name] = lines


def setup(app: Sphinx) -> None:
    """Setup the Sphinx application."""
    default_url = os.environ.get('METABASE_URL', 'https://metabase.endlessm.com/api')
    app.add_config_value('metabase_url', default_url, 'env')
    app.add_config_value('metabase_api_key', os.environ.get('METABASE_API_KEY'), 'env')
    app.add_config_value('metabase_username', os.environ.get('METABASE_USERNAME'), 'env')
    app.add_config_value('metabase_password', os.environ.get('METABASE_PASSWORD'), 'env')
    dry_run_env = os.environ.get('METABASE_DRY_RUN', '')
    dry_run = True if dry_run_env.lower() in ('y', 'yes', '1', 'true') else False
    app.add_config_value('metabase_dry_run', dry_run, 'env')
    app.connect('autodoc-process-docstring', process_docstring)
    app.add_builder(MetabaseBuilder)
