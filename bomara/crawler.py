#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import os
import copy
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
        self._schema = schema
        self._parser = parser
        self._parser_args = parser_args
        self._ignored_headers = ignored_headers
        self._software_identifiers = software_identifiers
        self.page = schema

        # Constants
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        # Not currently supported
        self.breadcrumbs = None

        self.reset()

    def reset(self):
        self.page = copy.deepcopy(self._schema)

        self.parser_warning = None
        self.page['Meta']['vendor'] = self.vendor

        self.ignored_headers = self._ignored_headers
        self.software_identifiers = self._software_identifiers

        self.parse = self._parser
        self.soup = None

    def dl_img(self, url, img_type, name):
        try:
            request = urllib2.Request(url, None, {
                'User-Agent': self.user_agent
            })
            data = urllib2.urlopen(request)

            # Create image directory if it doesn't exist already
            if not os.path.exists('output/images'):
                os.makedirs('output/images')

            with open('output/images/{0}{1}'.format(name, img_type), 'wb') as img_f:
                img_f.write(data.read())
                img_f.close()
            return True
        except urllib2.URLError:
            return "Error loading image URL"
        except Exception as e:
            return "Image file download failed: {0!s}".format(e)

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
        self.soup = BeautifulSoup(html, 'lxml')   

    def apply(self, template='base.html', write=False):
        try:
            self.parse(self)
        except Exception as e:
            raise ValueError('Failed to parse: {}'.format(e))

        # Write provides a JSON data sheet
        if write:
            output = json.dumps(self.page, sort_keys=True, indent=4)
            with open('output/output.json', 'w') as f:
                bomara.tools.log('Writing {} to output.json'.format(
                    self.page['Meta']['part_number']))
                f.write(output)
                f.close()

        # Download part image
        img = self.dl_img(
            # URL
            self.page['Meta']['img_url'],
            # Image type
            self.page['Meta']['img_type'],
            # Name
            self.page['Meta']['part_number']
        )
        if img != True:
            self.parser_warning = str(img)

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
        if 'Options' not in self._schema:
            self.page['Options'] = False

        with open('output/{0}.htm'.format(self.page['Meta']['part_number']), 'w') as t:
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
