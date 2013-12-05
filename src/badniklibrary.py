#!/usr/bin/python3
#    badniklibrary.py, the library of Video Games.
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
import os.path

from gi.repository import Badnik

class BadnikLibrary(Badnik.Library):
	'''A games dedicated database'''
	def __init__(self, app, save_data_dir):
		Badnik.Library.__init__(self, db_name = "games", db_dir = save_data_dir)
		
		self.app = app
		self.path = os.path.join(save_data_dir, "games.db")

