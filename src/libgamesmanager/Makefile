# See http://www.gnu.org/prep/standards/html_node/Directory-Variables.html for informations about the variables.
prefix = /usr/local
exec_prefix = $(prefix)
libdir = $(exec_prefix)/lib

PKG_NAME = games-manager
LIB_NAME = libgamesmanager
GIR_NAME = GamesManager
GIR_VERSION = 0.1

SOURCES = GameInfo.vala \
          Library.vala \
          System.vala \
          Desktop.vala \
          MegaDrive.vala

SHARED_OBJECT = $(LIB_NAME).so
GI_REPOSITORY = $(GIR_NAME)-$(GIR_VERSION).gir
GI_TYPELIB    = $(GIR_NAME)-$(GIR_VERSION).typelib

VALAC_OUTPUT = $(SHARED_OBJECT) $(GI_REPOSITORY) $(GIR_NAME).vapi
VALA_PKG = --pkg=gio-unix-2.0 --pkg=gtk+-3.0 --pkg=gdk-pixbuf-2.0 --pkg=libgda-5.0 --pkg=libxml-2.0
VALA_C_OPTION = -X -fPIC -X -shared
VALA_OPTIONS = --thread
VAPI_DIR = --vapidir=.

all: $(VALAC_OUTPUT) $(GI_TYPELIB)

$(VALAC_OUTPUT): $(SOURCES)
	valac $^ $(VALA_PKG) $(VAPI_DIR) $(VALA_OPTIONS) $(VALA_C_OPTION) -o $(SHARED_OBJECT) --library=$(GIR_NAME) --gir $(GI_REPOSITORY)

$(GI_TYPELIB): $(GI_REPOSITORY)
	g-ir-compiler --shared-library=$(SHARED_OBJECT) --output=$@ $(GI_REPOSITORY)

install: all
	install -D $(SHARED_OBJECT) $(libdir)/$(PKG_NAME)/$(SHARED_OBJECT)
	install -D $(GI_TYPELIB) $(libdir)/$(PKG_NAME)/girepository-1.0/$(GIR_NAME)-$(GIR_VERSION).typelib
	
clean:
	rm -f $(VALAC_OUTPUT) $(GI_TYPELIB)

PHONY: all install clean
