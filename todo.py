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

def wrap_color(text, *args):
    for arg in args:
        try:
            text = COLORS[arg] + text + COLORS['end']
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

def format_verbose_line(i, text):
    return '%s: %s' % (wrap_color(str(i), 'blue'), text)

def print_todos():
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        print format_verbose_line(i, todo)

def complete_todo(n):
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        try:
            if i == int(n):
                archive_todo(todos[i])
                del todos[i]
        except ValueError:
            print 'n must be an integer'

    write_named_file_lines('todo', todos)

def archive_todo(text):
    todos = get_named_file_lines('archive')
    todos.append(text)
    write_named_file_lines('archive', todos)

def add_todo(text):
    todos = get_named_file_lines('todo')
    todos.append(text)
    write_named_file_lines('todo', todos)

def search_todo(text):
    todos = get_named_file_lines('todo')
    for i, todo in enumerate(todos):
        if todo.find(text) != -1:
            print format_verbose_line(i, todo)

def refresh_projects():
    print 'not fully functional.'
    todos = get_named_file_lines('todo')
    projects = {}
    for todo in todos:
        print todo

## ARGUMENT PARSING ##

def parse(args):
    if args.command in ['show', 's']:
        print_todos()
    elif args.command in ['complete', 'c']:
        complete_todo(args.m)
    elif args.command in ['add', 'a']:
        add_todo(args.m)
    elif args.command in ['search', 'e']:
        search_todo(args.m)
    elif args.command in ['projects', 'p']:
        refresh_projects()

parser = argparse.ArgumentParser(description='Manage todos.')
parser.add_argument(
    'command', metavar='cmd', type=str, 
    help='one of s[how], c[omplete], a[dd], s[earch], p[rojects]',
    choices=['show', 's', 'complete', 'c', 'add', 'a', 'search', 'e', 'projects', 'p']
)
parser.add_argument('-m', metavar='text', type=str, default='', help='text of your command. (for complete, must be an integer)')

args = parser.parse_args()
parse(args)
