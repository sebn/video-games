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
from os import walk
import sqlite3

from gi.repository import Gtk
from gi.repository import GamesManager

from systems.basesystem import BaseSystem
from metadata import mobygames

class Desktop(GamesManager.System):
	BLACK_LIST = [ "steam.desktop",
	               "lutris.desktop",
	               "badnik.desktop" ]
	
	def __init__(self, library):
		GamesManager.System.__init__(self, reference = "desktop", game_search_type = GamesManager.GameSearchType.APPLICATIONS)
	
	def do_get_game_info(self, library, id):
		info = GamesManager.System._get_game_info(self, library, id)
		
		uri = library.get_game_uri(id)
		entry = DesktopEntry.DesktopEntry(uri)
		
		info.set_property("system", self.get_property("reference"))
		info.set_property("title", entry.getName())
		info.set_property("icon", entry.getIcon())
		return info
	
	def do_is_a_game(self, uri):
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
		
		return is_a_game_entry(uri)
	
	def do_get_game_reference_for_uri(self, uri):
		return path.basename(uri).split(".")[0]
	
	def do_search_new_games(self, library):
		print("desktop: do_search_new_games start")
		for entry in self.get_game_desktop_entries():
			self.add_new_game(entry)
		
		print("desktop: do_search_new_games end")
		self.update_games_metadata(library)
	
	def update_games_metadata(self, library):
		for id in self.get_games_id():
			self.download_metadata(library, id)
	
	def get_games_id(self):
		db = sqlite3.connect(library.path)
		ids = []
		for row in db.execute('SELECT id FROM games WHERE systemid = ?', [self.get_property("id")]):
			ids.append(row[0])
		db.close()
		return ids
	
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
	
	def do_is_game_available(self, library, id):
		db = sqlite3.connect(library.path)
		exists = False
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			exists = path.exists(row[0])
			break
		db.close()
		return exists
	
	def do_get_game_exec(self, library, id):
		db = sqlite3.connect(library.path)
		value = None
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			value = DesktopEntry.DesktopEntry(row[0]).getExec()
		db.close()
		return value
		
	def get_game_desktop_entries(self):
		'''Return the list of the paths of game related and not black listed desktop entries.'''
		def get_application_directories():
			"""Return the list of the application directories"""
			app_dirs = []
			
			for dir in BaseDirectory.xdg_data_dirs:
				app_dir = path.join(dir, "applications")
				if path.exists(app_dir):
					app_dirs.append(app_dir)
			
			return app_dirs
		
		def is_black_listed(file):
			for name in Desktop.BLACK_LIST:
				if file == name:
					return True
			return False
		
		game_entries = []
		
		for dir in get_application_directories():
			for root, dirs, files in walk(dir):
				for file in files:
					if not is_black_listed(file):
						file = path.join(root, file)
						if self.is_a_game(file):
							game_entries.append(file)
		
		return game_entries

if __name__ == '__main__':
	desktop = Desktop()
	for entry in desktop.get_game_desktop_entries():
		print(entry)
