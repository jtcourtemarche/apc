#!/usr/bin/python

import os
import datetime
import bomara.crawler
import bomara.vendors 

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

def process_family_links(vendor, packages):
    if vendor == 'Vertiv':
        # Deprecated
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
    elif vendor == 'Servertech':
        for part in packages:
            scraper = bomara.vendors.servertech.family_crawler
            scraper.reset()
            scraper.page['Meta']['part_number'] = part['number']
            scraper.page['img_url'] = None
            scraper.page['img_type'] = None

            scraper.page['Meta']['description'] = part['description']

            scraper.page['Headers'].append('General Specifications')

            for spec in part['product_specs']:
                scraper.page['Techspecs'].append(spec)
                scraper.page['Headers'].append('*')

            scraper.apply(parse=False, dl_img=False)

