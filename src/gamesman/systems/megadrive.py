#!/usr/bin/python3
#    megadrive.py Managing the SEGA Mega Drive / Genesis system.
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

from os import walk, path
from gamesman.systems.utils import has_suffix

from gi.repository import GamesManager

from gamesman.systems.tosecsystem import TOSECSystem
import sqlite3

class MegaDrive(TOSECSystem):
	def __init__(self, gamesdb):
		TOSECSystem.__init__(self, gamesdb, "megadrive")
		db = sqlite3.connect(self.gamesdb.path)
		db.execute('''CREATE TABLE IF NOT EXISTS ''' + self.system + '''
				          (
				            id INTEGER PRIMARY KEY,
				            path TEXT
				          )''')
		db.commit()
		db.close()
	
	def get_game_info(self, id):
		'''Return a GameInfo object representing the game or None if an error occured.'''
		db = sqlite3.connect(self.gamesdb.path)
		c = db.cursor()
		c.execute('SELECT megadrive.id, megadrive.path, games.time_played, games.last_played FROM games, megadrive WHERE games.gameid = megadrive.id AND megadrive.id = ?', [id])
		result = c.fetchone()
		db.close()
		info = None
		
		if result:
			path = result[1]
			info = GamesManager.GameInfo()
			info.set_property("id", id)
			info.set_property("title", self.gamesdb.tosec.get_game_title(path))
			info.set_property("cover", self.gamesdb.app.iconsdir + "/" + self.system + ".png")
			info.set_property("system", self.system)
			info.set_property("played", result[2])
			info.set_property("playedlast", result[3])
		
		return info
	
	def update_db(self):
		db = sqlite3.connect(self.gamesdb.path)
		for rom in self.get_roms():
			id = None
			for row in db.execute('SELECT id FROM ' + self.system + ' WHERE path = ?', [rom]):
				id = row[0]
			
			# Search in the games table
			if not id:
				db.execute('INSERT INTO ' + self.system + ' VALUES (NULL, ?)', [rom])
				for row in db.execute('SELECT id FROM ' + self.system + ' WHERE path = ?', [rom]):
					id = row[0]
				
				db.execute('INSERT INTO games VALUES (NULL, ?, ?, 0, 0)', [id, self.system])
		db.commit()
		db.close
	
	def get_roms(self):
		roms = []
		for root, dirs, files in walk(path.expanduser("~")):
			for file in files:
				file = path.join(root, file)
				if self.is_rom(file):
					roms.append(file)
		return roms
	
	def is_rom(self, file):
		return has_suffix(file, "md")
	
	def is_game_available(self, id):
		return True
		db = sqlite3.connect(self.gamesdb.path)
		exists = False
		for row in db.execute('SELECT path FROM megadrive WHERE id = ?', [id]):
			exists = path.exists(row[0])
			break
		db.close()
		return exists
	
	def get_game_exec(self, id):
		return ""
