#!/usr/bin/python

import os
import datetime
import bomara.crawler

def clear_output():
    if os.path.isdir('output/'):
        for page in os.listdir('output/'):
            if os.path.isfile('output/'+page):
                os.remove('output/'+page)

        if os.path.isdir('output/images'): 
            for image in os.listdir('output/images'):
                os.remove('output/images/' + image)
        else:
            os.makedirs('output/images/')
    else:
        os.makedirs('output/')

def process_family_links(vendor, part_list, family_name, family_description):
    # Specific to Vertiv crawler
    part_numbers = []
    part_descriptions = []
    part_names = []
    if vendor == 'Vertiv':
        scraper = bomara.vendors.vertiv.crawler()
        for link in part_list:
            scraper.reset()
            scraper.connect(link)
            scraper.parse(family_member=(family_name, family_description))
            scraper.apply_template()

            part_numbers.append(scraper.page['Meta']['part_number'])
            part_descriptions.append(scraper.page['Meta']['includes'])
            part_names.append(scraper.page['Meta']['description'])
        return list(zip(part_numbers, part_descriptions, part_names))