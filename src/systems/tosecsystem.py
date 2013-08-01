#!/usr/bin/python3
#    tosecsystem.py A Python module representing systems using the TOSEC data base.
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

from systems.basesystem import BaseSystem

class TOSECSystem(BaseSystem):
	def __init__(self, gamesdb, system):
		BaseSystem.__init__(self, gamesdb, system)
		tosecdata = gamesdb.app.tosecdir + "/" + system + ".dat"
		gamesdb.tosec.parse_file(tosecdata, self.system)
	
	def get_game_name(self, id):
		path = None
		for row in self.gamesdb.db.execute('SELECT path FROM ' + self.system + ' WHERE id = ?', [id]):
			path = row[0]
		
		if path:
			return self.gamesdb.tosec.get_game_title(path)
		else:
			return id
	
	def get_game_icon(self, id, size, flag):
		return self.gamesdb.app.iconsdir + "/" + self.system + ".png"
	
