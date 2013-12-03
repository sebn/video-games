#!/usr/bin/python3
#    badnikwindow.py A Python module to use TOSEC data files as a SQLite database.
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


from gi.repository import Gtk

from headerbar import Headerbar
from gamelist import GameList
from gameview import GameView

class BadnikWindow(Gtk.ApplicationWindow):
	def __init__(self, app):
		Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL, title=app.fullname, application=app)
		self.set_wmclass ("Badnik", "Badnik")
		self.set_default_icon_name('badnik')
		
		self.app = app
		
		self.set_default_size(800, 600)
		self.set_position(Gtk.WindowPosition.CENTER)
		
		
		self.headerbar = Headerbar ()
		self.gamelist = GameList(app)
		self.gameview = GameView()
		
		if Gtk.get_minor_version() > 8:
			self.set_titlebar (self.headerbar)
			
			box = Gtk.Box (orientation=Gtk.Orientation.VERTICAL, spacing=0)
			box.show ()
			
			box.pack_end (self.gamelist, True, True, 0)
			box.pack_end (self.gameview, True, True, 0)
			self.add(box)
			
		else:
			box = Gtk.Box (orientation=Gtk.Orientation.VERTICAL, spacing=0)
			box.show ()
			
			box.pack_start (self.headerbar, False, False, 0)
			box.pack_end (self.gamelist, True, True, 0)
			box.pack_end (self.gameview, True, True, 0)
			self.add(box)
		
		self.headerbar.previous_button.connect('clicked', self.on_previous_clicked)
		self.headerbar.add_games_button.connect('clicked', self.on_add_games_clicked)
		self.headerbar.play_game_button.connect('clicked', self.on_play_game_clicked)
		self.gamelist.connect('game_clicked', self.on_game_clicked)
		
		self.headerbar.show ()
		
		self.set_mode ('list')
		self.show ()
	
	def on_previous_clicked(self, button):
		self.set_mode ('list')
	
	def on_add_games_clicked(self, button):
		print ("add games clicked")
	
	def on_play_game_clicked(self, button):
		print ("play game clicked")
	
	def on_game_clicked(self, view, game):
		self.gameview.set_game (game)
		self.set_mode ('game')
	
	def set_mode (self, mode):
		if mode == 'list':
			self.gamelist.show ()
			self.gameview.hide ()
			
			self.headerbar.previous_button.hide ()
			self.headerbar.add_games_button.show ()
			self.headerbar.play_game_button.hide ()
		
		elif mode == 'game':
			self.gamelist.hide ()
			self.gameview.show ()
			
			self.headerbar.previous_button.show ()
			self.headerbar.add_games_button.hide ()
			self.headerbar.play_game_button.show ()

