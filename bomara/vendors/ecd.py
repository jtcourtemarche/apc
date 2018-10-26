from bomara.crawler import Crawler
from bs4 import BeautifulSoup

def parse(self):
    # Get description & part number ---------------------------------->
    datasheet = self.soup.find('table', class_='datasheet')
    self.page['Meta']['part_number'] = datasheet.find('tr').find('h3').get_text()
    self.page['Meta']['description'] = datasheet.find('tr').find('h4').get_text()
    self.page['Meta']['includes'] = self.soup.find('div', class_='title').get_text()

    self.page['Meta']['img_url'] = 'https://www.ecdata.com' + datasheet.find('tr').find('img').get('src')
    self.page['Meta']['img_type'] = '.gif'

    table = None

    # Grab data table
    for tr in datasheet.find_all('tr'):
        for td in tr.find_all('td'):
            if 'SPECIFICATIONS' in td.get_text():
                table = td.parent.parent.parent.find_all('tr')
                break

    self.page['Headers'].append('General')

    # Ignore row that says 'SPECIFICATIONS'
    del table[0]

    for row in table:
        col = [entry.get_text().replace(u'\u00a0', '') for entry in row.find_all('td') if entry.get_text().replace('\u00a0', '').strip(' ') != '']
        if len(col) > 1:
            self.page['Techspecs'].append(col)
            self.page['Headers'].append('*')

crawler = Crawler(
    # Vendor name
    vendor = 'East Coast Datacom',
    schema = {
        # Required
        'Meta': dict(),
        # Required
        'Techspecs': [],
        # Required
        'Headers': [],
    },
    # Ignored tech specs headers
    ignored_headers = [],
    # Mostly APC exclusive
    software_identifiers = [],

    links=['ecdata.com/*'],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parse,
)