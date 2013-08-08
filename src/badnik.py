#!/usr/bin/python3
#    badnik.py A Python module to use TOSEC data files as a SQLite database.
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

from gi.repository import Gtk, Gdk, GLib, Gio
import sys, os
from threading import Thread
from xdg import BaseDirectory

from badnikwindow import BadnikWindow
from badniklibrary import BadnikLibrary

class BadnikApplication(Gtk.Application):
	def __init__(self):
		Gtk.Application.__init__(self, application_id = 'org.gnome.badnik', flags = Gio.ApplicationFlags.FLAGS_NONE)
		GLib.threads_init()
		Gdk.threads_init()
		
		self.simplename = "badnik"
		self.fullname = "Badnik"
		
		self.datadir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
		self.savedatadir = BaseDirectory.save_data_path(self.simplename)
		self.iconsdir = self.datadir + "/data/icons"
		self.tosecdir = self.datadir + "/data/tosec"
		self.srcdir = self.datadir + "/src"
		
		self.gamesdb = BadnikLibrary(self, self.savedatadir)
		
		self.focused_game = None
		
		self.connect("activate", self.on_activate)
		
		self.register(None)
		
		self.settings = Gio.Settings.new('org.gnome.badnik')
		
		self.builder = Gtk.Builder()
		self.builder.add_from_file(self.srcdir + "/ressources/app-menu.ui")
		self.builder.connect_signals(self)
		
		self.menumodel = self.builder.get_object("app-menu")
		self.set_app_menu(self.menumodel)
		
		self._action_entries = [ { 'name': 'quit', 'callback': self.on_quit, 'accel': '<Primary>q' },
		                         { 'name': 'about', 'callback': self.on_about },
		                         { 'name': 'help', 'callback': self.on_help, 'accel': 'F1' },
		                         { 'name': 'fullscreen', 'callback': self.on_fullscreen, 'accel': 'F11' },
		                         { 'name': 'view-as', 'callback': self.on_view_as, 'create_hook': self._view_as_create_hook,
		                           'parameter_type': 's', 'state': self.settings.get_value('view-as') },
		                         { 'name': 'add-games', 'callback': self.on_add_games }
		                       ]
		self._add_actions()
		
		settings = Gtk.Settings.get_default()
		settings.set_property("gtk-application-prefer-dark-theme", True)
		settings.set_property("gtk-shell-shows-app-menu", True)
	
	def on_activate(self, data=None):
		self.window = BadnikWindow(self)
		self.window.show()
		self.add_window(self.window)
		
		self.update_library_async()
	
	def _add_actions(self):
		for action_entry in self._action_entries:
			state = action_entry['state'] if 'state' in action_entry else None
			parameterType = GLib.VariantType.new(action_entry['parameter_type']) if 'parameter_type' in action_entry else None
			
			action = None
			if (state):
				action = Gio.SimpleAction.new_stateful(action_entry['name'], parameterType, action_entry['state'])
			else:
				action = Gio.SimpleAction.new(action_entry['name'], None)
			
			if 'create_hook' in action_entry:
				action_entry['create_hook'](action)
			
			if 'callback' in action_entry:
				action.connect('activate', action_entry['callback'])
			
			if 'accel' in action_entry:
				self.add_accelerator(action_entry['accel'], 'app.' + action_entry['name'], None)
			
			self.add_action(action)
	
	def on_quit(self, action, data):
		self.quit()
	
	def on_about(self, action, data):
		aboutdialog = Gtk.AboutDialog()
		aboutdialog.set_destroy_with_parent(True)
		aboutdialog.set_transient_for(self.window)
		aboutdialog.set_modal(True)
		
		#aboutdialog.set_artists([])
		aboutdialog.set_authors(["Adrien Plazas<kekun.plazas@laposte.net>"])
		aboutdialog.set_comments("A video game launcher")
		aboutdialog.set_copyright("Copyright © 2013 Adrien Plazas")
		#aboutdialog.set_documenters([])
		aboutdialog.set_license_type(Gtk.License.GPL_3_0)
		aboutdialog.set_logo_icon_name(self.simplename)
		aboutdialog.set_program_name(self.fullname)
		#aboutdialog.set_translator_credits()
		aboutdialog.set_version("0.1.0")
		aboutdialog.set_website("http://adrienplazas.net")
		
		def on_close(action, parameter):
			action.destroy()
		aboutdialog.connect("response", on_close)
		aboutdialog.show()
	
	def on_help(self, action, data):
		print("help")
	
	def on_fullscreen(self, action, data):
		print("fullscreen")
	
	def on_view_as(self, action, parameter):
		self.settings.set_value('view-as', parameter)
	
	def on_add_games(self, action, data):
		print("add games")
	
	def _view_as_create_hook(self, action):
		def _changed_view_as(settings, setting):
			action.state = settings.get_value('view-as')
		self.settings.connect('changed::view-as', _changed_view_as)
	
	def update_library(self):
		self.gamesdb.search_new_games(os.path.expanduser("~"))
	
	def update_library_async(self):
		Thread(target=self.update_library, args=(), kwargs={}).start()
		
	def play_game(self, id=None):
		id = id if id else self.focused_game
		if id:
			p = GameProcess(self.gamesdb, id)
			p.connect('game_started', self.on_game_started)
			p.connect('game_stopped', self.on_game_stopped)
			p.start()
	
	def focus_game(self, id):
		self.focused_game = id
	
	def on_game_started(self, process, id):
		pass
	
	def on_game_stopped(self, process, id, return_code, start_time, end_time):
		time_played = end_time - start_time
		
		if return_code == 0 or time_played > 10:
			self.gamesdb.update_game_play_time(id, start_time, end_time)

from gi.repository import GObject

import shlex, subprocess, time
from threading import Thread

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
		if self.gamesdb.query_is_game_available(self.id):
			args = shlex.split(self.gamesdb.get_game_exec(self.id))
			
			self.emit('game_started', int(self.id))
			
			start_time = time.time()
			return_code = subprocess.call(args, stdout=self.out, stderr=self.err)
			end_time = time.time()
			
			self.emit('game_stopped', int(self.id), int(return_code), int(start_time), int(end_time))

if __name__ == '__main__':
	app = BadnikApplication()
	exit_status = app.run(sys.argv)
	sys.exit(exit_status)

