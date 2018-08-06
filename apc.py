#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2, json, re, webbrowser, os
from jinja2 import Template, Environment, PackageLoader, select_autoescape
from bs4 import BeautifulSoup

class APCCrawler:
	# Reads url passed into class, parses data sheet as json,
	# and applies that data, among other things, to a jinja2 template
	def __init__(self, url, breadcrumbs=[('','')]):
		self.user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
		self.page = {
			'Meta': dict(),
			'Headers':[],
			'Content': dict(),
		}

		self.breadcrumbs = breadcrumbs

		self.env = Environment(
			loader=PackageLoader('main', 'templates'),
			autoescape=select_autoescape(['html', 'xml'])
		)

		#  CONNECT ---------------------------------------------->
		try:
			self.request = urllib2.Request(url, None, {
				'User-Agent':self.user_agent
			})
			self.data = urllib2.urlopen(self.request)
		except:
			raise ValueError("Not a valid url!")

		if (self.data.getcode() != 200):
			raise ValueError('Error: {0!s}'.format(self.data.getcode()))
		#  ------------------------------------------------------>

		html = self.data.read()
		self.soup = BeautifulSoup(html, 'html.parser')
		
		self.page['Meta']['description'] = self.soup.find(class_='page-header').get_text()
		self.page['Meta']['part_number'] = self.soup.find(class_='part-number').get_text()

	def filter_content(self, list_item, title):
		# Remove Unicode Characters
		content = list_item.get_text(' ', strip=True).encode('ascii', 'ignore')

		# Remove first instance of title
		content = content.replace(title, '', 1)

		# Removes spaces & tabs
		content = re.sub(r"[\n\t]*", "", content)

		if 'View Runtime Graph' in content:
			scrot_url = "http://www.apc.com/products/runtimegraph/runtime_graph.cfm?base_sku={0}&chartSize=large".format(self.page['Meta']['part_number'])

			#webbrowser.open(scrot_url)
			content = "<img class='display-image-1_5' src='images/{0}-runtime.png'>".format(self.page['Meta']['part_number'])

		# Handle efficiency graphs
		#if 'View Efficiency Graph' in content:	

		return content	

	def parse(self, write=False):
		page_div = self.soup.find('div', id='techspecs')
		for header in page_div.find_all('h4'):
			header = header.contents[0]
			header = header.replace('&amp;', '&')
		
			self.page['Headers'].append(header)

		for list_item in page_div.find_all(class_='col-md-12 no-gutter'):
			for title in list_item.find(class_='col-md-3 bold'):
				# Skip over this option, unecessarily difficult to retrieve this info because it links to
				# a separate data sheet
				if 'Extended Run Options' in title:
					continue

				self.page['Content'][title] = self.filter_content(list_item, title)
		
		# Get image
		self.page['Meta']['image'] = 'http:{0}'.format(self.soup.find_all(class_='img-responsive')[0].get('src'))

		output = json.dumps(self.page, sort_keys=True, indent=4)
		
		# Write provides a JSON data sheet
		if write:
			with open('output.json', 'w') as f:
				print 'Writing to output.json'
				f.write(output)
				f.close()

		return output

	def apply_template(self, template='templates/base.html', output_dir='out/'):
		# Download part image
		try:
			request = urllib2.Request(self.page['Meta']['image'], None, {
				'User-Agent':self.user_agent
			})
			data = urllib2.urlopen(request)
			
			# Create image directory if it doesn't exist already
			if not os.path.exists('{0}images'.format(output_dir)):
				os.makedirs('{0}images'.format(output_dir))

			with open('{0}images/{1}.jpg'.format(output_dir, self.page['Meta']['part_number']), 'wb') as img_f:
				img_f.write(data.read())
				img_f.close()
		except:
			raise ValueError("Image file download failed")

		# Breadcrumbs
		breadcrumbs = map(lambda x: u"<a href='{0}'>{1}</a> »".format(x[1], x[0]), self.breadcrumbs) 

		self.page['Meta']['breadcrumbs'] = ''.join(breadcrumbs)

		# Body
		body = []
		for key, value in self.page['Content'].iteritems():
			body.append((u"<tr><td>{0}</td><td>{1}</td></tr>").format(key, value))

		bsoup = BeautifulSoup(''.join(body), 'html.parser')
		self.page['Meta']['body'] = bsoup.prettify(formatter='html')  

		with open('{0}{1}.htm'.format(output_dir, self.page['Meta']['part_number']), 'w') as t:
			template = self.env.get_template('base.html')
			template = template.render(
				meta = self.page['Meta'],
				content = self.page['Content'],
				headers = self.page['Headers']
			).encode('utf-8')
			t.write(template)
			t.close()
