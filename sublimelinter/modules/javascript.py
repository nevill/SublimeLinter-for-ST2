import json
import re
import subprocess

from base_linter import BaseLinter, INPUT_METHOD_TEMP_FILE

CONFIG = {
    'language': 'JavaScript',
    'executable': 'jshint',
    'test_existence_args': '-v',
    'input_method': INPUT_METHOD_TEMP_FILE
}


class Linter(BaseLinter):
    LINT_RE = re.compile(r'^.+line (?P<line>\d+), col (?P<col>\d+), \s*(?P<message>.+)')

    def __init__(self, config):
        super(Linter, self).__init__(config)

    def get_lint_args(self, view, code, filename):
        path = self.find_file('.jshintrc', view, True)
        if path is None:
            return [filename]
        else:
            return ['-c', path, filename]

    def parse_errors(self, view, errors, lines, errorUnderlines, violationUnderlines, warningUnderlines, errorMessages, violationMessages, warningMessages):
        for line in errors.splitlines():
            match = re.match(self.LINT_RE, line)

            if match:
                error, col, line = match.group('message'), match.group('col'), match.group('line')
                lineno = int(line)
                self.add_message(lineno, lines, error, errorMessages)
                self.underline_range(view, lineno, int(col) - 1, errorUnderlines)
