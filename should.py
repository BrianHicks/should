'Should, a small command line app for working with plain text todo files'
import argparse
import os
import platform
import random
import re

# constants
# {{{

PROJECT_CHAR = '+'
TAG_CHAR = '@'
DEPENDENCY_CHAR = '^'

# }}}
# files
# {{{

def get_absolute_file_name(name):
    'get the absolute file name relative to should.py'
    try:
        return os.path.join(os.path.dirname(__file__), '%s.txt' % name)
    except NameError:
        return '%s.txt' % name

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

cache = {}
def get_cached_file_lines(name):
    'get cached lines from a file'
    if name in cache:
        return cache[name]
    else:
        lines = get_named_file_lines(name)
        cache[name] = lines
        return lines

# }}}
# todo actions
# {{{

def complete_todo(args):
    'complete a todo specified in args.ids'
    todos = get_cached_file_lines('todo')
    archive = get_cached_file_lines('archive')
    remaining_todos = []

    for todo in todos:
        if extract_id(todo) not in args.ids:
            remaining_todos.append(todo)
        else:
            archive.append(todo)
            print 'completed:', todo

    write_named_file_lines('archive', archive)
    write_named_file_lines('todo', remaining_todos)

def archive_todo(text):
    'archive a line of text'
    todos = get_cached_file_lines('archive')
    todos.append(text)
    write_named_file_lines('archive', todos)

def add_todo(args):
    'add a todo to the text file'
    todos = get_cached_file_lines('todo')
    new_id = generate_id(args.text)
    todos.append('%s: %s' % (new_id, args.text))
    print 'adding todo: %s (id %s)' % (args.text, new_id)
    write_named_file_lines('todo', todos)

# }}}
# search methods
# {{{

