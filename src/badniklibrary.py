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
import os.path

from gi.repository import GamesManager

from metadata import tosec
from systems import desktop
from systems import megadrive
from systems import snes

class BadnikLibrary(GamesManager.Library):
	'''A games dedicated database'''
	def __init__(self, save_data_dir):
		GamesManager.Library.__init__(self, db_name = "games", db_dir = save_data_dir)
		
		#self.app = app
		self.path = os.path.join(save_data_dir, "games.db")
		
		# Init the TOSEC databases
		self.tosec = tosec.TOSEC(save_data_dir)
		
		self.add_system(desktop.Desktop(self))
		#self.add_system(snes.SNES(self))
		#self.add_system(megadrive.MegaDrive(self))

