from bomara.crawler import Crawler
import re

def parser(self):
    # Get description & part number ---------------------------------->
    features = self.soup.find('div', id='features').find('div', class_='features__info').find_all('div')
    if len(features) > 1:
        self.page['Meta']['description'] = features[1].get_text()
    else:
        self.page['Meta']['description'] = None

    self.page['Meta']['part_number'] = self.soup.find('h2', class_='product-description__part-number').get_text()

    # Parse tech specs ---------------------------------------------->
    techspecs_container = self.soup.find('div', class_='pd-tabs__tab', id='technical_specification')

    self.page['Headers'] = []

    for section in techspecs_container.find_all('div', class_='technical-specification-tab'):
        self.page['Headers'].append(
            section.find('div', class_='technical-specification-tab__header').get_text()
        )

        rows = section.find_all('div', class_='technical-content-block')

        for row in rows:
            title = row.find('strong', class_='technical-content-block__category').get_text()
            description = row.find('div', class_='technical-content-block__data').get_text(strip=True)
            description = description.replace(title, '').replace('\n', '')

            # Checks title filters
            #if filter(lambda x: x in title, self.ignored_headers):
            #    continue

            self.page['Techspecs'].append((title, description))
            self.page['Headers'].append('*')       

    # Get image ---------------------------------------------------->

    self.page['Meta']['img_url'] = 'http:{}'.format(
        self.soup.find('img', class_='product-description__main-block__image').get('src'))

    self.page['Meta']['img_type'] = '.jpg'

    # Includes ----------------------------------------------------->
    self.page['Meta']['includes'] = self.soup.find('h1', class_='product-description-title').get_text()

    # Options ------------------------------------------------------->
    """
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
"""

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

    links=['apc.com/*'],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parser,
)
