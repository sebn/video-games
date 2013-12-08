#!/usr/bin/python3
#    gameview.py, display a game .
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

class GameView(Gtk.ScrolledWindow):
	def __init__(self):
		Gtk.ScrolledWindow.__init__(self)
		self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
		#context = self.get_style_context()
		#context.add_class("documents-scrolledwin")
		
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
		
		self.game = None
		self.playinfo = None
	
	def set_game(self, game, playinfo = None):
		self.game = game
		self.playinfo = playinfo
		
		playinfo.connect('updated', self.on_playinfo_updated)
		self._set_informations_from_game()
	
	def on_playinfo_updated (self, playinfo):
		self._set_informations_from_game ()
	
	def _set_informations_from_game(self):
		print ("gameview: getting info for", self.game.get_reference ())
		info = self.game.get_info()
		print ("gameview: got info for", self.game.get_reference ())
		#Gdk.threads_enter ()
		
		# Set the title
		
		title = info.get_property("title") if info.get_property("title") else "Unknown title"
		f_title = "<span size='large'>" + title + "</span>"
		self.title.set_markup(f_title)
		print ("gameview: title for", self.game.get_reference (), f_title)
		
		# Set the developers
		developer = info.get_developers ()
		if len (developer) > 0:
			developer = ", ".join (developer)
		else:
			developer = "Unknown developer"
		self.developer.set_markup("<span size='large'>" + developer + "</span>")
		
		# Set the cover
		icon = GameInfo(info).get_pixbuf(self.cover_size, 0)
		self.cover.set_from_pixbuf(icon)
		
		# Set the release date
		date = info.get_property("release_date")
		if date:
			year = str (date.get_year ())
			month = str (int (date.get_month ()))
			day = str (date.get_day ())
			
			self._release_year.show()
			self.release_year.show()
			self.release_year.set_text("/".join ((day, month, year)))
		else:
			self._release_year.hide()
			self.release_year.hide()
		
		# Set the system
		if info.get_property("system_name"):
			self._system.show()
			self.system.show()
			self.system.set_text(info.get_property("system_name"))
		else:
			self._system.hide()
			self.system.hide()
		
		# Set the genre
		genre = info.get_genres ()
		if len (genre) > 0:
			self._genre.show()
			self.genre.show()
			genre = ", ".join (genre)
			self.genre.set_text(genre)
		else:
			self._genre.hide()
			self.genre.hide()
			developer = "Unknown developer"
		
		# Set the play informations
		if self.game and self.playinfo:
			s = self.playinfo.get_play_duration ()
			last_time = self.playinfo.get_last_play_time ()
			
			if s > 0:
				# Get the time played
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
				last_time = time.localtime(last_time)
				
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
		else:
			self._time_played.show()
			self.time_played.show()
			self._last_played.hide()
			self.last_played.hide()
			self.time_played.set_text("Never")
		
		# Set the players number
		players = info.get_property("players")
		if players:
			self._players.show()
			self.players.show()
			min_players = players.get_lower_endpoint ()
			max_players = players.get_upper_endpoint ()
			if min_players == max_players:
				self.players.set_text(str(min_players))
			else:
				self.players.set_text(str(min_players) + '-' + str(max_players))
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

