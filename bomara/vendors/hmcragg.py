from bomara.crawler import Crawler
import urllib2
import re
from bs4 import BeautifulSoup

def parse(self):
    #Get description & part number ---------------------------------->
    self.page['Meta']['part_number'] = self.soup.find('div', class_='contents_1col').find_all('h1')[0].get_text()
    self.page['Meta']['description'] = self.soup.find('div', class_='clear').previous_sibling.replace('\r\n', '')

    self.page['Meta']['part_number'] = re.sub("[\(\[].*?[\)\]]", "", self.page['Meta']['part_number']).replace(' ', '')

    self.page['Meta']['img_url'] = None

    outlets = 0

    specs = self.soup.find_all('table', class_='dataTable')[0]
    for img in enumerate(specs.find_all('img')):
        if img[0] > 0:
            if 'Product_Images' in img[1].get('src'):
                self.dl_img(
                    'http://hmcragg.com/'+img[1].get('src'),
                    '.jpg',
                    self.page['Meta']['part_number'] + '-image',
                )
            if '/Icons/' in img[1].get('src'):
                outlets = outlets + 1
                self.dl_img(
                    'http://hmcragg.com/'+img[1].get('src'),
                    '.gif',
                    self.page['Meta']['part_number'] + '-outlet-' + str(outlets)
                )
        else:
            self.page['Meta']['img_url'] = "http://hmcragg.com"+img[1].get('src') 

    self.page['Meta']['img_type'] = '.jpg'

    outlets = 0
    for tr in specs.find_all('tr'):
        if tr.find_all('th') != []:
            self.page['Headers'].append(tr.find('th').get_text())
            self.page['Techspecs'].append('*')
        else:
            td = tr.find_all('td')
            if td != []:
                title = td[0].get_text().replace(':', '').replace('\n', '')

                if filter(lambda x: title == x, self.ignored_headers):
                    continue
                elif title == 'Drawing':
                    description = '<img class="display-image-1_5" src="images/{}.jpg"></img>'.format(self.page['Meta']['part_number'])
                elif title == 'Image':
                    description = '<img class="display-image-1_5" src="images/{}.jpg"></img>'.format(self.page['Meta']['part_number']+'-image')
                elif not title:
                    continue
                elif len(td) == 2:
                    description = td[1].get_text()
                elif len(td) > 2: 
                    if title == 'Outlets':
                        outlets = outlets + 1
                        td = map(lambda x: x.get_text(), td)
                        td.pop(0)
                        description = '{0}<br/><img width="50px" src="images/{1}.gif"></img>'.format(' '.join(td).replace(u'\u00a0', ''), self.page['Meta']['part_number']+'-outlet-'+str(outlets))
                    else:    
                        td = map(lambda x: x.get_text(), td)
                        td.pop(0)
                        description = ' '.join(td)   

                self.page['Techspecs'].append((title, description.replace('\n', '').replace(u'\u00a0', '')))
                self.page['Headers'].append('*')

crawler = Crawler(
    # Vendor name
    vendor = 'Pulizzi',
    schema = {
        # Required
        'Meta': dict(),
        # Required
        'Techspecs': [],
        # Required
        'Headers': [],
    },
    # Ignored tech specs headers
    ignored_headers = ['Inventory Status'],
    # Mostly APC exclusive
    software_identifiers = [],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parse,
)