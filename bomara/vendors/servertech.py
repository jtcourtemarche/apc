from bomara.crawler import Crawler
import urllib
import os
import subprocess
import bomara.utils
from pdf2image import convert_from_path
from bs4 import BeautifulSoup

def parse(self):
    # Get description & part number ---------------------------------->
    self.page['Meta']['description'] = self.soup.find('meta',
        attrs={'itemprop':'name'}).get('content').replace(' | Server Technology', '')

    breadcrumbs = self.soup.find('ul', class_='breadcrumb')
    self.page['Meta']['part_number'] = breadcrumbs.find_all('li')[-1].get_text().replace('  ', '')

    # Full description
    self.page['Meta']['includes'] = self.soup.find('div', id="panel1a").get_text()

    # Product image

    try:
        self.page['Meta']['img_url'] = self.soup.find_all('img',
            class_='lazyOwl')[0].get('data-src')
    except:
        self.page['Meta']['img_url'] = None

    self.page['Meta']['img_type'] = '.png'

    self.cleanup(['Meta/part_number'])

    # Get family (each part generates a new file that is crawled)
    self.page['Headers'].append('Family Products')

    panel1b = self.soup.find('div', id='panel1b', class_='content')
    panel1c = self.soup.find('div', id='panel1c', class_='content')
    panel1d = self.soup.find('div', id='panel1d', class_='content')

    packages = []
    for product in panel1c.find_all(class_='column'):
        header = product.find('thead')    
        title = header.find('th', class_='m-title').get_text()

        part_num = title.split('(')[0].replace(' ', '').replace('\n', '').replace(u'\u2605', '')
        part_description = str(title.split(')')[1].replace('  ', '').replace('\n', '').replace(u'\u2605', ''))

        self.page['Techspecs'].append((f'<a href="{part_num}.htm">{part_num}</a>', part_description))

        product_pkg = {
            'number': part_num,
            'family': self.page['Meta']['part_number'],
            'description': part_description,
            'product_specs': []
        }

        body = product.find('tbody')
        for spec in body.find_all('tr'):
            tds = spec.find_all('td')
            spec_title = tds[0].get_text()
            spec_description = tds[1].get_text()

            product_pkg['product_specs'].append((spec_title.replace(':', ''), spec_description))

        packages.append(product_pkg)

    bomara.utils.process_family_links('Servertech', packages, breadcrumbs=self.breadcrumbs)

    # Family Specs
    self.page['Headers'].append('Family Specifications')

    # Get drawing 
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

    for spec in panel1b.find_all('div', class_='column'):
        for item in spec.find_all('li'):
            if item.find('strong') == None:
                continue
            else:
                title = item.find('strong').get_text().replace(':', '')
                description = item.find('span').get_text()

                if title in self.ignored_headers:
                    continue

                if description == '':
                    continue

                self.page['Techspecs'].append((title, description))
                self.page['Headers'].append('*')

# Main crawler
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

# Crawler that will be reset by process_family_links
family_crawler = Crawler(
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
    links=[],
    parser = None,
)