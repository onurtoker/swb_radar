# swb_radar
Synthetic Wide-Band Radar using USRPs

Pure Python implementation: 

myConstants.py has constant paramater values
myUSRP.py has low-level UHD calls and provides a layer of abstraction
usrp_radar.py has is the main program

GNU radio + Octave implementation:

swb_radar.grc is the GNU radio graph
swb_radar.m is the Octave script

Other details:

For XMLRPC within Octave, py_xmlrpc.py script is used

Make sure that liboctave-dev is installed, and zeromq package is enabled in Octave
(Type "pkg install -forge zeromq" in Octave)




