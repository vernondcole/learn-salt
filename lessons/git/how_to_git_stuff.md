# How to GIT Stuff

GIT is a distributed version control system (dvcs).

It is one of three popular free dvcs packages, is the most popular,
and is the most difficult to use. For more information see 
[the Wikepedia](https://en.wikipedia.org/wiki/Git) or
[the official web site](https://git-scm.com/).

Windows versions can be downloaded from
[the official site](https://git-scm.com/downloads).

Ubuntu Linux is often shipped with git already installed.  If not,
just type:

    sudo apt install git
    
MacOS ships with a version of git pre-installed.

## GitHub

GitHub is a popular web site used for storing repositories of software
which are maintained using `git`.  It is free to use for open source
projects. Other web sites (such as [BitBucket](https://bitbucket.org/))
also use `git`.  

Open source projects can be freely downloaded from GitHub using `http:`,
but in order to freely send updates _to_ GitHub, or to use `scp:` protocol,
you will need to register for a free user account, and upload an ssh private
key to it. Instructions for this are clearly available on the site.

## git Quickstart

- clone: the initial download of a project repository is done using the
`git clone` command, which will create a copy of the source repository in
a new sub-directory at the location where you type the `clone` command.  All other 
`git` commands are typed from within that sub-directory.

- pull: you get updates of an upstream repository using the `git pull` command. 

- add: you must mark any changed files which should be commited to the repository
using the `git add` command.  You must `add` a changed file, even though it already
exists in the repository. This is not intuitive.

- commit: actually adds the files which you have mentioned in `add` commands
to the repository.  Commits must always have a comment, so the simplest command
is `git commit -m "this is my comment"`.

- push: send all committed changes to the upstream repository.

- branch: make a new name for versions of software in your repository.

- merge: combine work from one branch into another branch.

- rebase: like merge, only more complicated, but sometimes necessary.

### Another Way

If you use a good Integrated Development Environment 
(like [PyCharm](https://www.jetbrains.com/pycharm/))
it will handle the git commands for you.
