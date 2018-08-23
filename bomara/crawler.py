#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import os
import bomara.tools
from jinja2 import Template, Environment, PackageLoader, select_autoescape
from bs4 import BeautifulSoup

#
# Crawler()
# --------------------------------------------------------
# See example below
#
# Crawler().connect()
# --------------------------------------------------------
# Required: link to APC page
#
# Crawler().apply()
# --------------------------------------------------------
# Optional: output_dir
# output_dir => directory to generate files to
#

""" Example
crawler = Crawler(
    # Vendor name
    vendor = 'APC',
    schema = {
        # Required
        'Meta': dict(),
        # Required
        'Techspecs': [],
        # Required
        'Headers': [],
        # Optional
        'Options': {
            'Accessories': [],
            'Services': [], 
            'Software': []
        }
    },
    # Ignored tech specs headers
    ignored_headers = ['Extended Run Options', 'PEP', 'EOLI'],
    # Mostly APC exclusive
    software_identifiers = ['software', 'struxureware'],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parser(),
)
"""

class Crawler:
    def __init__(
        self, vendor, schema, parser, parser_args=[], ignored_headers=[], software_identifiers=[]):

        # Initializers
        self.vendor = vendor
        self.schema = schema
        self.i_parser = parser
        self.i_parser_args = parser_args
        self.i_ignored_headers = ignored_headers
        self.i_software_identifiers = software_identifiers

        # Constants
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        # Not currently supported
        self.breadcrumbs = [('Symmetra Family', 'symmetra-family.htm'), ('Symmetra RM', 'symmetra-rm.htm')]

        self.reset()

    def reset(self):
        self.page = self.schema
        self.page['Headers'] = []
        self.page['Techspecs'] = []
        self.page['Meta'] = dict()

        self.parser_warning = None
        self.page['Meta']['vendor'] = self.vendor

        self.ignored_headers = self.i_ignored_headers
        self.software_identifiers = self.i_software_identifiers

        self.parse = self.i_parser
        self.soup = None

    def connect(self, url):
        # Connect
        try:
            request = urllib2.Request(url, None, {
                'User-Agent': self.user_agent
            })
            data = urllib2.urlopen(request)
        except urllib2.URLError:
            raise ValueError("Not a valid url!")

        if (data.getcode() != 200):
            raise ValueError('Error: {0!s}'.format(data.getcode()))

        html = data.read()
        self.soup = BeautifulSoup(html, 'html.parser')   

    def apply(self, output_dir='output/', template='base.html', write=False):
        try:
            self.parse(self)
        except Exception as e:
            raise ValueError('Failed to parse: {}'.format(e))

        # Write provides a JSON data sheet
        if write:
            output = json.dumps(self.page, sort_keys=True, indent=4)
            with open(output_dir+'output.json', 'w') as f:
                bomara.tools.log('Writing {} to output.json'.format(
                    self.page['Meta']['part_number']))
                f.write(output)
                f.close()

        # Download part image 
        try:
            request = urllib2.Request(self.page['Meta']['img_url'], None, {
                'User-Agent': self.user_agent
            })
            data = urllib2.urlopen(request)

            # Create image directory if it doesn't exist already
            if not os.path.exists('{0}images'.format(output_dir)):
                os.makedirs('{0}images'.format(output_dir))

            with open('{0}images/{1}{2}'.format(output_dir, self.page['Meta']['part_number'], self.page['Meta']['img_type']), 'wb') as img_f:
                img_f.write(data.read())
                img_f.close()
        except urllib2.URLError:
            raise ValueError("Error loading image URL")
        except Exception as e:
            raise ValueError("Image file download failed: {0!s}".format(e))

        # Breadcrumbs 
        if not self.breadcrumbs:
            self.page['Meta']['breadcrumbs'] = ''
        else:
            breadcrumbs = map(
                lambda x: u"<a href='{0}'>{1}</a> » ".format(x[1], x[0]), self.breadcrumbs)
            self.page['Meta']['breadcrumbs'] = ''.join(breadcrumbs)

        self.env = Environment(
            loader=PackageLoader('bomara', '../templates'),
            autoescape=True
        )

        # Checks if options needs to be passed as False
        if not self.page['Options']:
            self.page['Options'] = False

        with open('{0}{1}.htm'.format(output_dir, self.page['Meta']['part_number']), 'w') as t:
            template = self.env.get_template(template)
            template = template.render(
                meta=self.page['Meta'],
                techspecs=zip(self.page['Techspecs'], self.page['Headers']),
                options=self.page['Options']
            ).encode('utf-8')
            t.write(template)
            t.close()

        bomara.tools.log('Created: '+self.page['Meta']['part_number'])
        return self.page['Meta']['part_number']

