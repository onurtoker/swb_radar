import xmlrpc.client
import argparse

# Create the parser
my_parser = argparse.ArgumentParser(description='Command to set LO frequency')

# Add the arguments
my_parser.add_argument('lo_freq',
                       metavar='LO freq',
                       type=float,
                       help='LO freq in Hz')

# Execute the parse_args() method
args = my_parser.parse_args()

desired_lo_freq = args.lo_freq

#print(desired_lo_freq)

s = xmlrpc.client.ServerProxy('http://localhost:8080')
s.set_freq(desired_lo_freq)
