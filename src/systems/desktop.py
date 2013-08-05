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
		GamesManager.System.__init__(self, reference = "desktop")
	
	def do_get_game_info(self, id):
		info = GamesManager.System._get_game_info(self, id)
		
		uri = None
		db = sqlite3.connect(self.get_property("library").path)
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			uri = row[0]
			break
		db.close()
		entry = DesktopEntry.DesktopEntry(uri)
		
		info.set_property("system", self.get_property("reference"))
		info.set_property("title", entry.getName())
		info.set_property("icon", entry.getIcon())
		return info
	
	def do_search_new_games(self):
		print("update desktop start")
		for entry in self.get_game_desktop_entries():
			# Check the game's existence in the table
			exists = False
			
			db = sqlite3.connect(self.get_property("library").path)
			for row in db.execute('SELECT * FROM uris WHERE uri = ?', [entry]):
				exists = True
				break
			db.close()
			
			if not exists:
				self.add_new_game_to_database(entry)
		
		print("update desktop end")
		self.update_games_metadata()
	
	def add_new_game_to_database (self, uri):
		db = sqlite3.connect(self.get_property("library").path)
		# obtenir un identifiant unique de jeu : la racine du nom de fichier du .desktop
		gameid = None
		gameref = path.basename(uri).split(".")[0]
		
		# Getting the game id
		for row in db.execute('SELECT games.id FROM games, systems WHERE games.systemid = systems.id AND games.ref = ?', [gameref]):
			gameid = row[0]
			break
		
		if not gameid:
			# Adding the game
			db.execute('INSERT INTO games (id, systemid, ref, played, playedlast) VALUES (NULL, ?, ?, ?, ?)', [self.get_property("id"), gameref, 0, 0])
			
			# Getting the new game id
			for row in db.execute('SELECT games.id FROM games, systems WHERE games.systemid = systems.id AND games.ref = ?', [gameref]):
				gameid = row[0]
				break
		
		# Adding the URI
		db.execute('INSERT INTO uris (id, uri, gameid) VALUES (NULL, ?, ?)', [uri, gameid])
		
		db.commit()
		
		self.get_property("library").emit("game_updated", gameid)
		
		db.close()
	
	def update_games_metadata(self):
		for id in self.get_games_id():
			self.download_metadata(id)
	
	def get_games_id(self):
		db = sqlite3.connect(self.get_property("library").path)
		ids = []
		for row in db.execute('SELECT id FROM games WHERE systemid = ?', [self.get_property("id")]):
			ids.append(row[0])
		db.close()
		return ids
	
	def download_metadata(self, id):
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
		db = sqlite3.connect(self.get_property("library").path)
		print("found results for", name, "on", system, "on Mobygames")
		if len(urls) > 0:
			print("getting informations for", name, "on", system, "on Mobygames")
			info = mobygames.get_game_info(urls[0])
			db.execute('UPDATE games SET developer = ?,released = ?, genre = ?, description = ?, rank = ? WHERE id = ?', [info['developer'], info['released'], info['genre'], info['description'], info['rank'], id])
			db.commit()
			print("got informations for", name, "on", system, "on Mobygames")
			self.get_property("library").emit("game_updated", id)
		db.close()
	
	def do_is_game_available(self, id):
		db = sqlite3.connect(self.get_property("library").path)
		exists = False
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			exists = path.exists(row[0])
			break
		db.close()
		return exists
	
	def do_get_game_exec(self, id):
		db = sqlite3.connect(self.get_property("library").path)
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
						if is_a_game_entry(file):
							game_entries.append(file)
		
		return game_entries

if __name__ == '__main__':
	desktop = Desktop()
	for entry in desktop.get_game_desktop_entries():
		print(entry)
