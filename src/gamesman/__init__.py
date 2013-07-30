#!/usr/bin/python3
#    gamesman/__init__.py Managing games.
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

from gi.repository.GdkPixbuf import Pixbuf
from gi.repository.Gtk import IconTheme
from gi.repository import GObject, GLib

import shlex, subprocess, time
from threading import Thread

###
### GameProcess
###

class GameProcess(GObject.Object, Thread):
	'''A class representing an asynchronous game process.'''
	
	__gsignals__ = {
		'game_started': (GObject.SIGNAL_RUN_FIRST, None, (int,)),
		'game_stopped': (GObject.SIGNAL_RUN_FIRST, None, (int, int, int, int)) # Parameters are the game ID, the process's result, the start time and the end time
	}
	
	def __init__(self, gamesdb, id, out=subprocess.DEVNULL, err=subprocess.DEVNULL):
		GObject.Object.__init__(self)
		Thread.__init__(self)
		self.gamesdb = gamesdb
		self.id = id
		self.out = out
		self.err = err
	
	def run(self):
		if self.gamesdb.is_game_available(self.id):
			args = shlex.split(self.gamesdb.get_game_exec(self.id))
		
			self.emit('game_started', int(self.id))
		
			start_time = time.time()
			return_code = subprocess.call(args, stdout=self.out, stderr=self.err)
			end_time = time.time()
		
			self.emit('game_stopped', int(self.id), int(return_code), int(start_time), int(end_time))
	
