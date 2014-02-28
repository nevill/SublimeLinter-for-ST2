import json
import os

from .base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'executable': 'tslint',
    'lint_args': [
        '-f','{filename}',
        '-c', '{configPath}',
        '-t', 'json'
    ],
    'language': 'TypeScript',
    'input_method': INPUT_METHOD_TEMP_FILE
}


class Linter(BaseLinter):

    def __init__(self, config):
        super(Linter, self).__init__(config)


    def find_file_path(self, filename, view):
        '''Find a file path with the given name, starting in the view's directory,
           then ascending the file hierarchy up to root.'''
        path = view.file_name()
        # quit if the view is temporary
        if not path:
            return None

        dirname = os.path.dirname(path)

        while True:
            print(dirname,filename)
            path = os.path.join(dirname, filename)

            if os.path.isfile(path):
                return path

            # if we hit root, quit
            parent = os.path.dirname(dirname)

            if parent == dirname:
                return None
            else:
                dirname = parent

    def get_lint_args(self, view, code, filename):
        lintArgs = self.lint_args or []
        settings = view.settings().get('SublimeLinter', {}).get(self.language, {})
        configPath = self.find_file_path('tslint.json', view)

        if configPath is None:
            raise ValueError("You must include a tslint.json file in your project")

        if settings:
            if 'lint_args' in settings:
                lintArgs = settings['lint_args']

            cwd = settings.get('working_directory', '').encode('utf-8')

            if cwd and os.path.isabs(cwd) and os.path.isdir(cwd):
                os.chdir(cwd)

        return [arg.format(filename=filename,configPath=configPath) for arg in lintArgs]

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        try:
            errors = json.loads(errors.strip() or '[]')
        except ValueError:
            raise ValueError("Error from {0}: {1}".format('tslint', errors))

        for error in errors:
            lineno = error['startPosition']['line'] + 1
            startchar = error['startPosition']['character'];
            length = error['endPosition']['character']-startchar+1;
            self.add_message(lineno, lines, error['failure'], errorMessages)
            self.underline_range(view, lineno, startchar, errorUnderlines, length)
