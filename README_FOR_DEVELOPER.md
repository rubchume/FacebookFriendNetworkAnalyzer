# What is this?

This is a project template for basic Python projects.
It includes basic libraries and a noxfile script for testing, lynting, and typing.


# What should I do?

There is a script called `start_project.sh`.

Execute it writing
```bash
$ start_project.sh
```
in Windows.

or writing
```bash
./start_project.sh
```
in Linux.

It will install the package manager library called Poetry, and install some basic packages for the developing tasks I have described.

It will also delete any `.git` folder if it exists, and initialize a new Git repository, add all files not included in `.gitignore` (the file is already filled), and finall commit them as the initial commit. 

Finally will delete itself (`start_project.sh`) and this file (`README_FOR_DEVELOPERS.md`).
