# swb_radar
Synthetic Wide-Band Radar using USRPs

Pure Python implementation: 
===========================

myConstants.py has constant paramater values,
myUSRP.py has low-level UHD calls and provides a layer of abstraction, and
usrp_radar.py is the main program.

GNU radio + Octave implementation:
==================================

swb_radar.grc is the GNU radio graph, and
swb_radar.m is the main Octave script.

Other details:
==============

For XMLRPC within Octave, py_xmlrpc.py script is used.

Make sure that liboctave-dev is installed (Type "sudo  apt install liboctave-dev" in terminal window), and zeromq package is enabled in Octave
(Type "pkg install -forge zeromq" in Octave)




