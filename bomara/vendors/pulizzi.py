from bomara.crawler import Crawler
import urllib2
from bs4 import BeautifulSoup

def parse(self):
    #Get description & part number ---------------------------------->
    self.page['Meta']['part_number'] = self.soup.find('div',
        id='wmSkuPageTopLeftCol').find_all('h1')[0].get_text().replace('\n', '').replace(' (End of Life)', '')
    self.page['Meta']['description'] = 'Pulizzi {}'.format(self.page['Meta']['part_number'])

    specs = self.soup.find('div', id='wmSkuPageMain').find('table')
    for img in specs.find_all('img'):
        if 'Download' in str(img):
            self.page['Meta']['img_url'] = img.get('src') 
    
    self.page['Meta']['img_type'] = '.jpg'

    for tr in specs.find_all('tr'):
        try:
            self.page['Headers'].append(tr.find('td', class_='TableHead').get_text())
            self.page['Techspecs'].append('*')
        except:
            td = tr.find_all('td')
            title = td[0].get_text()

            if title == 'Plug' or title == 'Outlets':
                url = td[1].find('img').get('src')
                img_data = urllib2.urlopen(url)
                with open(self.output_dir+'/images/'+self.page['Meta']['part_number']+'-'+title+'.gif', 'wb') as f:
                    f.write(img_data.read())
                    f.close()
                description = td[1].get_text() + "<br/><img src='images/{}.gif'></img>".format(self.page['Meta']['part_number']+'-'+title)
            elif filter(lambda x: title == x, self.ignored_headers):
                continue
            elif title == 'Drawing':
                description = '<img class="display-image-1_5" src="images/{}.jpg"></img>'.format(self.page['Meta']['part_number'])
            elif len(td) > 1 and title != u"\u00A0":
                description = td[1].get_text()
            else:
                continue

            self.page['Techspecs'].append((title, description))
            self.page['Headers'].append('*')

# This handles the OLD Eaton website only ->

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
    ignored_headers = ['Function', 'MIB', 'Device Installer'],
    # Mostly APC exclusive
    software_identifiers = [],

    # Required returns: 
    #   self.page['Meta']['part_number', 'img_url', 'img_type']
    #   self.page['Techspecs', 'Headers']
    parser = parse,
)