from apc import APCScraper

# Optional: breadcrumbs
# breadcrumbs => list of tuples for every breadcrumb
reader = APCScraper('http://www.apc.com/shop/us/en/products/APC-Smart-UPS-SRT-1000VA-RM-120V/P-SRT1000RMXLA', [('APC Rocks', 'http')])

# Optional: write
# write => outputs parsing results to a json file (output.json)
reader.parse()

# Optional: template, output_dir
# template => template file location
# output_dir => directory to generate files to
reader.apply_template()