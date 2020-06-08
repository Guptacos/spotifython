""" Get a list of files to lint """

# Use subprocess instead of glob to have access to git ls-files
import subprocess
from sys import argv

# Any files or folders to ignore. Does not support regex.
lint_ignores = [
    'docs',
    '__init__.py',
    'venv',
    'lint.py',
    'setup.py',
    'response.py',
]

def keep_file(filename):
    """ Return True if the file should be linted, else False """
    if not filename.endswith('.py'):
        return False

    for ignore in lint_ignores:
        if ignore in filename:
            return False

    return True

def main():
    """ Get a list of filenames to lint, formated as command line arguments

    Args:
        argv[1]: one of:
            all: lint all files that should be linted
            diff: only lint files changed in this branch
    """
    # Validate inputs
    if len(argv) != 2 or argv[1] not in ['all', 'diff']:
        print('USAGE:')
        print(f'All lint files: python {argv[0]} all')
        print(f'Diff lint files: python {argv[0]} diff')
        exit(-1)

    # Pick which command to use to get filenames
    if argv[1] == 'all':
        command = 'git ls-files'
    else:
        # --diff-filter=d excludes deleted files
        command = 'git diff origin/master --name-only --diff-filter=d'


    # Run the command in the shell
    all_files = subprocess.check_output(command, encoding='UTF-8', shell=True)

    for filename in all_files.split('\n'):
        if keep_file(filename):
            print(filename, end=' ')

if __name__ == '__main__':
    main()
