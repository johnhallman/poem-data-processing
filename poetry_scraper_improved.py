# used for scraping poetryfoundation.org
# Author: John Hallman

import sys
import re
import csv
import time
import sets
import datetime
import requests
from bs4 import BeautifulSoup
from selenium import webdriver


# define parameters and set up scraper settings
start_page, end_page = int(sys.argv[1]), int(sys.argv[2]) # out of 2225 pages, CHANGE FOR EACH PROGRAM
pages = end_page - start_page + 1
filename = 'pages{}-{}.csv'.format(start_page, end_page)
browser = webdriver.Chrome('/Users/johnhallman/mlcourse/junior_ml/chromedriver')
browser.implicitly_wait(3)


# returns string displaying time taken since t_start
def time_taken(t_start):
	d = datetime.timedelta(seconds=(time.time() - t_start))
	s = str(d).split('.')[0]
	return s


# removes whitespace at beginning and end of string
def cut_whitespace(s):
	return re.sub(r'\s*$', '', re.sub(r'^\s*', '', s))


# cleans poem html
def clean_content(temp):
	temp = re.sub(r"([a-zA-Z])\s*<em>\s*", r"\1 ", temp) # remove italic, keep space if letters nearby
	temp = re.sub(r"\s*</em>\s*([a-zA-Z])", r" \1", temp)
	temp = re.sub(r'\s*<em>\s*', '', temp)        # remove italic and space near punctuation
	temp = re.sub(r'\s*</em>\s*', '', temp)
	temp = re.sub(r'>\s*<br/>', '>\nXXXXX', temp) # replaces empty line with placeholder
	temp = re.sub(r'<.+?>', '', temp)             # get rid of divs
	temp = re.sub(r'\n\s*\n*?', '\n', temp)       # remove unnecessary newlines
	temp = re.sub('XXXXX', '', temp)              # remove placeholder
	temp = re.sub(r' +', ' ', temp)               # remove multiple spaces
	return temp


# cleans a full web html file
def clean(poem_data):
	title   = poem_data.find("div", class_= "c-feature-hd").prettify()
	author  = poem_data.find("span", class_= "c-txt c-txt_attribution").prettify()
	content = poem_data.find("div", class_= "c-feature-bd").prettify()
	title   = re.sub(r'<.+?>', '', title)
	author  = re.sub(r'<.+?>', '', author)
	author  = re.sub(r'By\s*', '', author)
	content = clean_content(content)
	title   = cut_whitespace(title)
	author  = cut_whitespace(author)
	content = cut_whitespace(content)
	return title, author, content


# loop over all the pages and extract all poems
print("\nScraping {} pages to {}\n".format(pages, filename))
t_start = time.time()
ID_list = set()

with open(filename, 'w') as file:
	writer = csv.writer(file)
	writer.writerow(['Author', 'Title', 'Poetry Foundation ID', 'Content'])

	# loop over all pages in range
	for t in range(start_page, end_page + 1):

		# extract links from page list
		url = "https://www.poetryfoundation.org/poems/browse#page={}&sort_by=title".format(t)
		browser.get(url)
		html_soup = BeautifulSoup(browser.page_source, 'html.parser')
		list_soup = html_soup.findAll("a")

		# check links for poems, clean data and write to csv file
		for raw_soup in list_soup:
			clean_soup = raw_soup.prettify()
			clean_soup = re.search(r'"https://www\.poetryfoundation\.org.*?/poems/\d+/.*?"', clean_soup)
			if not clean_soup:
				continue

			poem_url = clean_soup.group(0)[1:-1]
			poem_request = requests.get(poem_url)
			if not re.search(r'/poems/', poem_request.url):
				continue

			ID = re.search(r"/poems/(\d+)", poem_url).group(1)
			if ID in ID_list:
				continue

			ID_list.add(ID)
			poem_data = BeautifulSoup(poem_request.text, 'html.parser')
			title, author, content = clean(poem_data)
			writer.writerow([author, title, ID, content])

			time.sleep(0.01) # avoids overloading website

		# occasionally print status of scraping
		if (((10 * t) % pages == 0)):
			print("{}% scraped, total runtime {}".format(100 * t / pages, time_taken(t_start)))

browser.quit()

print("\nScraped {} pages to {}, runtime: {}\n".format(pages, filename, time_taken(t_start)))
print("\nScraping complete")

