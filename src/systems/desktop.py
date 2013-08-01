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
	
	def __init__(self, gamesdb):
		GamesManager.System.__init__(self, id = "desktop")
		self.path = gamesdb.path
		db = sqlite3.connect(self.path)
		db.execute('''CREATE TABLE IF NOT EXISTS desktop
		              (
		                id INTEGER PRIMARY KEY,
		                path TEXT,
		                developer TEXT,
		                released TEXT,
		                genre TEXT,
		                description TEXT,
		                rank TEXT
		              )''')
		db.close()
	
	def do_get_game_info(self, id):
		'''Return a GameInfo object representing the game or None if an error occured.'''
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute('SELECT desktop.id, desktop.path, desktop.developer, desktop.released, desktop.genre, desktop.description, desktop.rank, games.time_played, games.last_played FROM games, desktop WHERE games.gameid = desktop.id AND desktop.id = ?', [id])
		result = c.fetchone()
		db.close()
		info = None
		
		if result:
			entry = DesktopEntry.DesktopEntry(result[1])
			info = GamesManager.GameInfo()
			info.set_property("id", id)
			info.set_property("title", entry.getName())
			info.set_property("developer", result[2])
			info.set_property("icon", entry.getIcon())
			info.set_property("released", result[3])
			info.set_property("system", self.get_property("id"))
			info.set_property("genre", result[4])
			info.set_property("played", result[7])
			info.set_property("playedlast", result[8])
			info.set_property("description", result[5])
			info.set_property("rank", result[6])
		
		return info
	
	def do_search_new_games(self):
		print("update desktop start")
		db = sqlite3.connect(self.path)
		for entry in self.get_game_desktop_entries():
			# Check the game's existence in the table
			id = None
			for row in db.execute('SELECT id FROM ' + self.get_property("id") + ' WHERE path = ?', [entry]):
				id = row[0]
			
			# If the game isn't in the table: add it
			if not id:
				db.execute('INSERT INTO ' + self.get_property("id") + ' (id, path) VALUES (NULL, ?)', [entry])
				for row in db.execute('SELECT id FROM ' + self.get_property("id") + ' WHERE path = ?', [entry]):
					id = row[0]
				db.execute('INSERT INTO games VALUES (NULL, ?, ?, 0, 0)', [id, self.get_property("id")])
				db.commit()
				self.get_property("library").emit("game_updated", self.get_global_game_id(id))
		db.close()
		print("update desktop end")
		self.update_games_metadata()
	
	def update_games_metadata(self):
		for id in self.get_games_id():
			self.download_metadata(id)
	
	def get_games_id(self):
		db = sqlite3.connect(self.path)
		ids = []
		for row in db.execute('SELECT id FROM desktop'):
			ids.append(row[0])
		db.close()
		return ids
	
	def get_global_game_id(self, id):
		db = sqlite3.connect(self.path)
		gid = None
		for row in db.execute('SELECT id FROM games WHERE gameid = ? AND system = "desktop"', [id]):
			gid = row[0]
			break
		db.close()
		return gid
	
	def download_metadata(self, id):
		print("try to download metadata for", id)
		info = self.do_get_game_info(id)
		if not info:
			return
		name, system = info.get_property("title"), info.get_property("system")
		if not (name and system):
			return
		print("downloading metadata for", id)
		urls = mobygames.get_search_results(name, system)
		db = sqlite3.connect(self.path)
		if len(urls) > 0:
			info = mobygames.get_game_info(urls[0])
			db.execute('UPDATE desktop SET developer = ?,released = ?, genre = ?, description = ?, rank = ? WHERE id = ?', [info['developer'], info['released'], info['genre'], info['description'], info['rank'], id])
			db.commit()
			self.get_property("library").emit("game_updated", self.get_global_game_id(id))
		db.close()
	
	def do_is_game_available(self, id):
		db = sqlite3.connect(self.path)
		exists = False
		for row in db.execute('SELECT path FROM desktop WHERE id = ?', [id]):
			exists = path.exists(row[0])
			break
		db.close()
		return exists
	
	def do_get_game_exec(self, id):
		db = sqlite3.connect(self.path)
		value = None
		for row in db.execute('SELECT path FROM desktop WHERE id = ?', [id]):
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
