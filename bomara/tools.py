#!/usr/bin/python

import os
import datetime
import bomara.crawler

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

    if os.path.isdir('{}/images'.format(output_dir)): 
        for image in os.listdir('{}/images'.format(output_dir)):
            os.remove(output_dir + '/images/' + image)

    log('Output cleared', write=True)

def process_family_links(vendor, part_list, family_name, family_description):
    part_numbers = []
    part_descriptions = []
    part_names = []
    if vendor == 'Vertiv':
        for link in part_list:
            scraper = bomara.crawler.VertivCrawler()
            scraper.connect(link)
            scraper.parse(family_member=(family_name, family_description))
            scraper.apply_template()

            part_numbers.append(scraper.page['Meta']['part_number'])
            part_descriptions.append(scraper.page['Meta']['includes'])
            part_names.append(scraper.page['Meta']['description'])
        return zip(part_numbers, part_descriptions, part_names)