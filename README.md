#Video Games

![Video Games logo](https://raw.github.com/Kekun/video-games/master/icons/hicolor/256x256/apps/badnik.png "Video Games logo")

Video Games is a video game manager and launcher for GNOME.

##Dependencies

- Python 3.3 (or newer)
- [Badnik](https://github.com/Kekun/badnik)
- GNOME Documents (for libgd)
- GTK+ (tested on 3.8 and 3.10, should work on older Gtk+ 3 versions)

##Installation

To install Video Games type from the project's directory :
`make install`

You can set the installation directory by modifying the prefix variable (/usr/local by default) :
`make install prefix=/usr`

##To-do

Change unwanted "badnik" references to "video-games" in:
- icons
- desktop entry
- executable
- …

Port the UI to Glade.

Allow to add games by clicking the *add games* button.

Publish a first stable version handling desktop entries.

