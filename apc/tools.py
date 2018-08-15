#!/usr/bin/python

import os
import datetime

def log(string, write=True):
	string = '[{0}] {1}\n'.format(datetime.datetime.now(), string)
	if write:
		if os.path.isfile('crawler.log'):
			with open('crawler.log', 'a') as l:
				l.write(string)
				l.close()
		else:
			with open('crawler.log', 'w') as l:
				l.write(string)
				l.close()

def clear_output(output_dir='output/'):
	for page in os.listdir(output_dir):
		if os.path.isfile(output_dir+page):
			os.remove(output_dir+page)
	
	for image in os.listdir('{}/images'.format(output_dir)):
		os.remove(output_dir + '/images/' + image)
	log('Output cleared', write=True)
	