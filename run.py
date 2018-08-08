#!/usr/bin/python

from apc.crawler import APCCrawler
from apc.gui import run

# Optional: breadcrumbs
# breadcrumbs => list of tuples for every breadcrumb
# reader = APCCrawler('http://www.apc.com/shop/us/en/products/APC-Smart-UPS-SRT-1000VA-RM-120V/P-SRT1000RMXLA', [('APC Rocks', 'http')])

# Optional: write
# write => outputs parsing results to a json file (output.json)
# reader.parse()

# Optional: template, output_dir
# path => template file location
# output_dir => directory to generate files to
# reader.apply_template()

# Run GUI
run()