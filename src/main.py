#!/usr/bin/python3
#    main.py A Python module to launch Badnik with the required environment.
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

import os, sys

try:
	from gi.repository import Gtk
	gtk_version = (Gtk.get_major_version(), Gtk.get_minor_version(), Gtk.get_micro_version())
	gtk_version_required = (3, 8, 0)
	assert gtk_version >= gtk_version_required
except:
	sys.stderr.write("GTK+ version requirement not met.")
	sys.stderr.write("GTK+ 3.8.0 or greater is required.")
	sys.exit(1)

execdir = os.path.dirname(os.path.realpath(sys.argv[0]))
path = execdir + "/badnik.py"
args = sys.argv[1:]
env = os.environ
env["LD_LIBRARY_PATH"] = "/usr/lib64/gnome-documents/"
env["GI_TYPELIB_PATH"] = "/usr/lib64/gnome-documents/girepository-1.0/"

os.execve(path, args, env)

