#!/usr/bin/python3
#    mobygames.py A Python module to search for and extract game metadata from mobygames.com.
#    Copyright (C) 2013 Adrien Plazas
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#    Adrien Plazas <mailto:kekun.plazas@laposte.net>

import urllib
from bs4 import BeautifulSoup
import re
from html.parser import HTMLParser

systems = { "all": -1,
            "desktop": -1,
            "snes": 15,
            "megadrive": 16 }

def urlopen(url):
	'''Try five times ton open (and return) the URL before failing and returning None'''
	for i in range(5):
		try:
			file = urllib.request.urlopen(url)
			return file
		except urllib.error.URLError:
			continue
	return None

def get_search_url(title, system):
	simple_title = title # Needs to modify the title by turning it into a searchable title (+ instead of spaces, no special characters...)
	system_id = systems["all"]
	if system in systems:
		system_id = systems[system]
	return "http://www.mobygames.com/search/quick?q=" + simple_title + "&p=" + str(system_id) + "&search=Go&sFilter=1&sG=on"

def get_search_results(title, system):
	url = get_search_url(title, system)
	file = urlopen(url)
	if not file:
		return []
	content = file.read()
	soup = BeautifulSoup(content)
	
	results = soup.findAll('div', 'searchTitle')
	
	urls = []
	prog = re.compile('.*<a href="(.*?)">.*')
	for result in results:
		match = prog.match(str(result))
		urls.append("http://www.mobygames.com" + match.group(1))
	return urls

def get_game_info(url):
	info = {}
	info['publisher'] = None
	info['developer'] = None
	info['released'] = None
	info['platforms'] = None
	info['publisher'] = None
	info['genre'] = None
	info['perspective'] = None
	info['non-sport'] = None
	info['description'] = None
	info['rank'] = None
	
	file = urlopen(url)
	if not file:
		return info
	content = file.read()
	soup = BeautifulSoup(content)
	
	# Get some raw data
	
	_cover = soup.find('div', id='coreGameCover')
	_release = soup.find('div', id='coreGameRelease')
	_genre = soup.find('div', id='coreGameGenre')
	_rank = soup.find('div', id='coreGameRank')
	_description = soup.find('div', 'rightPanelMain')
	_screenshots_url = url + "/screenshots"
	
	def get_next_div_content(data, next_div_from):
		prog = re.compile('.*' + next_div_from + '.*?< *div.*?>(.*?)< */ *div *>.*')
		match = prog.match(str(data))
		if match:
			return match.group(1)
		else:
			return None
	
	def get_plain_text(data):
		'''Turn HTML data into plain text data'''
		# Replace single or consecutives instanes of <br/> and new lines by a standard new line
		data = re.sub('((< *br */? *>)|\n)+', '\n', data)
		# Remove the tags
		return re.sub('<.*?>', '', data)
	
	# Feed the information dictionary
	
	publisher = get_next_div_content(_release, 'Published by')
	if publisher:
		info['publisher'] = get_plain_text(publisher)
	
	developer = get_next_div_content(_release, 'Developed by')
	if developer:
		info['developer'] = get_plain_text(developer)
	
	released = get_next_div_content(_release, 'Released')
	if released:
		info['released'] = get_plain_text(released)
	
	platforms = get_next_div_content(_release, 'Platforms')
	if platforms:
		info['platforms'] = get_plain_text(platforms)
	
	genre = get_next_div_content(_genre, 'Genre')
	if genre:
		info['genre'] = get_plain_text(genre)
	
	perspective = get_next_div_content(_genre, 'Perspective')
	if perspective:
		info['perspective'] = get_plain_text(perspective)
	
	non_sport = get_next_div_content(_genre, 'Non-Sport')
	if non_sport:
		info['non-sport'] = get_plain_text(non_sport)
	
	description = re.match('.*?</h2>(.*?)<div', str(_description))
	if description:
		info['description'] = get_plain_text(description.group(1))
	
	# Unescape the informations
	
	parser = HTMLParser()
	for key in list(info.keys()):
		if info[key]:
			info[key] = info[key].replace(u'\xa0',u' ')
			info[key] = parser.unescape(info[key])
	
	info['screenshots'] = get_game_screenshots(url)
	
	return info

def get_game_screenshots(url):
	screenshots = []
	
	file = urlopen(url + "/screenshots")
	if not file:
		return screenshots
	content = file.read()
	soup = BeautifulSoup(content)
	
	_screenshots = soup.find('div', 'thumbnailContainer')
	
	_screenshot_pages = re.findall('href="(.*?gameShotId.*?)"', str(_screenshots))
	
	for screenshot_page in _screenshot_pages:
		url = "http://www.mobygames.com" + screenshot_page
		file = urlopen(url)
		if file:
			content = file.read()
			soup = BeautifulSoup(content)
			
			content = soup.find('div', 'rightPanelMain')
			
			result = re.search('href="(/images/shots.*?)"', str(content))
			if result:
				screenshots.append("http://www.mobygames.com" + result.group(1))
	
	return screenshots

if __name__ == '__main__':
	urls = get_search_results('hedgewars', 'desktop')
	if len(urls) > 0:
		info = get_game_info(urls[0])
		print(info)
		if 'description' in info:
			print(info['description'])

