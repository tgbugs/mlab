mlab
====
repo holding code for an ephys rig and a database for scientific data

	Do these things
	Measure these things
	In this order
	And if you do
	You will find
	What I found.

About
-----
This repository has been opened, as-is, in hopes that someone might find
some of the ideas explored here useful. This project was not finished and
many comments reflect this. This was also my first large python project and
there are significant issues with complexity management. Documentation is
spotty and much of the code was written for python 3 running on windows XP
with specific assumptions about other pieces of software and hardware being
connected to the computer, no abstraction layer was implemented so the code
probably wont run.

Overview
--------
This repository has 3 parts, the database, the rig, and analysis.
 - **analysis** not particularly interesting since it holds
scripts for analysing specific data which is not publically accessible.
 - **rig** contains considerable, if scattered, effort to build an
integrated interface for controlling an electrophysiology rig and collecting
data and metadata about experiments. The most useful code here provides a python
interface for Clampex and MultiClampCommander and has already been made publically
available via [inferno](https://github.com/tgbugs/inferno).
 - **database** contains an SQLAlchemy specification for a database for
storing experimental data and metadata. It also contains an attempt to create
a abstraction for specifying and running protocols on an electrophysiology rig,
including everything from the breeding of mice all the way through tracking the
serial number of the headstage a specific datafile was collected on.

Dependencies
------------

* \>= python 3.X (may run on 2.7.X but untested and may have hidden gotchas)
* \>= sqlalchemy-0.8
* psycopg2
* docopt
* numpy
* scipy
* matplotlib
* ipython
* python-neo
* pyserial
* requests
* rpdb2 (debug)
* *tom's personal utils (debug, tgplot) >_< bettered fix that*

Configuration
-------------

Oh man, don't even get started on this one.

