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

from gi.repository import GamesManager

from gamesman.metadata import tosec
from gamesman.systems import desktop
from gamesman.systems import megadrive
from gamesman.systems import snes

class BadnikLibrary(GamesManager.Library):
	'''A games dedicated database'''
	def __init__(self, app):
		GamesManager.Library.__init__(self, db_name = "games2", db_dir = app.savedatadir)
		
		self.app = app
		self.path = os.path.join(self.app.savedatadir, "games2.db")
		
		# Init the TOSEC databases
		self.tosec = tosec.TOSEC(self.app.savedatadir)
		
		# Init the system related databases
		system_list = []
		system_list.append(desktop.Desktop(self))
		#system_list.append(snes.SNES(self))
		system_list.append(megadrive.MegaDrive(self))
		
		for system in system_list:
			self.add_system(system)
