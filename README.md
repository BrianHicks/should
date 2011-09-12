Should
======

This is a python program to manage todos from the command line. It'll
create all the files it needs as it needs them.

Data format
-----------

Data is stored as plain text, in the same directory as should.py. An
archive file will also be filled with old todos.

 - `@`: tags
 - `+`: project
 - `^`: dependencies

Usage
-----

To add a task to the list:

    $ should.py add "program ALL the things +bigproject @work"
    adding todo: program ALL the things +bigproject @work (id ibeu)

What was it I added earlier?

    $ should.py show
    ibeu: program ALL the things +bigproject @work
    aebb: eat a sandwich @food

Right, but what if I want to see only the bigproject tasks?

    $ should.py show -p bigproject
    ibeu: program ALL the things +bigproject @work

Or all the things related to food?

    $ should.py show -t food
    aebb: eat a sandwich @food

Or just all the things relating to sandwiches?

    $ should.py show sandwich
    aebb: eat a sandwich @food

Om nom nom, and you're done. Now mark it as complete:

    $ should complete aebb
    completed: aebb: eat a sandwich @food

You can see further help with `should.py -h` or `should.py [cmd] -h`.

Ideas
-----

Here's some ideas from my list about should:

 - projects!
 - due date and search
 - non-verbose printing format
 - public list / private list in different text files (for example, this
   list of ideas would be public)
 - ability to edit / add tags, projects, due dates from the command line
   interface

Here's the ones I've done:

 - color
 - better command line interface
 - better search (by tags AND/OR projects plus exclusion)
 - dependency management / parenting
