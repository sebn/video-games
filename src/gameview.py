#!/usr/bin/python3
#    gameview.py A Widget 
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
from gi.repository import Gd, GamesManager
import time

from threading import Thread

class MainGameView(Gtk.Box):
	def __init__(self, app):
		Gtk.Box.__init__(self, orientation = Gtk.Orientation.VERTICAL)
		
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
		
		self.gameview = None
		
		self.toolbar = Gd.MainToolbar()
		#self.toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR);
		self.toolbar.get_style_context().add_class(Gtk.STYLE_CLASS_MENUBAR);
		self.toolbar.set_show_modes(False)
		self.toolbar.show_all()
		
		# Add the "go previous" icon
		
		iconname = None
		if self.toolbar.get_direction() == Gtk.TextDirection.RTL:
			iconname = 'go-next-symbolic'
		else:
			iconname = 'go-previous-symbolic'
		self.previous_button = self.toolbar.add_button(iconname, "Previous", True)
		self.previous_button.connect('clicked', self.on_previous_button_clicked)
		
		# Add the "add games" icon
		
		iconname = 'list-add-symbolic'
		self.add_games_button = self.toolbar.add_button(iconname, "Add games", True)
		self.add_games_button.connect('clicked', self.on_add_games_button_clicked)
		
		# Add the "start game" icon
		
		iconname = 'media-playback-start-symbolic'
		self.play_game_button = self.toolbar.add_button(iconname, "Play the game", True)
		self.play_game_button.connect('clicked', self.on_play_game_button_clicked)
		
		self.view = Gd.MainView()
		self.view.connect('item-activated', self.on_item_activated)
	#	self.view.connect('selection-mode-request', Lang.bind(this, this._onSelectionModeRequest));
	#	self.view.connect('view-selection-changed', Lang.bind(this, this._onViewSelectionChanged));
		self.view.set_model(self.model)
		
		self.pack_start(self.toolbar, False, True, 0)
		self.pack_start(self.view, True, True, 0)
		
		self.app.settings.connect('changed::view-as', self.set_view)
		
		self.set_view()
		self.show_game_list()
		
		self.populate_async()
	
	def has_game(self, id):
		# Beware of concurrent threads manipulating the same game simulteanously
		for game in self.model:
			if int(id) == int(game[0]):
				return True
		return False
	
	def add_game(self, id):
		if (not self.has_game(id)) and self.app.gamesdb.query_is_game_available(id):
			info = self.app.gamesdb.get_game_info(id)
			if not info:
				info = GamesManager.GameInfo()
			title = info.get_property("title")
			developer = info.get_property("developer")
			icon = info.get_pixbuf(128, 0)
			Gdk.threads_enter()
			self.view.get_model().append([str(id), "", title, developer, icon, int(time.time()), False])
			Gdk.threads_leave()
	
	def set_view(self, settings=None, setting=None):
		value = self.app.settings.get_value('view-as').get_string()
		if value == 'icon':
			self.view.set_view_type(0)
		elif value == 'list':
			self.view.set_view_type(1)
		
	
	def populate(self):
		for id in self.app.gamesdb.get_games_id():
			self.add_game(id)
	
	def populate_async(self):
		Thread(target=self.populate, args=(), kwargs={}).start()
	
	def on_item_activated(self, view, itemid, itemindex):
		self.show_game(itemid)
	
	def on_previous_button_clicked(self, button):
		self.show_game_list()
	
	def on_add_games_button_clicked(self, button):
		self.show_game_list()
	
	def on_play_game_button_clicked(self, button):
		self.app.play_game()
	
	def on_game_updated(self, application, id):
		# Get the relative entry in the model
		iter = None
		
		#Gdk.threads_enter ()
		for game in self.model:
			if int(game[0]) == int(id):
				iter = game.iter
				break
		#Gdk.threads_leave ()
		
		# It is extremly important to use Gdk.threads_enter() and
		# Gdk.threads_leave() : it allows to synchronise the Gdk (Gtk)
		# thread with any thread calling it.
		# Every signal handling function (or method) should use them.
		
		if iter:
			info = self.app.gamesdb.get_game_info(id)
			Gdk.threads_enter()
			self.model.set_value(iter, 2, info.get_property("title"))
			self.model.set_value(iter, 3, info.get_property("developer"))
			self.model.set_value(iter, 4, info.get_pixbuf(128, 0))
			self.model.set_value(iter, 5, int(time.time()))
			Gdk.threads_leave()
		else:
			self.add_game(id)
	
	def show_game_list(self):
		self.app.focus_game(None)
		
		# Hide
		
		self.toolbar.set_labels(None, None)
		if self.gameview:
			self.gameview.hide()
		self.previous_button.hide()
		self.play_game_button.hide()
		
		#Show
		
		self.view.show()
		self.add_games_button.show()
	
	def show_game(self, id):
		id = int(id)
		self.app.focus_game(id)
		#try:
		#	Thread(target=self.app.gamesdb.download_game_metadata, args=(self.app.focused_game, ),).start()
		#except:
		#	print("Can't download metadata.")
		
		# Show
		info = self.app.gamesdb.get_game_info(id)
		self.toolbar.set_labels(info.get_property("title"), None)
		if self.gameview:
			self.gameview.set_game(id)
		else:
			self.gameview = GameView(self.app, id)
			self.pack_end(self.gameview, True, True, 0)
		self.gameview.show()
		self.previous_button.show()
		self.play_game_button.show()
		
		# Hide
		
		self.view.hide()
		self.add_games_button.hide()

