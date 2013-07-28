#!/usr/bin/python3
#    snes.py Managing the Super Nintento Entertainment System / Super Famicom system.
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

from gamesman.systems.tosecsystem import TOSECSystem

class SNES(TOSECSystem):
	def __init__(self, gamesdb):
		TOSECSystem.__init__(self, gamesdb, "snes")
		gamesdb.db.execute('''CREATE TABLE IF NOT EXISTS ''' + self.system + '''
				          (
				            id INTEGER PRIMARY KEY,
				            path TEXT
				          )''')
	
	def update_db(self):
		for rom in self.get_roms():
			id = None
			for row in self.gamesdb.db.execute('SELECT id FROM ' + self.system + ' WHERE path = ?', [rom]):
				id = row[0]
			
			# Search in the games table
			if not id:
				self.gamesdb.db.execute('INSERT INTO ' + self.system + ' VALUES (NULL, ?)', [rom])
				for row in self.gamesdb.db.execute('SELECT id FROM ' + self.system + ' WHERE path = ?', [rom]):
					id = row[0]
				
				self.gamesdb.db.execute('INSERT INTO games VALUES (NULL, ?, ?, 0, 0)', [id, self.system])
		self.gamesdb.db.commit()
	
	def get_roms(self):
		roms = []
		for root, dirs, files in walk("/home/kekun/Jeux"):
			for file in files:
				file = path.join(root, file)
				if self.is_rom(file):
					roms.append(file)
		return roms
	
	def is_rom(self, file):
		return has_suffix(file, "sfc")
