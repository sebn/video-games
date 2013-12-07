#!/usr/bin/python3
#    gamelist.py, display a list of games.
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

from gi.repository import Gtk, Gdk, GObject, GdkPixbuf
from gi.repository import Gd, Badnik
import time

from gameinfo import GameInfo

from threading import Thread

class GameList(Gtk.Box):
	__gsignals__ = {
		'game_clicked': (GObject.SIGNAL_RUN_FIRST, None, (object,))
	}
	
	def __init__(self, app):
		Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
		
		self.games = {}
		
		self.set_size_request(640, 480)
		
		self.app = app
		self.app.gamesdb.connect('game_updated', self.on_game_updated)
		
		self.model = Gtk.ListStore(str,              # id     (game id)
		                           str,              # uri
		                           str,              # name   (game title)
		                           str,              # author (game developer)
		                           GdkPixbuf.Pixbuf, # pixbuf (game cover or icon)
		                           int,              # mtime  (last modification time in seconds)
		                           bool              # ???
		                           )
		
		self.view = Gd.MainView()
		self.view.connect('item-activated', self.on_item_activated)
	#	self.view.connect('selection-mode-request', Lang.bind(this, this._onSelectionModeRequest));
	#	self.view.connect('view-selection-changed', Lang.bind(this, this._onViewSelectionChanged));
		self.view.set_model(self.model)
		
		self.pack_start(self.view, True, True, 0)
		
		self.app.settings.connect('changed::view-as', self.set_view)
		
		self.set_view()
		self.show_game_list()
		
		self.populate_async()
	
	def has_game(self, gameref):
		# Beware of concurrent threads manipulating the same game simulteanously
		for entry in self.model:
			if gameref == entry[0]:
				print ("yes")
				return True
		return False
	
	def add_game(self, game):
		#if (not self.has_game(GameList.get_game_reference (game))) and game.query_is_available():
		if (not self.has_game(GameList.get_game_reference (game))):
			info = game.get_info()
			if not info:
				info = Badnik.GameInfo()
			
			id = GameList.get_game_reference (game)
			uri = ""
			primary_text = info.get_property("title")
			secondary_text = ", ".join (info.get_developers ())
			icon = GameInfo(info).get_pixbuf(self.get_requiered_pixbuf_size (), 0)
			mtime = int(time.time())
			selected = False
			pulse = False
			last = False
			
			entry = [id, uri, primary_text, secondary_text, icon, mtime, selected]
			
			Gdk.threads_enter()
			self.view.get_model().append(entry)
			Gdk.threads_leave()
			
			self.games[id] = game
	
	def get_game_reference (game):
		return game.get_system_reference () + ":" + game.get_reference ()
	
	def set_view(self, settings=None, setting=None):
		value = self.app.settings.get_value('view-as').get_string()
		
		if value == 'icon':
			self.view.set_view_type(0)
		elif value == 'list':
			self.view.set_view_type(1)
		
		size = self.get_requiered_pixbuf_size ()
		#Gdk.threads_enter()
		for entry in self.model:
			info = self.app.gamesdb.get_game_info(int(entry[0]))
			self.model.set_value(entry.iter, 4, info.get_pixbuf(size, 0))
		#Gdk.threads_leave()
	
	def get_requiered_pixbuf_size (self):
		value = self.app.settings.get_value('view-as').get_string()
		if value == 'icon':
			return 128
		elif value == 'list':
			return 48
		else:
			return 128
	
	def populate(self):
		for game in self.app.gamesdb.get_games (self.app.systems):
			self.add_game(game)
	
	def populate_async(self):
		Thread(target=self.populate, args=(), kwargs={}).start()
	
	def on_item_activated(self, view, itemid, itemindex):
		game = self.games[itemid]
		self.emit("game_clicked", game)
	
	def on_game_updated(self, application, gameref):
		# Get the relative entry in the model
		iter = None
		
		#Gdk.threads_enter ()
		for game in self.model:
			if game[0] == gameref:
				iter = game.iter
				break
		#Gdk.threads_leave ()
		
		# It is extremly important to use Gdk.threads_enter() and
		# Gdk.threads_leave() : it allows to synchronise the Gdk (Gtk)
		# thread with any thread calling it.
		# Every signal handling function (or method) should use them.
		
		if iter:
			info = self.app.gamesdb.get_game_info(gameref)
			Gdk.threads_enter()
			self.model.set_value(iter, 2, info.get_property("title"))
			self.model.set_value(iter, 3, info.get_property("developer"))
			self.model.set_value(iter, 4, info.get_pixbuf(self.get_requiered_pixbuf_size (), 0))
			self.model.set_value(iter, 5, int(time.time()))
			Gdk.threads_leave()
		else:
			self.add_game(gameref)
		
	def show_game_list(self):
		self.app.focus_game(None)
		self.view.show()
	
	def show_game(self, gameref):
		self.app.focus_game(gameref)

