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

from gameview import MainGameView

class BadnikWindow(Gtk.ApplicationWindow):
	def __init__(self, app):
		Gtk.Window.__init__(self, type=Gtk.WindowType.TOPLEVEL, title=app.fullname, application=app)
		self.set_wmclass ("Badnik", "Badnik")
		self.set_default_icon_name('badnik')
		self.set_hide_titlebar_when_maximized(True)
		
		self.app = app
		
		self.set_default_size(800, 600)
		self.set_position(Gtk.WindowPosition.CENTER)
		
		self.view = MainGameView(app)
		self.view.show()
		self.add(self.view)

