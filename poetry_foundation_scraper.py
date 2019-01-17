# used for scraping poetryfoundation.org

import sys
import requests
import re
import csv
import time
import datetime
from bs4 import BeautifulSoup

if (len(sys.argv) == 1):
	print("Please include name of csv file in command line")
	sys.exit(0)

filename = sys.argv[3] + '.csv' 
lower, upper = int(sys.argv[1]), int(sys.argv[2]) # bounds on the number of articles at poetry foundation
oops_class = "c-billboard c-mix-billboard_neutral c-mix-billboard_hatch c-mix-billboard_hatch_darkest c-mix-billboard_offsetForce"
    


# returns html string for given URL
def get_html(url):
	data = requests.get(url)
	return BeautifulSoup(data.text, 'html.parser')

# cleans a div of given data
def clean_div(data, class_name):
    temp = data.find("div", class_= class_name).prettify()
    temp = re.sub('<em>\n', '', temp)             # these two lines remove italic cleanly
    temp = re.sub(r'\n.*</em>\n?', '', temp)
    temp = re.sub(r'>\s*<br/>', '>\nXXXXX', temp) # replaces empty line with placeholder
    temp = re.sub(r'<.+?>', '', temp)             # get rid of divs
    temp = re.sub(r'\n\s*\n*?', '\n', temp)       # remove unnecessary newlines
    temp = re.sub('XXXXX', '', temp)              # remove placeholder
    temp = re.sub(r' +', ' ', temp)               # remove multiple spaces
    temp = re.sub(r'\s*$', '', temp)              # remove whitespace at start and end of string
    temp = re.sub(r'^\s*', '', temp)              # remove whitespace at start and end of string
    return temp


print("\nStarting scraping for IDs from {} to {}\n".format(lower, upper))
t_start = time.time()
with open(filename, 'w') as file:
	writer = csv.writer(file)
	writer.writerow(['Author', 'Title', 'Poetry Foundation ID', 'Content'])

	for n in range(lower, upper):
		if ((10 * (n + 1 - lower)) % (upper - lower) == 0):
			print("{}% scraped".format(100 * (n + 1 - lower) / (upper - lower)))
			print("Total runtime: {}".format(datetime.timedelta(seconds=(time.time() - t_start))))
		name = "https://www.poetryfoundation.org/poems/{}".format(n)
		
		# obtain poem, check validity, extract title, author, and content
		#"""
		d = get_html(name)
		if not d.find_all("div", {"class": oops_class}):
			title = clean_div(d, "c-feature-hd")
			author = clean_div(d, "c-feature-sub")
			content = clean_div(d, "c-feature-bd")

			title = re.sub('\n.*', '', title)
			author = author[3:] # gets rid of initial "By"

			writer.writerow([author, title, n, content]) # write content to csv file

		#"""

		time.sleep(0.1) # wait to avoid overloading website

print("\nScraping complete\n")
