#!/usr/bin/python3
#    headerbar.py A Widget 
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

from gi.repository import Gtk, Gdk, GObject, GdkPixbuf, Gio
from gi.repository import Gd, Badnik

if Gtk.get_minor_version() > 8:
	class Headerbar(Gtk.HeaderBar):
		def __init__(self):
			Gtk.HeaderBar.__init__(self)
			
			previous_iconname = None
			if self.get_direction() == Gtk.TextDirection.RTL:
				previous_iconname = 'go-next-symbolic'
			else:
				previous_iconname = 'go-previous-symbolic'
			
			self.previous_button = Headerbar._get_button (previous_iconname)
			self.add_games_button = Headerbar._get_button ('list-add-symbolic')
			self.play_game_button = Headerbar._get_button ('media-playback-start-symbolic')
			
			self.pack_start (self.previous_button)
			self.pack_start (self.add_games_button)
			self.pack_start (self.play_game_button)
			
			self.set_show_close_button (True)
			
			self.show_all()
		
		def _get_button (iconname):
			image = Gtk.Image.new_from_icon_name (iconname, Gtk.IconSize.SMALL_TOOLBAR)
			return Gtk.Button (image=image)

else:
	class Headerbar(Gd.MainToolbar):
		def __init__(self):
			Gd.MainToolbar.__init__(self)
			
			previous_iconname = None
			if self.get_direction() == Gtk.TextDirection.RTL:
				previous_iconname = 'go-next-symbolic'
			else:
				previous_iconname = 'go-previous-symbolic'
			
			self.previous_button = self.add_button(previous_iconname, "Previous", True)
			self.add_games_button = self.add_button('list-add-symbolic', "Add games", True)
			self.play_game_button = self.add_button('media-playback-start-symbolic', "Play the game", True)
			
			self.get_style_context().add_class(Gtk.STYLE_CLASS_PRIMARY_TOOLBAR);
			self.set_show_modes(False)
			
			self.pack_start (self.previous_button)
			self.pack_start (self.add_games_button)
			self.pack_start (self.play_game_button)
			
			self.show_all()

