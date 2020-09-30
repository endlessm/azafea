"""
A Sphinx extension adding table name, UUID and payload type to table classes.

"""


def process_docstring(app, what, name, obj, options, lines):
    for i, line in enumerate(lines):
        if line.startswith(':UUID name:'):
            lines.insert(i, f':table name: ``{obj.__tablename__}``')
            lines.insert(i + 1, f':payload type: ``{obj.__payload_type__ or "NULL"}``')
            lines.insert(i + 2, f':UUID: ``{obj.__event_uuid__}``')
            return


def setup(app):
    app.connect('autodoc-process-docstring', process_docstring)
