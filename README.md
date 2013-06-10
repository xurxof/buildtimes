buildtimes.py is a python script for calculate some statistic data on build times in Visual Studio.

= Requirements =
 
This code has been run on Python 2.6.6

= External Deps  =
 
* matplotlib 0.99.3-1 (current in my Debian repo ) (http://matplotlib.org/downloads.html)

* The data about build time can be collected with BuildMonitor (https://github.com/vinntreus/BuildMonitor), an add-on for Visual Studio.
 
= Tests =
 
This was my first approach to the actual use of python, so no test code available.

= Use ==

You must execute the program  in two steps. First time is for parse, aggregate and save the data. 

    python buildtimes.py buildtimes_big.json
    
Depending on the file size and your computer, it may take two or three minutes. I test it with a 40 Mb file in a Intel Core2 Quad CPU @ 2.40GHz and take 1:30 min.

The first step create a file_name.pkl in same directory. The second step show the info:

    python buildtimes.py buildtimes_big.pkl
    
It will print some stats, and show a graph for per-day-of-week time consume.
   
= License =
 
You can use this (messy) code as you wish, without restrictions of any kind.

= Support =
 
No support available. The code is provided as is, with no warranty.
