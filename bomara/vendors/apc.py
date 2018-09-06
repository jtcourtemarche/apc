from bomara.crawler import Crawler
import re

def parser(self):
    # Get description & part number ---------------------------------->
    self.page['Meta']['description'] = self.soup.find(
        class_='page-header').get_text()
    self.page['Meta']['part_number'] = self.soup.find(
        class_='part-number').get_text()

    # Parse tech specs ---------------------------------------------->
    page_div = self.soup.find('div', id='techspecs')
    techspecs = []
    for header in page_div.find_all('h4'):
        cheader = header.contents[0]
        cheader = cheader.replace('&amp;', '&')

        if self.page['Headers'] != []:
            self.page['Headers'][len(self.page['Headers'])-1] = cheader
            self.page['Techspecs'].append('*')
        else:
            self.page['Headers'].append(cheader)
            self.page['Techspecs'].append('*')

        list_item = header.find_next_sibling('ul', class_='table-normal')
        for contents in list_item.find_all(class_='col-md-12'):
            for title in contents.find(class_='col-md-3 bold'):
                # Checks title filters
                if filter(lambda x: x in title, self.ignored_headers):
                    continue

                contents = contents.get_text(
                    ' ', strip=True).replace(title, '').replace('\n', '')

                self.page['Techspecs'].append((title, contents))
                self.page['Headers'].append('*')

    # Get image ---------------------------------------------------->
    try:
        # Newer pages
        self.page['Meta']['img_url'] = 'http:{}'.format(
            self.soup.find_all(class_='img-responsive')[0].get('src'))
    except Exception:
        # Applicable to some older pages
        self.page['Meta']['img_url'] = 'http:{}'.format(
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
            #   - Accessories
            #   - Services
            #   - Software

            if option_number[0].lower() == 'w':
                option_type = 'Services'
            elif filter(lambda x: x in option_title.lower(), self.software_identifiers):
                option_type = 'Software'
            else:
                option_type = 'Accessories'

            self.page['Options'][option_type].append(
                (option_title, option_description, option_number))

        # Sort options alphanumerically / remove if they are empty
        dead_keys = []
        for key, value in self.page['Options'].iteritems():
            if value == []:
                dead_keys.append(key)
            else:
                self.page['Options'][key] = sorted(value, key=lambda x: x[2])
    
        for key in dead_keys: self.page['Options'].pop(key, None)
    except Exception as e:
        self.page['Options'] = False
        self.parser_warning = 'No options on this page: {}'.format(e)

# ->

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
    parser = parser,
)
