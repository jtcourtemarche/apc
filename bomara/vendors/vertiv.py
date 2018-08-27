from bomara.crawler import Crawler
import bomara.tools

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
            if filter(lambda x: x in title, self.ignored_headers):
                continue

            self.page['Techspecs'].append((title, description))
            self.page['Headers'].append('*')

def parse(self, write=False, family_member=None):
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
            parse_techspecs(self, page_div)
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
        self.page['Meta']['img_url'] = 'http://www.vertivco.com' + \
            image_holder.find('img').get('data-src')
        self.page['Meta']['img_type'] = '.png'
    except:
        self.page['Meta']['img_url'] = None

    if write:
        output = json.dumps(self.page, sort_keys=True, indent=4)
        with open('output.json', 'w') as f:
            bomara.tools.log('Writing {} to output.json'.format(
                self.page['Meta']['part_number']))
            f.write(output)
            f.close()

# ->

crawler = Crawler(
    # Vendor name
    vendor = 'Vertiv',
    schema = {
        # Required
        'Meta': dict(),
        # Required
        'Techspecs': [],
        # Required
        'Headers': [],
        # Optional
        'BF': {
            'Benefits': [],
            'Features': []
        }
    },
    # Ignored tech specs headers
    ignored_headers = [],
    # Mostly APC exclusive
    software_identifiers = [],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parse,
)