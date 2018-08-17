#!/usr/bin/python

import argparse

from apc.interface import run
from apc.crawler import VertivCrawler
from apc.tools import clear_output

# Load args ------------------------->

parser = argparse.ArgumentParser()
parser.add_argument('tool', nargs='?')
parser.add_argument('tool_args', nargs='?')

args = parser.parse_args()

if args.tool == 'clear':
	if args.tool_args != None:
		clear_output(output_dir=args.tool_args)
	else:
		# Assume default dir ('output/')
		clear_output()
	exit()

# ----------------------------------->

# Run GUI
if __name__ == '__main__':
	#run()
	vertiv = VertivCrawler()
	vertiv.connect(args.tool)
	vertiv.parse(write=True)
	vertiv.apply_template()
	