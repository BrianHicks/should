Do
==

This is a python program to manage todos from the command line. It'll
create all the files it needs as it needs them.

Data format
-----------

Data is stored as plain text, in the same directory as do.py. An
archive file will also be filled with old todos.

 - `@`: tags
 - `+`: project
 - `^`: dependencies
 - `:`: start date
 - `;`: due date

Usage
-----

To add a task to the list:

    $ do.py add "program ALL the things +bigproject @work"
    adding todo: program ALL the things +bigproject @work (id ibeu)

What was it I added earlier?

    $ do.py show
    ibeu: program ALL the things +bigproject @work
    aebb: eat a sandwich @food

Right, but what if I want to see only the bigproject tasks?

    $ do.py show -p bigproject
    ibeu: program ALL the things +bigproject @work

Or all the things related to food?

    $ do.py show -t food
    aebb: eat a sandwich @food

Or just all the things relating to sandwiches?

    $ do.py show sandwich
    aebb: eat a sandwich @food

Om nom nom, and you're done. Now mark it as complete:

    $ do complete aebb
    completed: aebb: eat a sandwich @food

You can see further help with `do.py -h` or `do.py [cmd] -h`.

Ideas
-----

Here's some ideas from my list about do:

 - projects!
 - due date and search
 - public list / private list in different text files (for example, this
   list of ideas would be public)

Here's the ones I've done:

 - color
 - better command line interface
 - better search (by tags AND/OR projects plus exclusion)
 - dependency management / parenting
 - non-verbose printing format
 - ability to edit / add tags, projects, due dates from the command line
   interface
