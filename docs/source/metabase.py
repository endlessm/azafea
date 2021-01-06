"""
A Sphinx builder putting documentation on Metabase.

"""

import os
import re
from typing import Any, Dict, List

import sphinx.writers.text
import requests
from docutils.core import publish_string
from sphinx.application import Sphinx
from sphinx.builders.dummy import DummyBuilder
from sphinx.util import logging
from sphinx.writers.text import TextTranslator, TextWriter

logger = logging.getLogger(__name__)

# Such a shame to depend on globals…
sphinx.writers.text.MAXWIDTH = float('inf')


class MetabaseBuilder(DummyBuilder):
    """Sphinx builder used to deploy descriptions on Metabase."""
    name = 'metabase'
    default_translator_class = TextTranslator
    tables = None
    writer = None
    _session = None

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

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()

            # Gather authentication headers
            json = {
                'username': self.config.metabase_username,
                'password': self.config.metabase_password,
            }
            with self._session.post(f'{self.config.metabase_url}/session', json=json) as response:
                response.raise_for_status()
                self._session.headers.update({
                    'Content-Type': 'application/json',
                    'X-Metabase-Session': response.json()['id'],
                })

        return self._session

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
            return lines[0].strip(), '\n'.join(lines[2:]).strip()
        else:
            return '\n'.join(lines).strip(), None

    def finish(self) -> None:
        """Finish the Sphinx building process."""

        # Use real table names as self.tables keys
        self.tables = {table['obj'].__tablename__: table for table in self.tables.values()}

        # Tables and database ID
        logger.info('\nUpdating tables\n')
        tables = [table for table in self._get('table') if table['db']['name'] == 'Azafea']
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
            self._put(f'table/{table["id"]}', json={
                'description': description, 'points_of_interest': points_of_interest})

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
            self._put(f'field/{field["id"]}', json={
                'description': description, 'points_of_interest': points_of_interest})


def process_docstring(app: Sphinx, type_: str, name: str, obj: Any, data: Dict[str, Any],
                      lines: List[str]) -> None:
    """Find and store useful information when docstrings are processed."""
    # Ignore other builders
    if app.builder.name != 'metabase':
        return

    # Create tables dict if not set
    if app.builder.tables is None:
        app.builder.tables = {}

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
    app.add_config_value('metabase_username', os.environ.get('METABASE_USERNAME'), 'env')
    app.add_config_value('metabase_password', os.environ.get('METABASE_PASSWORD'), 'env')
    app.connect('autodoc-process-docstring', process_docstring)
    app.add_builder(MetabaseBuilder)
