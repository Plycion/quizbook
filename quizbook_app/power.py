import sys

def print_terminal(s):
	print >>sys.stderr, "\n>>> %s\n" % (s)