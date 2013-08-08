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
	
	BLACK_LIST = [ "steam.desktop",
	               "lutris.desktop",
	               "badnik.desktop" ]
	
	def __init__(self):
		GamesManager.Desktop.__init__(self, reference = "desktop", game_search_type = GamesManager.GameSearchType.APPLICATIONS)
	
	###
	### Abstract methods that have to be implemented.
	###
	
	def do_get_game_info(self, library, id):
		print("Get info for game", id)
		info = GamesManager.System._get_game_info(self, library, id)
		
		uri = library.get_game_uri(id)
		uri = urllib.parse.urlparse(uri).path
		
		entry = DesktopEntry.DesktopEntry(uri)
		
		info.set_property("system", self.get_property("reference"))
		info.set_property("title", entry.getName())
		info.set_property("icon", entry.getIcon())
		return info
	
	def do_get_game_exec(self, library, id):
		db = sqlite3.connect(library.path)
		value = None
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			uri = urllib.parse.urlparse(row[0]).path
			value = DesktopEntry.DesktopEntry(uri).getExec()
		db.close()
		return value
	
	def do_query_is_game_available(self, library, id):
		db = sqlite3.connect(library.path)
		exists = False
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			game_path = urllib.parse.urlparse(row[0]).path
			exists = path.exists(game_path)
			break
		db.close()
		return exists
	
	def do_query_is_a_game(self, uri):
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
		
		uri = urllib.parse.urlparse(uri).path
		return is_a_game_entry(uri)
	
	def do_get_game_reference_for_uri(self, uri):
		uri = urllib.parse.urlparse(uri).path
		return path.basename(uri).split(".")[0]
	
	###
	### Utility methods.
	###
	
	def download_metadata(self, library, id):
		print("try to download metadata for", id)
		info = self.do_get_game_info(id)
		if not info:
			return
		name, system = info.get_property("title"), info.get_property("system")
		if not (name and system):
			return
		print("downloading metadata for", id)
		print("searching for", name, "on", system, "on Mobygames")
		urls = mobygames.get_search_results(name, system)
		db = sqlite3.connect(library.path)
		print("found results for", name, "on", system, "on Mobygames")
		if len(urls) > 0:
			print("getting informations for", name, "on", system, "on Mobygames")
			info = mobygames.get_game_info(urls[0])
			db.execute('UPDATE games SET developer = ?,released = ?, genre = ?, description = ?, rank = ? WHERE id = ?', [info['developer'], info['released'], info['genre'], info['description'], info['rank'], id])
			db.commit()
			print("got informations for", name, "on", system, "on Mobygames")
			library.emit("game_updated", id)
		db.close()