class GameView(Gtk.ScrolledWindow):
	def __init__(self, app, id):
		Gtk.ScrolledWindow.__init__(self)
		self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		#context = self.get_style_context()
		#context.add_class("documents-scrolledwin")
		
		self.app = app
		self.app.gamesdb.connect('game_updated', self.on_game_updated)
		
		self.cover_size = 256
		
		# Set the primary informations
		
		self.primary_info = Gtk.Grid()
		self.primary_info.set_orientation(Gtk.Orientation.VERTICAL)
		self.primary_info.set_halign(Gtk.Align.CENTER)
		self.primary_info.set_row_spacing(6)
		self.primary_info.set_column_spacing(24)
		self.primary_info.set_margin_top(12)
		self.primary_info.set_margin_left(24)
		self.primary_info.set_margin_right(24)
		self.primary_info.set_margin_bottom(12)
		
		self.cover = Gtk.Image()
		self.cover.set_size_request(self.cover_size, self.cover_size)
		
		self.title = Gtk.Label("")
		self.title.set_markup("<span size='large'>Title</span>")
		
		self.developer = Gtk.Label("")
		self.developer.get_style_context().add_class('dim-label')
		self.developer.set_markup("<span size='large'>Developer Inc.</span>")
		
		self.primary_info.add(self.cover)
		self.primary_info.add(self.title)
		self.primary_info.add(self.developer)
		
		self.primary_info.show_all()
		
		# Set the secondary informations
		
		self.secondary_info = Gtk.Grid ()
		self.secondary_info.set_orientation(Gtk.Orientation.VERTICAL)
		self.secondary_info.set_row_homogeneous(False)
		self.secondary_info.set_column_homogeneous(True)
		self.secondary_info.set_halign(Gtk.Align.CENTER)
		self.secondary_info.set_row_spacing(6)
		self.secondary_info.set_column_spacing(24)
		self.secondary_info.set_margin_top(12)
		self.secondary_info.set_margin_left(24)
		self.secondary_info.set_margin_right(24)
		self.secondary_info.set_margin_bottom(12)
		
		self._release_year = Gtk.Label("Released")
		self._release_year.set_halign(Gtk.Align.END)
		self._release_year.get_style_context().add_class('dim-label')
		
		self._system = Gtk.Label("System")
		self._system.set_halign(Gtk.Align.END)
		self._system.get_style_context().add_class('dim-label')
		
		self._genre = Gtk.Label("Genre")
		self._genre.set_halign(Gtk.Align.END)
		self._genre.get_style_context().add_class('dim-label')
		
		self._time_played = Gtk.Label("Played")
		self._time_played.set_halign(Gtk.Align.END)
		self._time_played.get_style_context().add_class('dim-label')
		
		self._last_played = Gtk.Label("Last played")
		self._last_played.set_halign(Gtk.Align.END)
		self._last_played.get_style_context().add_class('dim-label')
		
		self._players = Gtk.Label("Players")
		self._players.set_halign(Gtk.Align.END)
		self._players.get_style_context().add_class('dim-label')
		
		self._online = Gtk.Label("Online")
		self._online.set_halign(Gtk.Align.END)
		self._online.get_style_context().add_class('dim-label')
		
		self.release_year = Gtk.Label("")
		self.release_year.set_halign(Gtk.Align.START)
		
		self.system = Gtk.Label("")
		self.system.set_halign(Gtk.Align.START)
		
		self.genre = Gtk.Label("")
		self.genre.set_halign(Gtk.Align.START)
		
		self.time_played = Gtk.Label("")
		self.time_played.set_halign(Gtk.Align.START)
		
		self.last_played = Gtk.Label("")
		self.last_played.set_halign(Gtk.Align.START)
		
		self.players = Gtk.Label("")
		self.players.set_halign(Gtk.Align.START)
		
		self.online = Gtk.Label("")
		self.online.set_halign(Gtk.Align.START)
		
		self.secondary_info.add(self._release_year)
		self.secondary_info.add(self._system)
		self.secondary_info.add(self._genre)
		self.secondary_info.add(self._time_played)
		self.secondary_info.add(self._last_played)
		self.secondary_info.add(self._players)
		self.secondary_info.add(self._online)
		self.secondary_info.attach_next_to(self.release_year, self._release_year, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.attach_next_to(self.system, self._system, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.attach_next_to(self.genre, self._genre, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.attach_next_to(self.time_played, self._time_played, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.attach_next_to(self.last_played, self._last_played, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.attach_next_to(self.players, self._players, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.attach_next_to(self.online, self._online, Gtk.PositionType.RIGHT, 1, 1)
		self.secondary_info.show_all()
		
		# Set the screenshots
		
		self.screenshots_info = Gtk.Box()
		self.screenshots_info.set_orientation(Gtk.Orientation.VERTICAL)
		self.screenshots_info.set_spacing(12)
		self.screenshots_info.set_margin_top(12)
		self.screenshots_info.set_margin_left(24)
		self.screenshots_info.set_margin_right(24)
		self.screenshots_info.set_margin_bottom(12)
		
		self.screenshots = Gtk.Label("No screenshots")
		
		self.screenshots_info.pack_start(self.screenshots, True, True, 0)
		self.screenshots_info.show_all()
		
		# Set the game description
		self.description_info = Gtk.Box()
		self.description_info.set_orientation(Gtk.Orientation.VERTICAL)
		self.description_info.set_spacing(12)
		self.description_info.set_margin_top(12)
		self.description_info.set_margin_left(24)
		self.description_info.set_margin_right(24)
		self.description_info.set_margin_bottom(12)
		
		self._description = Gtk.Label("")
		self._description.set_markup("<span size='large'>Description</span>")
		self._description.get_style_context().add_class('dim-label')
		self._description.set_halign(Gtk.Align.START)
		
		self.description = Gtk.Label("")
		self.description.set_line_wrap(True)
		self.description.set_justify(Gtk.Justification.FILL)
		
		self.more_info = Gtk.Button("Get more information")
		
		self.description_info.pack_start(self._description, False, False, 0)
		self.description_info.pack_start(self.description, True, True, 0)
		self.description_info.pack_start(self.more_info, False, False, 0)
		self.description_info.show_all()
		
		# Set the main grid
		self.grid = Gtk.Grid()
		self.grid.set_orientation(Gtk.Orientation.VERTICAL)
		self.grid.set_row_homogeneous(False)
		self.grid.set_column_homogeneous(False)
		self.grid.set_halign(Gtk.Align.CENTER)
		self.grid.set_row_spacing(12)
		self.grid.set_column_spacing(24)
		self.grid.set_margin_top(24)
		self.grid.set_margin_left(48)
		self.grid.set_margin_right(48)
		self.grid.set_margin_bottom(24)
		
		self.lbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.lbox.set_size_request(256, -1)
		self.lbox.pack_end(Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL), True, True, 0)
		self.lbox.show_all()
		self.lbox.pack_start(self.primary_info, False, False, 0)
		self.lbox.pack_start(self.secondary_info, False, False, 0)
		
		self.rbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
		self.rbox.set_size_request(480, -1)
		self.rbox.pack_end(Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL), True, True, 0)
		self.rbox.show_all()
		self.rbox.pack_start(self.screenshots_info, False, False, 0)
		self.rbox.pack_start(self.description_info, False, False, 0)
		
		self.grid.add(self.lbox)
		#self.grid.add(self.secondary_info)
		self.grid.attach_next_to(self.rbox, self.lbox, Gtk.PositionType.RIGHT, 1, 1)
		#self.grid.attach_next_to(self.description_info, self.secondary_info, Gtk.PositionType.RIGHT, 1, 1)
		self.grid.show()
		
		self.add_with_viewport(self.grid)
		self.show()
		
		self.set_game(id)
	
	def set_game(self, id):
		self.id = int(id)
		self._set_informations_from_game()
	
	def on_game_updated(self, application, id):
		if self.app.focused_game and int(self.app.focused_game) == int(id):
			self._set_informations_from_game()
	
	def _set_informations_from_game(self):
		info = self.app.gamesdb.get_game_info(self.app.focused_game)
		
		#Gdk.threads_enter ()
		
		# Set the title
		title = info.get_property("title") if info.get_property("title") else "Unknown title"
		self.title.set_markup("<span size='large'>" + title + "</span>")
		
		# Set the developer
		developer = info.get_property("developer") if info.get_property("developer") else "Unknown developer"
		self.developer.set_markup("<span size='large'>" + developer + "</span>")
		
		# Set the cover
		icon = info.get_pixbuf(self.cover_size, 0)
		self.cover.set_from_pixbuf(icon)
		
		# Set the release year
		if info.get_property("released"):
			self._release_year.show()
			self.release_year.show()
			self.release_year.set_text(info.get_property("released"))
		else:
			self._release_year.hide()
			self.release_year.hide()
		
		# Set the system
		if info.get_property("system"):
			self._system.show()
			self.system.show()
			self.system.set_text(info.get_property("system").get_name())
		else:
			self._system.hide()
			self.system.hide()
		
		# Set the genre
		if info.get_property("genre"):
			self._genre.show()
			self.genre.show()
			self.genre.set_text(info.get_property("genre"))
		else:
			self._genre.hide()
			self.genre.hide()
		
		# Set the play informations
		if info.get_property("played") > 0:
			# Get the time played
			s = int(info.get_property("played"))
			
			d = s // 86400
			h = (s // 3600) % 24
			m = (s // 60) % 60
			s = s % 60
			
			if d != 0:
				time_played = str(d) + "d " + str(h) + "h "
			elif h != 0:
				time_played = str(h) + "h " + str(m) + "m "
			elif m != 0:
				time_played = str(m) + "m " + str(s) + "s"
			else:
				time_played = str(s) + "s"
			
			# If the last play day is the current day, display the play time, else display the date
			current_time = time.localtime()
			last_time = time.localtime(int(info.get_property("playedlast")))
			played_today = current_time[:3] == last_time[:3]
			if played_today:
				last_played = time.strftime("%H:%M:%S", last_time)
			else:
				last_played = time.strftime("%d %b %Y", last_time)
			
			self._time_played.show()
			self.time_played.show()
			self._last_played.show()
			self.last_played.show()
			self.time_played.set_text(time_played)
			self.last_played.set_text(last_played)
		else:
			self._time_played.show()
			self.time_played.show()
			self._last_played.hide()
			self.last_played.hide()
			self.time_played.set_text("Never")
		
		# Set the players number
		if info.get_property("players"):
			self._players.show()
			self.players.show()
			self.players.set_text(info.get_property("players"))
		else:
			self._players.hide()
			self.players.hide()
		
		# Set the online mode
		if info.get_property("online"):
			self._online.show()
			self.online.show()
			self.online.set_text(info.get_property("online"))
		else:
			self._online.hide()
			self.online.hide()
		
		# Set description
		if info.get_property("description"):
			self._description.show()
			self.description.show()
			self.description.set_text(info.get_property("description"))
		else:
			self._description.hide()
			self.description.hide()
		
		#Gdk.threads_leave ()
