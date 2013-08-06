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
from systems.utils import has_suffix

from gi.repository import GamesManager

from systems.tosecsystem import TOSECSystem
import sqlite3

class MegaDrive(TOSECSystem):
	def __init__(self, gamesdb):
		TOSECSystem.__init__(self, gamesdb, "megadrive")
	
	def do_get_game_info(self, library, id):
		info = GamesManager.System._get_game_info(self, id)
		
		uri = self.get_game_uri(id)
		
		info.set_property("title", library.tosec.get_game_title(uri))
		info.set_property("cover", library.app.iconsdir + "/" + self.get_property("reference") + ".png")
		
		return info
	
	def do_get_game_reference_for_uri(self, library, uri):
		return library.tosec.get_game_title(uri)
	
	def do_search_new_games(self):
		print("update megadrive start")
		for rom in self.get_roms():
			self.add_new_game(rom)
		
		print("update megadrive end")
		#self.update_games_metadata()
	
	def get_roms(self):
		roms = []
		for root, dirs, files in walk(path.expanduser("~")):
			for file in files:
				file = path.join(root, file)
				if self.is_a_game(file):
					roms.append(file)
		return roms
	
	def do_is_a_game(self, uri):
		return has_suffix(uri, "md")
	
	def do_is_game_available(self, library, id):
		db = sqlite3.connect(library.path)
		exists = False
		for row in db.execute('SELECT uri FROM uris WHERE gameid = ?', [id]):
			exists = path.exists(row[0])
			break
		db.close()
		return exists
	
	def do_get_game_exec(self, library, id):
		return 'gens --game "' + self.get_game_uri(id) + '"'
