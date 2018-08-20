#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import json
import re
import os
import bomara.tools
from jinja2 import Template, Environment, PackageLoader, select_autoescape
from bs4 import BeautifulSoup

# Initialize template directory
template_dir = None

#
# APCCrawler()
# --------------------------------------------------------
# Optional: breadcrumbs
# breadcrumbs => list of tuples for every breadcrumb
#
# APCCrawler().connect()
# --------------------------------------------------------
# Required: link to APC page
#
# APCCrawler().parse()
# --------------------------------------------------------
# Optional: write
# write => outputs parsing results to a json file (output.json)
#
# APCCrawler().apply_template()
# --------------------------------------------------------
# Optional: output_dir
# output_dir => directory to generate files to
#


class APCCrawler:
    # Reads url passed into class, parses data sheet as json,
    # and applies that data, among other things, to a jinja2 template
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.page = {
            'Meta': dict(),
            'Techspecs': [],
            'Headers': [],
            'Options': {
                'Accessories': [],
                'Services': [],
                'Software': [],
            }
        }

        self.page['Meta']['vendor'] = 'APC'
        self.template_dir = template_dir
        self.breadcrumbs = []
        self.techspecs_title_filters = ['Extended Run Options', 'PEP', 'EOLI']
        self.software_options_filters = ['software', 'struxureware']

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

        self.page['Meta']['description'] = self.soup.find(
            class_='page-header').get_text()
        self.page['Meta']['part_number'] = self.soup.find(
            class_='part-number').get_text()

    def parse(self, write=False):
        # Parse tech specs ---------------------------------------------->
        page_div = self.soup.find('div', id='techspecs')
        techspecs = []
        for header in page_div.find_all('h4'):
            cheader = header.contents[0]
            cheader = cheader.replace('&amp;', '&')

            if self.page['Headers']:
                self.page['Headers'][len(self.page['Headers'])-1] = cheader
            else:
                self.page['Headers'].append(cheader)

            list_item = header.find_next_sibling('ul', class_='table-normal')
            for contents in list_item.find_all(class_='col-md-12'):
                for title in contents.find(class_='col-md-3 bold'):
                    # Checks title filters
                    if filter(lambda x: x in title, self.techspecs_title_filters):
                        continue

                    contents = contents.get_text(
                        ' ', strip=True).replace(title, '')

                    self.page['Techspecs'].append((title, contents))
                    self.page['Headers'].append('*')

        # Get image ---------------------------------------------------->
        try:
            # Newer pages
            self.page['Meta']['image'] = 'http:{}'.format(
                self.soup.find_all(class_='img-responsive')[0].get('src'))
        except Exception:
            # Applicable to some older pages
            self.page['Meta']['image'] = 'http:{}'.format(
                self.soup.find_all(id='DataDisplay')[0].get('src'))

        self.page['Meta']['img_type'] = '.jpg'

        # Includes ----------------------------------------------------->
        product_overview = self.soup.find_all(id='productoverview')[0]

        # Default includes to none
        self.page['Meta']['includes'] = ''
        try:
            # Test for explicit reference to includes
            # -> Usually found in older pages
            self.page['Meta']['includes'] = self.soup.find(
                class_='includes').get_text()
        except Exception:
            # Scan for includes instead
            for p in product_overview.find_all('p'):
                if 'Includes' in p.get_text():
                    self.page['Meta']['includes'] = p.get_text()
                    break

        self.page['Meta']['includes'] = re.sub(
            '\s\s+', ' ', self.page['Meta']['includes']).replace(' ,', ',')

        # Options ------------------------------------------------------->

        try:
            options = self.soup.find('div', id='options')

            for option in options.find_all('div', class_='col-md-12'):
                option_item = option.find('div', class_='option-item')

                if option_item is None:
                    # There are multiple 'col-md-12' divs, find the right one
                    continue

                option_title = option_item.find('a').get_text()
                option_description = option_item.find('p').get_text()

                if option_description == '':
                    option_description = '...'

                option_number = option.find('div', class_='part-no').get_text()
                # Remove tabs and new lines
                option_description = option_description.replace(
                    '\n', '').replace('\t', '')
                option_number = option_number.replace(
                    '\n', '').replace('\t', '')

                # 3 Available option types:
                # 	- Accessories
                # 	- Services
                #	- Software

                if option_number[0].lower() == 'w':
                    option_type = 'Services'
                elif filter(lambda x: x in option_title.lower(), self.software_options_filters):
                    option_type = 'Software'
                else:
                    option_type = 'Accessories'

                self.page['Options'][option_type].append(
                    (option_title, option_description, option_number))

            # Sort options alphanumerically
            for key, value in self.page['Options'].iteritems():
                self.page['Options'][key] = sorted(value, key=lambda x: x[2])

        except Exception:
            self.page['Options'] = False

        # Write provides a JSON data sheet ----------------------------->
        if write:
            output = json.dumps(self.page, sort_keys=True, indent=4)
            with open('output.json', 'w') as f:
                bomara.tools.log('Writing {} to output.json'.format(
                    self.page['Meta']['part_number']))
                f.write(output)
                f.close()

    def apply_template(self, output_dir='output/'):
        # Download part image ------------------------------------------>
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

        # Breadcrumbs -------------------------------------------------->
        if not self.breadcrumbs:
            self.page['Meta']['breadcrumbs'] = ''
        else:
            breadcrumbs = map(
                lambda x: u"<a href='{0}'>{1}</a> »".format(x[1], x[0]), self.breadcrumbs)
            self.page['Meta']['breadcrumbs'] = ''.join(breadcrumbs)

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
                options=self.page['Options']
            ).encode('utf-8')
            t.write(template)
            t.close()

        bomara.tools.log('Created: '+self.page['Meta']['part_number'])
        return self.page['Meta']['part_number']

