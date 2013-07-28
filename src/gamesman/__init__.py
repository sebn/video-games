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
### GameInfo
###

class GameInfo:
	'''An object containing informations about a game a the time of its creation.'''
	def __init__(self):
		'''Internationalization uses the same system as Freedesktop, looking for : Key[lang_COUNTRY], then Key[lang] and defaulting to Key.'''
		self.id = None
		self.title = None
		self.developer = None
		self.icon = None # The icon name
		self.cover = None # The path to the cover
		self.released = None
		self.system = None
		self.genre = None
		self.played = None
		self.playedlast = None
		self.online = None
		self.description = None
		self.rank = None
		self.players = None
	
	def get_pixbuf(self, size, flag):
		'''Return a pixbuf representing the game (a cover or an icon) or None if it wasn't able to load one.
		   size :  the desired icon size
		   flags : the flags modifying the behavior of the icon lookup
		   gtk.ICON_LOOKUP_NO_SVG : Never return Scalable Vector Graphics (SVG) icons, even if gdk-pixbuf supports them. Cannot be used together with gtk.ICON_LOOKUP_FORCE_SVG.
		   gtk.ICON_LOOKUP_FORCE_SVG : Return SVG icons, even if gdk-pixbuf doesn't support them. Cannot be used together with gtk.ICON_LOOKUP_NO_SVG.
		   gtk.ICON_LOOKUP_USE_BUILTIN : When passed to the lookup_icon() method includes builtin icons as well as files. For a builtin icon, the gtk.IconInfo.get_filename() method returns None and you need to call the get_builtin_pixbuf() method.
		'''
		
		'''Try to load and return the cover.'''
		if self.cover:
			try:
				pixbuf = Pixbuf.new_from_file_at_scale(self.cover, size, size, True)
				return pixbuf
			except:
				pass
		
		icon_theme = IconTheme.get_default()
		
		'''Try to load and return the icon.'''
		
		if self.icon:
			icon = self.icon.split('.')[0]
			icon_info = icon_theme.lookup_icon(icon, size, flag)
			if icon_info:
				try:
					filename = icon_info.get_filename()
					pixbuf = Pixbuf.new_from_file_at_scale(filename, size, size, True)
					return pixbuf
				except:
					pass
		
		return None

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
	
