#!/usr/bin/python3
#    tosec.py Managing a video game library.
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

from gi.repository import GObject
import sqlite3
import os.path

from gamesman.metadata import tosec
from gamesman.systems import desktop
from gamesman.systems import megadrive
from gamesman.systems import snes

class GamesDB(GObject.Object):
	'''A games dedicated database'''
	__gsignals__ = {
		'game_updated': (GObject.SIGNAL_RUN_FIRST, None, (int,))
	}
	
	def __init__(self, app):
		GObject.Object.__init__(self)
		self.app = app
		self.path = os.path.join(self.app.savedatadir, "games.db")
		
		# Init the games database
		db = sqlite3.connect(self.path)
		db.execute('''CREATE TABLE IF NOT EXISTS games
		              (
		                id INTEGER PRIMARY KEY,
		                gameid INTEGER,
		                system TEXT,
		                time_played REAL,
		                last_played REAL,
		                UNIQUE (id, system)
		              )''')
		db.close()
		
		# Init the TOSEC databases
		self.tosec = tosec.TOSEC(self.app.savedatadir)
		
		# Init the system related databases
		system_list = []
		system_list.append(desktop.Desktop(self))
		#system_list.append(snes.SNES(self))
		system_list.append(megadrive.MegaDrive(self))
		
		self.systems = {}
		for system in system_list:
			self.systems[system.system] = system
	
	def get_specialized_game_id(self, id):
		'''Return a tuple containing the specialized game ID and the relative system'''
		db = sqlite3.connect(self.path)
		value = None
		id = str(id)
		for row in db.execute('SELECT gameid, system FROM games WHERE id = ?', [id]):
			value = row
		db.close()
		return value
	
	def is_game_available(self, id):
		id = str(id)
		gameid, system = self.get_specialized_game_id(id)
		return self.systems[system].is_game_available(gameid)
		
	def get_game_exec(self, id):
		id = str(id)
		gameid, system = self.get_specialized_game_id(id)
		return self.systems[system].get_game_exec(gameid)
	
	def get_game_info(self, id):
		id = str(id)
		gameid, system = self.get_specialized_game_id(id)
		return self.systems[system].get_game_info(gameid)
	
	def update_play_time(self, id, start, end):
		played = end - start
		
		db = sqlite3.connect(self.path)
		c = db.cursor()
		c.execute('SELECT time_played FROM games WHERE id = ?', [id])
		result = c.fetchone()
		
		if result:
			played += result[0]
		
		db.execute('UPDATE games SET time_played = ? WHERE id = ?', [played, id])
		db.execute('UPDATE games SET last_played = ? WHERE id = ?', [end, id])
		db.commit()
		db.close()
		
		self.emit('game_updated', int(id))
	
	def search_new_games(self):
		print("update db")
		for key in self.systems.keys():
			self.systems[key].update_db()
	
	def search_game(self, id, system):
		db = sqlite3.connect(self.path)
		value = None
		id = str(id)
		result = db.execute('SELECT * FROM games WHERE id = ? AND system = ? ORDER BY id, system', [id, system])
		for row in result:
			value = row
		db.close()
		return value
	
	def get_games(self):
		db = sqlite3.connect(self.path)
		result = list(db.execute('SELECT id, gameid, system FROM games'))
		db.close()
		return result
