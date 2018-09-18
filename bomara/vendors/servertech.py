from bomara.crawler import Crawler
import urllib
import os
import subprocess
from pdf2image import convert_from_path
from bs4 import BeautifulSoup

def parse(self):
    # Get description & part number ---------------------------------->
    self.page['Meta']['description'] = self.soup.find('meta',
        attrs={'itemprop':'name'}).get('content').replace(' | Server Technology', '')

    breadcrumbs = self.soup.find('ul', class_='breadcrumb')
    self.page['Meta']['part_number'] = breadcrumbs.find_all('li')[-1].get_text()

    # Full description
    self.page['Meta']['includes'] = self.soup.find('div', id="panel1a").get_text()

    # Product image
    self.page['Meta']['img_url'] = self.soup.find_all('img',
        class_='lazyOwl')[0].get('data-src')

    self.page['Meta']['img_type'] = '.png'

    self.cleanup(['part_number'])

    # Get drawing 

    panel1d = self.soup.find('div', id='panel1d', class_='content')
    if panel1d != None and panel1d.find('a') != None:
        self.dl_img(
            url=panel1d.find('a').get('href'),
            img_type='.pdf',
            name=self.page['Meta']['part_number'] + '-drawing'
        )
        pdf = convert_from_path('output/images/{}-drawing.pdf'.format(self.page['Meta']['part_number']), last_page=1, output_folder='output/images/', fmt='jpg')

        os.remove('output/images/{}-drawing.pdf'.format(self.page['Meta']['part_number']))

        drawing = '<img href="images/{}" class="display-image-1_5"></img>'.format(pdf[0].fp.name.replace('output/images/', ''))

        self.page['Techspecs'].append(('Drawing', drawing))

    # Get tech specs

    specs = self.soup.find('div', id='panel1b', class_='content')
    for spec in specs.find_all('div', class_='column'):
        for item in spec.find_all('li'):
            if item.find('strong') == None:
                continue
            else:
                title = item.find('strong').get_text().replace(':', '')
                description = item.find('span').get_text()

                if title in self.ignored_headers:
                    continue

                self.page['Techspecs'].append((title, description))
                self.page['Headers'].append('*')

crawler = Crawler(
    # Vendor name
    vendor = 'Servertech',
    schema = {
        # Required
        'Meta': dict(),
        # Required
        'Techspecs': [],
        # Required
        'Headers': [],
    },
    # Ignored tech specs headers
    ignored_headers = ['PDU Platform'],
    # Mostly APC exclusive
    software_identifiers = [],

    links=['servertech.com/families/*'],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parse,
)