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
from systems.utils import has_suffix, get_path_from_uri

from gi.repository import GamesManager, GLib

from systems.tosecsystem import TOSECSystem
import sqlite3

class MegaDrive(GamesManager.MegaDrive):
	def __init__(self, gamesdb):
		GamesManager.MegaDrive.__init__(self, reference = "megadrive")
		tosecdata = gamesdb.app.tosecdir + "/" + self.get_property("reference") + ".dat"
		gamesdb.tosec.parse_file(tosecdata, self.get_property("reference"))
		self.tosec = gamesdb.tosec
	
	def do_get_game_info(self, library, id):
		info = library.get_default_game_info(id)
		
		game_path = get_path_from_uri(library.get_game_uri(id))
		
		info.set_property("title", self.tosec.get_game_title(game_path))
		info.set_property("cover", library.app.iconsdir + "/" + self.get_property("reference") + ".png")
		
		return info
	
	def do_get_game_exec(self, library, id):
		game_path = get_path_from_uri(library.get_game_uri(id))
		return 'gens --fs --render-mode 2 --quickexit --enable-perfectsynchro "' + game_path + '"'
	
	def do_get_game_reference_for_uri(self, uri):
		game_path = get_path_from_uri(uri)
		return self.tosec.get_game_title(game_path)
	
	def do_download_game_metadata(self, library, game_id):
		return self.get_game_info(library, id)
	