class VertivCrawler:
    # Reads url passed into class, parses data sheet as json,
    # and applies that data, among other things, to a jinja2 template
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        self.page = {
            'Meta': dict(),
            'Techspecs': [],
            'Headers': [],
        }

        self.parser_warning = None
        self.page['Meta']['vendor'] = 'Vertiv / Avocent'
        self.template_dir = template_dir
        self.techspecs_title_filters = []
        self.software_options_filters = ['software', 'struxureware']

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

        if part_number[2] == 'Serial':
            self.page['Meta']['part_number'] = part_number[1] 
        else:
            self.page['Meta']['part_number'] = part_number[1] + part_number[2]

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

    def parse(self, write=False, family=None):
        # Check if valid product page ----------------------------------->
        if self.soup.find('span', class_='subtitle').get_text() == 'Product Family':
            family_links = []
            for link in self.soup.find_all('a', class_='same-height-target'):
                family_links.append("http://www.vertivco.com" + link.get('href'))
            
            bomara.tools.process_family_links('Vertiv', family_links, self.page['Meta']['part_number'], self.page['Meta']['description'])
        else:
            # Parse tech specs ------------------------------------------>
            try:
                page_div = self.soup.find_all('div', class_='prod-title')[0]
                page_div = page_div.parent
                self.parse_techspecs(page_div)
            except:
                # No tech specs available
                self.parser_warning = "This page doesn't have any tech specs"
        
        # Parse tech specs ------------------------------------------>
        if family:
            self.page['Meta']['breadcrumbs'] = "<a href='{0}.htm'>{1}</a>".format(
                family[0], family[1].replace('Avocent', '').replace('Vertiv', ''))

        # Get image ---------------------------------------------------->

        image_holder = self.soup.find('div', class_='main-image-holder')
        self.page['Meta']['image'] = 'http://www.vertivco.com' + \
            image_holder.find('img').get('data-src')
        self.page['Meta']['img_type'] = '.png'

        if write:
            output = json.dumps(self.page, sort_keys=True, indent=4)
            with open('output.json', 'w') as f:
                bomara.tools.log('Writing {} to output.json'.format(
                    self.page['Meta']['part_number']))
                f.write(output)
                f.close()

    def apply_template(self, output_dir='output/'):
        # Download part image ------------------------------------------>
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
            ).encode('utf-8')
            t.write(template)
            t.close()

        bomara.tools.log('Created: '+self.page['Meta']['part_number'])
        return self.page['Meta']['part_number']