"""    
class VertivCrawler:
    # Reads url passed into class, parses data sheet as json,
    # and applies that data, among other things, to a jinja2 template
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.page = {
            'Meta': dict(),
            'Techspecs': [],
            'Headers': [],
            'BF': {
                'Benefits': [],
                'Features': []
            }
        }

        self.parser_warning = None
        self.page['Meta']['vendor'] = 'Vertiv / Avocent'
        self.template_dir = template_dir
        self.techspecs_title_filters = []

    def connect(self, url):
        # CONNECT ----------------------------------------------->
        try:
            self.request = urllib2.Request(url, None, {
                'User-Agent': self.user_agent
            })
            self.data = urllib2.urlopen(self.request)
        except urllib2.URLError:
            raise ValueError("Not a valid url!")

        if (self.data.getcode() != 200):
            raise ValueError('Error: {0!s}'.format(self.data.getcode()))
        #  ------------------------------------------------------>

        html = self.data.read()
        self.soup = BeautifulSoup(html, 'html.parser')

        self.page['Meta']['includes'] = self.soup.find(
            'p', class_='product-hero-description').get_text()
        self.page['Meta']['description'] = self.soup.find(
            'h1', class_='productnamedata').get_text()

        part_number = self.soup.find(
            class_='productnamedata').get_text().split(' ')

        pnfilters = ['Serial', 'Secure', 'Advanced', 'Management', 'Digital', 'Basic']
        if filter(lambda x: x == part_number[2], pnfilters):
            self.page['Meta']['part_number'] = part_number[1] 
        else:
            self.page['Meta']['part_number'] = (part_number[1] + part_number[2]).replace('"', '')

    def parse_techspecs(self, page_div):
        page_div = page_div.parent

        for header in page_div.find_all('div', class_='data-list-holder'):
            cheader = header.find(
                'dl', class_='scrollable-list-heading').get_text()
            if self.page['Headers']:
                self.page['Headers'][len(self.page['Headers'])-1] = cheader
            else:
                self.page['Headers'].append(cheader)

            for contents in header.find_all('dl', class_='scrollable-list-body'):
                title = contents.find('dt').get_text()
                description = contents.find('dd').get_text()
                # Checks title filters
                if filter(lambda x: x in title, self.techspecs_title_filters):
                    continue

                self.page['Techspecs'].append((title, description))
                self.page['Headers'].append('*')

    def parse(self, write=False, family_member=None):
        # Check if valid product page ----------------------------------->
        if self.soup.find('span', class_='subtitle').get_text() == 'Product Family':
            family_links = []
            for link in self.soup.find_all('a', class_='same-height-target'):
                family_links.append("http://www.vertivco.com" + link.get('href'))
            
            family_data = bomara.tools.process_family_links('Vertiv', family_links, self.page['Meta']['part_number'], self.page['Meta']['description'])

            self.page['Meta']['breadcrumbs'] = self.page['Meta']['description'].replace('Avocent', '').replace('Vertiv', '')
            self.page['Meta']['family'] = family_data
        else:
            # Parse tech specs ------------------------------------------>
            try:
                page_div = self.soup.find_all('div', class_='prod-title')[0]
                page_div = page_div.parent
                self.parse_techspecs(page_div)
            except:
                # No tech specs available
                self.parser_warning = "This page doesn't have any tech specs"
        
        # Parse benefits & features ------------------------------------->
        benefits_features = self.soup.find('div', id='benefits-features')
        for pc in enumerate(benefits_features.find_all('div', class_='presentation-content')):
            if pc[0] == 0:
                htype = 'Benefits'
            elif pc[0] == 1:
                htype = 'Features'

            for c in pc[1].find_all('div', title='BM SideBar Bullet'):
                self.page['BF'][htype].append(c.get_text())

        # Parse family breadcrumbs -------------------------------------->
        if family_member:
            self.page['Meta']['breadcrumbs'] = "<a href='{0}.htm'>{1}</a>".format(
                family_member[0], family_member[1].replace('Avocent', '').replace('Vertiv', ''))

        # Get image ---------------------------------------------------->
        try:
            image_holder = self.soup.find('div', class_='main-image-holder')
            self.page['Meta']['image'] = 'http://www.vertivco.com' + \
                image_holder.find('img').get('data-src')
            self.page['Meta']['img_type'] = '.png'
        except:
            self.page['Meta']['image'] = None

        if write:
            output = json.dumps(self.page, sort_keys=True, indent=4)
            with open('output.json', 'w') as f:
                bomara.tools.log('Writing {} to output.json'.format(
                    self.page['Meta']['part_number']))
                f.write(output)
                f.close()

    def apply_template(self, output_dir='output/'):
        # Download part image ------------------------------------------>
        if self.page['Meta']['image']:
            try:
                request = urllib2.Request(self.page['Meta']['image'], None, {
                    'User-Agent': self.user_agent
                })
                data = urllib2.urlopen(request)

                # Create image directory if it doesn't exist already
                if not os.path.exists('{0}images'.format(output_dir)):
                    os.makedirs('{0}images'.format(output_dir))

                with open('{0}images/{1}{2}'.format(output_dir, self.page['Meta']['part_number'], self.page['Meta']['img_type']), 'wb') as img_f:
                    img_f.write(data.read())
                    img_f.close()
            except urllib2.URLError:
                raise ValueError("Error loading image URL")
            except Exception as e:
                raise ValueError("Image file download failed: {0!s}".format(e))

        # Parse given template_dir variable from interface ------------->
        path_indices = self.template_dir.split('/')
        for var in enumerate(path_indices):
            if '.html' in var[1]:
                template_file = path_indices[var[0]]
                self.template_dir = self.template_dir.split(var[1])[0]

        self.env = Environment(
            loader=PackageLoader('bomara', self.template_dir),
            autoescape=True
        )

        with open('{0}{1}.htm'.format(output_dir, self.page['Meta']['part_number']), 'w') as t:
            template = self.env.get_template(template_file)
            template = template.render(
                meta=self.page['Meta'],
                techspecs=zip(self.page['Techspecs'], self.page['Headers']),
                bf=self.page['BF']
            ).encode('utf-8')
            t.write(template)
            t.close()

        bomara.tools.log('Created: '+self.page['Meta']['part_number'])
        return self.page['Meta']['part_number']
"""