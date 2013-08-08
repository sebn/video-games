#!/usr/bin/python3
#    desktop.py Managing game Freedesktop.org desktop entries.
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

from xdg import BaseDirectory
from xdg import DesktopEntry
from xdg import Exceptions
from os import path
import sqlite3
import urllib

from gi.repository import Gtk
from gi.repository import GamesManager

from systems.basesystem import BaseSystem
from metadata import mobygames

class Desktop(GamesManager.Desktop):
	def __init__(self):
		GamesManager.Desktop.__init__(self, reference = "desktop", game_search_type = GamesManager.GameSearchType.APPLICATIONS)
	
	def do_query_is_game_available(self, library, id):
		exists = False
		
		# Check the file's existence
		db = sqlite3.connect(library.path)
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			game_path = urllib.parse.urlparse(row[0]).path
			exists = path.exists(game_path)
			break
		db.close()
		
		#
		if exists:
			for black_listed in library.get_application_black_list():
				if path.basename(game_path) == black_listed:
					return False
		
		return True
	
	def do_query_is_a_game(self, library, uri):
		def is_a_game_category(category):
			"""Return True if the given category can be considered as a game related category, False otherwise"""
			return category == "Game"
		
		def is_a_game_entry(file):
			"""Return True if the given entry path refer to a game related desktop entry, False otherwise"""
			try:
				entry = DesktopEntry.DesktopEntry(file)
				for category in entry.getCategories():
					if is_a_game_category(category):
						return True
				return False
			except:
				return False
		
		def is_black_listed(file):
			file_name = path.basename(file)
			for black_listed in library.get_application_black_list():
				if file_name == black_listed:
					return False
		
		uri = urllib.parse.urlparse(uri).path
		return is_a_game_entry(uri) and not is_black_listed(uri)
	
	def do_get_game_reference_for_uri(self, uri):
		uri = urllib.parse.urlparse(uri).path
		return path.basename(uri).split(".")[0]
	
	def do_download_game_metadata(self, library, game_id):
		info = self.get_game_info(library, id)
		
		name, system = info.get_property("title"), info.get_property("system")
		if not (name and system):
			return info
		
		# Searching the game on Mobygames
		urls = mobygames.get_search_results(name, system)
		
		# Getting information from the game's page on Mobygames
		if len(urls) > 0:
			print("getting informations for", name, "on", system, "on Mobygames")
			dl_info = mobygames.get_game_info(urls[0])
			info.set_property("developer", dl_info["developer"])
			info.set_property("released", dl_info["released"])
			info.set_property("genre", dl_info["genre"])
			info.set_property("description", dl_info["description"])
			info.set_property("rank", dl_info["rank"])
		
		return info
	
	def do_get_application_black_list(self):
		return [ "steam.desktop",
	             "lutris.desktop",
	             "badnik.desktop" ]
