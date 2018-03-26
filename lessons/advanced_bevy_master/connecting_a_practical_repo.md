### Connecting Working Systems to your Bevy

The bevy master used for these lessons has some working examples,
but is capable of more than just running these.  

Originally, the ancestor of the Bevy Master you now see was
part of a proprietary working system at Sling T.V. 
The master was split apart from the proprietary parts, and expanded
to contain the various lessons.  
It was always intended that it would continue in its role
to operate an example of the company's back-end system.

This lessons show how it, or any other working system,
can be connected to your Bevy Master.  
For this lesson, we will connect a fictional [Black Knight](https://www.youtube.com/watch?v=dhRUe-gz690)
backend system.

##### The _Black Knight_ seems to be the Ruler.

The useful application is the item on a maintainer's mind
when she first starts investigating the entire system.
She has never heard of a "bevy" and is not interested (yet)
in learning new things. She wants just to do the maintenance needed and
get back to other work. 
Therefore, the `learn-salt` system is treated as a sub-system
of the Black Knight application.  It is loaded from and called by it.

By design, the `learn-salt` code sits side-by-side with an application system,
but could also be organized as a submodule. 
The application calls out to learn-salt's configuration system with
one or more additional file roots which contain the Salt States
and default pillar files to configure the application.

The [black_knight_master](black_knight_master/README.md) directory in this lesson
contains Linux and Windows scripts to call Vagrant from the BlackKnight
directory, and to join a bevy with `black_knight/local_salt` added as a Salt root.
It has a bash script to clone `learn-salt` next to BlackKnight.
It also has a skeleton for the Salt state and pillar scripts for installing BlackKnight.
The README file is a starting point for documentation.
