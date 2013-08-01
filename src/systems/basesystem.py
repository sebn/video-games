#!/usr/bin/python3
#    basesystem.py A Python module reprenting the base abstract system.
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

import abc

from gi.repository import GamesManager

class BaseSystem(GamesManager.System):
	def __init__(self, gamesdb, system):
		GamesManager.System.__init__(self, id = system)
		self.system = system
		self.gamesdb = gamesdb
	
	@abc.abstractmethod
	def update_db(self):
		pass
		
	def do_get_game_exec(self, id):
		return self.get_game_exec(id)
		
	def do_is_game_available(self, id):
		return self.is_game_available(id)
	
	def do_search_new_games(self):
		self.update_db()
	
	@abc.abstractmethod
	def get_game_info(self, id):
		return None
	
	@abc.abstractmethod
	def is_game_available(self, id):
		return False
	