def search_todos(args):
    'search todos on a single matched string'
    todos = get_cached_file_lines('todo')
    for todo in todos:
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
        deps_satisfied = dependencies_satisfied(todo) \
            if args.all else True

        if all([
            has_text, has_tags, has_project, lacks_tags,
            lacks_project, deps_satisfied
            ]):
            if args.verbosity == 2:
                print format_verbose_line(args, todo)
            elif args.verbosity == 1:
                print format_succinct_line(args, todo)

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
        >>> extract_text('asdf: Eat some fudge +fudgeeating @yummy')
        'Eat some fudge'

    Make sure that emails are not excluded.
        >>> extract_text('asdf: Email test@example.org +bigproject @email')
        'Email test@example.org'

    Return the same string even if no id.
        >>> extract_text('Eat some fudge +fudgeeating @yummy')
        'Eat some fudge'

    Don't exclude plusses inside the text.
        >>> extract_text('asdf: Talk to Jim+John +bigproject @inperson')
        'Talk to Jim+John'

    Even if there are spaces between them.
        >>> extract_text('asdf: Talk to Jim + John +bigproject @inperson')
        'Talk to Jim + John'

    Don't include dependencies either (but allow spaces in symbol)
        >>> extract_text('asdf: Talk to Jim ^qwer,tyui')
        'Talk to Jim'
        >>> extract_text('asdf: Find pi^2 ^qwer,tyui')
        'Find pi^2'
    '''
    # remove project
    text = text.replace(PROJECT_CHAR + extract_project(text), '')

    # remove dependencies
    dependencies = DEPENDENCY_CHAR + ','.join(extract_dependencies(text))
    text = text.replace(dependencies, '')

    # remove tags
    for tag in extract_tags(text):
        text = text.replace(TAG_CHAR + tag, '')

    # remove id
    text = text.replace('%s: ' % extract_id(text, generate=False), '')

    return text.strip()

def extract_dependencies(text):
    '''
    extract dependencies (as a list) from a todo

    >>> extract_dependencies('asdf: Eat some fudge +project @tag ^aaaa,bbbb')
    ['aaaa', 'bbbb']

    >>> extract_dependencies('asdf: Eat some fudge +project @tag ^aaaa')
    ['aaaa']

    >>> extract_dependencies('asdf: Eat some fudge +project @tag')
    []
    '''
    match = re.search(r'(?<=\s\%s)[\w,]+' % DEPENDENCY_CHAR, text)
    if match is None:
        return []
    else:
        return text[match.start():match.end()].split(',')

def extract_id(text, generate=True):
    '''
    find the id from a task, generating if not found

    >>> extract_id('asdf: do a thing +project @tag')
    'asdf'

    If the id is missing, it is generated, not sliced
    >>> len(extract_id('do a thing +project @tag'))
    4
    >>> extract_id('do a thing +project @tag') != 'do a'
    True

    If the id is missing, and generate is false, don't generate
    >>> extract_id('do a thing +project @tag', generate=False)
    ''
    '''
    match = re.match(r'\w{4}(?=:\s)', text)
    if match is not None:
        return text[0:match.end()]
    else:
        if generate:
            return generate_id(text)
        else:
            return ''

def generate_id(text):
    '''
    generate a unique identifier from a bit of text

    four letter id from any input
    >>> len(generate_id(''))
    4
    >>> len(generate_id('a'))
    4

    unique for task text
    >>> gen_id = generate_id('Eat some fudge +fudgeeating @yummy')
    >>> generate_id('Eat some fudge +fudgeconsuming @delicious') == gen_id
    True
    '''
    random.seed(extract_text(text))
    alpha = 'aaaaabceeeeghiiiijklmnoooopqrstuuuuvwxyz'
    return ''.join([random.choice(alpha) for _ in range(4)])

def dependencies_satisfied(text):
    'whether all the todos dependencies are satisfied'
    dependencies = extract_dependencies(text)
    todos = get_cached_file_lines('todo')

    for todo in todos:
        if extract_id(todo) in dependencies:
            return False

    return True

# }}}
# formatting
# {{{

def format_succinct_line(args, text):
    'fromat a line of text in a succinct format'
    return '%s: %s' % (
        wrap_color(args, extract_id(text), 'blue'), 
        extract_text(text)
    )

def format_verbose_line(args, text):
    'format a line of text in a verbose format'
    todo_text = extract_text(text)
    tags = ' '.join(['%s%s' % (TAG_CHAR, t) for t in extract_tags(text)]) + ' '\
        if len(extract_tags(text)) > 0 else ''
    dependencies = DEPENDENCY_CHAR + ','.join(extract_dependencies(text)) \
        if len(extract_dependencies(text)) > 0 else ''
    project = PROJECT_CHAR + extract_project(text) + ' ' \
        if len(extract_project(text)) > 0 else ''

    return '%s: %s %s%s%s' % (
        wrap_color(args, extract_id(text), 'blue'), 
        todo_text,
        wrap_color(args, project, 'yellow'),
        wrap_color(args, tags, 'green'),
        wrap_color(args, dependencies, 'red'),
    )

COLORS = {
    'gray': '\033[1;30m',
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
        '-v', '--verbosity',
        type=int, choices=[1, 2], default=2,
        help='show verbose output'
    )
    parser.add_argument(
        '--version',
        action='version', version='%(prog)s 1.2'
    )

    subparsers = parser.add_subparsers()

    # add
    add_parser = subparsers.add_parser('add', help='add a new task')
    add_parser.add_argument('text', help='the text of your task')
    add_parser.set_defaults(func=add_todo)

    # complete
    complete_parser = subparsers.add_parser('complete', help='complete a task')
    complete_parser.add_argument(
        'ids', type=comma_separated_string,
        help='The task id(s) to mark as completed'
    )
    complete_parser.set_defaults(func=complete_todo)

    # show
    show_parser = subparsers.add_parser('show', help='show or find tasks')
    show_parser.add_argument(
        'text', help='the text of your search',
        nargs='?'
    )
    show_parser.add_argument(
        '-p', '--project',
        help='name of a project'
    )
    show_parser.add_argument(
        '-t', '--tags',
        type=comma_separated_string,
        help='name(s) of tag(s) (comma separated)'
    )
    show_parser.add_argument(
        '--not-project',
        type=comma_separated_string,
        help='name(s) of project(s) to exclude (comma separated)'
    )
    show_parser.add_argument(
        '--not-tags',
        type=comma_separated_string,
        help='name(s) of tag(s) to exclude (comma separated)'
    )
    show_parser.add_argument(
        '-a', '--all',
        action='store_false',
        help='show all tasks (with unmet dependencies)'
    )
    show_parser.set_defaults(func=search_todos)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run()

# }}}
