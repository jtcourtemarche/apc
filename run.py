from apc import APCScraper

reader = APCScraper('http://www.apc.com/shop/us/en/products/APC-Smart-UPS-SRT-1000VA-RM-120V/P-SRT1000RMXLA')
reader.parse()
reader.apply_template()