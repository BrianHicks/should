'Should, a small command line app for working with plain text todo files'
import argparse
import os
import re
import sys
from datetime import datetime

## COLORS ##

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
    'end': '\033[1;m',
}

def wrap_color(args, text, *colors):
    if args.color == 'n':
        return text

    for color in colors:
        try:
            text = COLORS[color] + text + COLORS['end']
        except KeyError:
            pass

    return text

## METHODS ##

def get_absolute_file_name(name):
    return os.path.join(os.path.dirname(__file__), '%s.txt' % name)

def get_named_file_lines(name):
    'get the lines from a named file (assuming .txt extension)'
    try:
        with open(get_absolute_file_name(name), 'rb') as f:
            return [l for l in f.read().split('\n') if l != '']
    except IOError:
        return []

def write_named_file_lines(name, lines):
    'write lines from a list to a file'
    try:
        with open(get_absolute_file_name(name), 'wb') as f:
            for line in lines:
                f.write('%s\n' % line)
    except IOError:
        print 'could not write lines to file, here they are:'
        print lines

def format_verbose_line(args, i, text):
    return '%s: %s' % (wrap_color(args, str(i), 'blue'), text)

def print_todos(args):
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        print format_verbose_line(args, i, todo)

def complete_todo(args):
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        if i == int(args.n):
            archive_todo(todos[i])
            del todos[i]

    write_named_file_lines('todo', todos)

def archive_todo(text):
    todos = get_named_file_lines('archive')
    todos.append(text)
    write_named_file_lines('archive', todos)

def add_todo(args):
    todos = get_named_file_lines('todo')
    todos.append(args.text)
    print 'adding todo',args.text
    write_named_file_lines('todo', todos)

def search_todos(args):
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        if todo.find(args.text) != -1:
            print format_verbose_line(args, i, todo)

def refresh_projects():
    print 'not fully functional.'
    todos = get_named_file_lines('todo')
    projects = {}
    for todo in todos:
        print todo

## EXECUTION ##

if __name__ == '__main__':
    'parse args to run functions'
    # global options
    parser = argparse.ArgumentParser(description='Manage text-based task list from the command line.')
    parser.add_argument('-c', '--color', default='y', choices=['y', 'n'], help="Colorized Output")

    subparsers = parser.add_subparsers()

    # show
    show_parser = subparsers.add_parser('show', help='show your list of tasks')
    show_parser.set_defaults(func=print_todos)

    # add
    add_parser = subparsers.add_parser('add', help='add a new task')
    add_parser.add_argument('text', help='The text of your task')
    add_parser.set_defaults(func=add_todo)

    # complete
    complete_parser = subparsers.add_parser('complete', help='complete a task')
    complete_parser.add_argument('n', type=int, help='The task number to mark as completed')
    complete_parser.set_defaults(func=complete_todo)

    # search
    search_parser = subparsers.add_parser('search', help='search for a task')
    search_parser.add_argument('text', help='The text of your search')
    search_parser.set_defaults(func=search_todos)

    # projects
    projects_parser = subparsers.add_parser('projects', help='view a list of projects, or modify them.')
    projects_parser.set_defaults(func=refresh_projects)

    args = parser.parse_args()
    args.func(args)
