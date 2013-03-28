Teeawards
=========

I made a small tool/server manager called TeeAwards
I made it to play teeworlds during the diner at job 
The first goal was to show player stats of my LAN server...
This tools get server logs and create stats, ranks achievements
I also add server and maps management !

Tested on ubuntu and Debian

You can get it here : https://github.com/titilambert/teeawards

Installation
------------

You need python-pymongo, mongodb and teeworlds-server

`sudo apt-get install python-pymongo mongodb teeworlds-server`

How to install:

`cd myfolder

git clone https://github.com/titilambert/teeawards.git

cd teeawards`

Then start it :

`python teeawards.py`

Then go on it: http://127.0.0.1:8081

Upload maps: http://127.0.0.1:8081/admin

Create configs: http://127.0.0.1:8081/admin

PLAY !!!!!

Launch your clients !

Go see your stats !
http://127.0.0.1:8081

TODOs
-----

 -  Add fedora and others distributions more compatible
 -  Add authentification for admin page
 -  Finish to convert achievements
 -  Find a better formula to get score
 -  Add "mode filter" in stats views
 -  Add sample config and maps
 -  Add more achievements
 -  Any idea ???
 -  Reset stats button ??

BIG THANKS
----------
 -  ALL FANS WHO MADE ART on the forum !!!!
 -  My colleagues

LINKS
-----
 -  Teeworlds thread: https://www.teeworlds.com/forum/viewtopic.php?pid=105386#p105386
