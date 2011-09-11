'Should, a small command line app for working with plain text todo files'
import argparse
import os
import platform
import re

# constants
# {{{

PROJECT_CHAR = '+'
TAG_CHAR = '@'

# }}}
# files
# {{{

def get_absolute_file_name(name):
    'get the absolute file name relative to should.py'
    return os.path.join(os.path.dirname(__file__), '%s.txt' % name)

def get_named_file_lines(name):
    'get the lines from a named file (assuming .txt extension)'
    try:
        with open(get_absolute_file_name(name), 'rb') as named_file:
            return [line for line
                    in named_file.read().split('\n')
                    if line != '']
    except IOError:
        return []

def write_named_file_lines(name, lines):
    'write lines from a list to a file'
    try:
        with open(get_absolute_file_name(name), 'wb') as out_file:
            for line in lines:
                out_file.write('%s\n' % line)
    except IOError:
        print 'could not write lines to file, here they are:'
        print lines

# }}}
# todo actions
# {{{

def complete_todo(args):
    'complete a todo specified in args.n'
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        if i == int(args.n):
            archive_todo(todo)
            del todos[i]

    write_named_file_lines('todo', todos)

def archive_todo(text):
    'archive a line of text'
    todos = get_named_file_lines('archive')
    todos.append(text)
    write_named_file_lines('archive', todos)

def add_todo(args):
    'add a todo to the text file'
    todos = get_named_file_lines('todo')
    todos.append(args.text)
    print 'adding todo:', args.text
    write_named_file_lines('todo', todos)

# }}}
# search methods
# {{{

def search_todos(args):
    'search todos on a single matched string'
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        tags = extract_tags(todo)
        project = extract_project(todo)

        has_text = todo.find(args.text) != -1 if args.text else True
        has_tags = all([tag in tags for tag in args.tags]) \
            if args.tags else True
        has_project = project == args.project \
            if args.project else True
        lacks_tags = all([tag not in tags for tag in args.not_tags]) \
            if args.not_tags else True
        lacks_project = all([project not in args.not_project]) \
            if args.not_project else True

        if all([has_text, has_tags, has_project, lacks_tags, lacks_project]):
            print format_verbose_line(args, i, todo)

# }}}
# information from todo
# {{{

def extract_tags(text):
    '''
    find all the tags in a task

    >>> extract_tags('This is a task +project @singletag')
    ['singletag']

    >>> extract_tags('This is a task +project @tagone @tagtwo')
    ['tagone', 'tagtwo']

    >>> extract_tags('Email test@example.org +project @email @example')
    ['email', 'example']
    '''
    return re.findall(r'(?<=\s%s)\w+' % TAG_CHAR, text)

def extract_project(text):
    '''
    find the projects in a task

    >>> extract_project('Eat some fudge +fudgeeating @yummy')
    'fudgeeating'

    >>> extract_project('Talk to Jim+John +bigproject @inperson')
    'bigproject'

    >>> extract_project('Talk to Jim + John +bigproject @inperson')
    'bigproject'
    '''
    match = re.search(r'(?<=\s\%s)\w+' % PROJECT_CHAR, text)
    if match is None:
        return ''
    else:
        return text[match.start():match.end()]

def extract_text(text):
    '''
    find the text in a task

    Regular text is just easy.
        >>> extract_text('Eat some fudge +fudgeeating @yummy')
        'Eat some fudge'

    Make sure that emails are not excluded.
        >>> extract_text('Email test@example.org +bigproject @email')
        'Email test@example.org'

    Don't exclude plusses inside the text.
        >>> extract_text('Talk to Jim+John +bigproject @inperson')
        'Talk to Jim+John'

    Even if there are spaces between them.
        >>> extract_text('Talk to Jim + John +bigproject @inperson')
        'Talk to Jim + John'
    '''
    # remove project
    text = text.replace(PROJECT_CHAR + extract_project(text), '')

    # remove tags
    for tag in extract_tags(text):
        text = text.replace(TAG_CHAR + tag, '')

    return text.strip()

# }}}
# formatting
# {{{

def format_verbose_line(args, i, text):
    'format a line of text in a verbose format'
    return '%s: %s' % (wrap_color(args, str(i), 'blue'), text)

COLORS = {
    'grey': '\033[1;30m',
    'red': '\033[1;31m',
    'green': '\033[1;32m',
    'yellow': '\033[1;33m',
    'blue': '\033[1;34m',
    'magenta': '\033[1;35m',
    'cyan': '\033[1;36m',
    'white': '\033[1;37m',
    'hred': '\033[1;41m',
    'hgreen': '\033[1;42m',
    'hbrown': '\033[1;43m',
    'hblue': '\033[1;44m',
    'hmagenta': '\033[1;45m',
    'hcyan': '\033[1;46m',
    'hgrey': '\033[1;47m',
    'hcrimson': '\033[1;48m',
    'end': '\033[0;m' if platform.uname()[0] == 'Darwin' else '\033[1;m',
}

def wrap_color(args, text, *colors):
    'wrap text in a color defined in COLORS. If opts.color is "n", don\'t.'
    if args.color == 'n':
        return text

    for color in colors:
        try:
            text = COLORS[color] + text + COLORS['end']
        except KeyError:
            pass

    return text

# }}}
## EXECUTION ##
# {{{
def comma_separated_string(string):
    'parse a comma separated list of values'
    return string.split(',')

def run():
    'parse args to run functions'
    # global options
    parser = argparse.ArgumentParser(
        description='manage text-based task list from the command line.'
    )
    parser.add_argument(
        '-c', '--color',
        default='y', choices=['y', 'n'],
        help="colorized output"
    )
    parser.add_argument(
        '--version',
        action='version', version='%(prog)s 1.1'
    )

    subparsers = parser.add_subparsers()

    # add
    add_parser = subparsers.add_parser('add', help='add a new task')
    add_parser.add_argument('text', help='the text of your task')
    add_parser.set_defaults(func=add_todo)

    # complete
    complete_parser = subparsers.add_parser('complete', help='complete a task')
    complete_parser.add_argument(
        'n', type=int,
        help='The task number to mark as completed'
    )
    complete_parser.set_defaults(func=complete_todo)

    # show
    search_parser = subparsers.add_parser('show', help='show or find tasks')
    search_parser.add_argument(
        'text', help='the text of your search',
        nargs='?'
    )
    search_parser.add_argument(
        '-p', '--project',
        help='name of a project'
    )
    search_parser.add_argument(
        '-t', '--tags',
        type=comma_separated_string,
        help='name(s) of tag(s) (comma separated)'
    )
    search_parser.add_argument(
        '--not-project',
        type=comma_separated_string,
        help='name(s) of project(s) to exclude (comma separated)'
    )
    search_parser.add_argument(
        '--not-tags',
        type=comma_separated_string,
        help='name(s) of tag(s) to exclude (comma separated)'
    )
    search_parser.set_defaults(func=search_todos)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run()

# }}}
