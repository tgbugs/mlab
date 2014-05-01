mlab
repo holding code for an ephys rig and a database for scientific data

this repo should NOT be synced to github until I work out the licensing stuff

use the dropbox setup


Do these things
Measure these things
In this order
And if you do
You will find
What I found.

Dependencies
------------

>= python 3.X (may run on 2.7.X but untested and may have hidden gotchas)
>= sqlalchemy-0.8
psycopg2
docopt
numpy
scipy
matplotlib
ipython
python-neo
pyserial
requests
*tom's personal utils (debug, tgplot) >_< bettered fix that*
rpdb2 (debug)

Configuration
-------------

In rig/clx.py and rig/mcc.py make sure to set the correct paths to the Axon DLL files.
Better yet, get those locations from the config file!
