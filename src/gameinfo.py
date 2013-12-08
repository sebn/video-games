#!/usr/bin/python3
#    gameinfo.py, help to handle game metadata.
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

from gi.repository import Gtk, GdkPixbuf

class GameInfo:
	def __init__(self, gameinfo):
		self.gameinfo = gameinfo
		
	def get_pixbuf (self, size, flags):
		cover = self.gameinfo.get_property("cover")
		
		if cover:
			from urllib import request
			f = open('00000001.jpg','wb')
			img = request.urlopen(cover.get_front ())
			f.write(img.read())
			f.close()
			
			try:
				return GdkPixbuf.Pixbuf.new_from_file_at_size('00000001.jpg', size, size)
			except:
				pass
		
		icon_theme = Gtk.IconTheme.get_default()
		
		#Try to load and return the icon.
		if self.gameinfo.get_property("icon"):
			icon_info = icon_theme.lookup_icon(self.gameinfo.get_property("icon").split(".")[0], size, flags);
			if icon_info:
				try:
					filename = icon_info.get_filename()
					pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(filename, size, size)
					return pixbuf
				except:
					pass
		
		return None

