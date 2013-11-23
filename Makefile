# See http://www.gnu.org/prep/standards/html_node/Directory-Variables.html for informations about the variables.
prefix = /usr/local

# Generally, $(exec_prefix) is used for directories that contain machine-specific files (such as executables and subroutine libraries), while $(prefix) is used directly for other directories.
exec_prefix = $(prefix)

# Executable programs that users can run.
bindir = $(prefix)/bin

# Executable programs to be run by other programs rather than by users. Usually installed in $(libexecdir)/package-name
libexecdir = $(exec_prefix)/libexec

# Root of the directory tree for read-only architecture-independent data files.
datarootdir = $(prefix)/share

datadir = $(datarootdir)

# Sources
APPNAME = badnik
DATADIR = $(datadir)/$(APPNAME)
DESKTOP = data/badnik.desktop
DESKTOPDIR = $(datadir)/applications
SOURCES = \
	src/__init__.py \
	src/badnik.py \
	src/badniklibrary.py \
	src/badnikwindow.py \
	src/gameview.py \
	src/main.py \
	src/metadata/__init__.py \
	src/metadata/mobygames.py \
	src/systems/__init__.py \
	src/systems/desktop.py \
	src/systems/utils.py \
	src/ressources/app-menu.ui

ICONS = \
	icons/hicolor/16x16/apps/$(APPNAME).png \
	icons/hicolor/22x22/apps/$(APPNAME).png \
	icons/hicolor/24x24/apps/$(APPNAME).png \
	icons/hicolor/32x32/apps/$(APPNAME).png \
	icons/hicolor/48x48/apps/$(APPNAME).png \
	icons/hicolor/256x256/apps/$(APPNAME).png

TOSEC = \
#	data/tosec/megadrive.dat \
#	data/tosec/snes.dat

SYSTEMICONS = \
#	data/icons/megadrive.png \
#	data/icons/snes.png

SRCDIR = $(DATADIR)/src

# Specific variables
schemadir = data/schemas
schemas = org.gnome.badnik.gschema.xml

schemainstalldir = $(datadir)/glib-2.0/schemas
installedschemas = $(schemas:%=$(schemainstalldir)/%)

bin = $(bindir)/$(APPNAME)
desktop = $(datadir)/applications/$(APPNAME).desktop
sources = $(SOURCES:%=$(DATADIR)/%)
icons = $(ICONS:%=$(datadir)/%)
icontheme = $(datadir)/icons/hicolor/index.theme
systemicons = $(SYSTEMICONS:%=$(DATADIR)/%)
tosec = $(TOSEC:%=$(DATADIR)/%)

all:

install: $(desktop)

$(desktop): $(DESKTOP) $(bin) $(icontheme)
	mkdir -p $(DESKTOPDIR)
	cp -f $< $(@D)
	chmod +x $@

$(bin): $(installedschemas) $(sources) $(tosec)
	ln -fs $(SRCDIR)/main.py $@
	chmod +x $(SRCDIR)/main.py
	chmod +x $@

$(installedschemas): $(schemainstalldir)/%.gschema.xml: $(schemadir)/%.gschema.xml
	mkdir -p $(schemainstalldir)
	cp -fR $< $(@D)
	glib-compile-schemas $(@D)

$(sources): $(DATADIR)/%: % $(systemicons)
	mkdir -p $(@D)
	cp -f $< $(@D)

$(systemicons): $(DATADIR)/%: %
	mkdir -p $(@D)
	cp -f $< $(@D)

$(icontheme): $(icons)
	if ! [ -f $@ ]; then mkdir -p $(@D); cp -f /usr/share/icons/hicolor/index.theme $(@D); fi;
	gtk-update-icon-cache -f $(@D)

$(icons): $(datadir)/%: %
	mkdir -p $(@D)
	cp -f $< $(@D)

$(tosec): $(DATADIR)/%: %
	mkdir -p $(@D)
	cp -f $< $(@D)

PHONY: all install
