mlab
repo holding code for an ephys rig and a database for scientific data

this repo should NOT be synced to github until I work out the licensing stuff

use the dropbox setup


Do these things \n
Measure these things \n
In this order \n
And if you do \n
You will find \n
What I found.

Dependencies
------------

>= python 3.X (may run on 2.7.X but untested and may have hidden gotchas) \n
>= sqlalchemy-0.8 \n
psycopg2 \n
docopt \n
numpy \n
scipy \n
matplotlib \n
ipython \n
python-neo \n
pyserial \n
requests \n
*tom's personal utils (debug, tgplot) >_< bettered fix that* \n
rpdb2 (debug) \n

Configuration
-------------

In rig/clx.py and rig/mcc.py make sure to set the correct paths to the Axon DLL files.
Better yet, get those locations from the config file!
