namespace GamesManager {
	public class GameInfo : Object {
		public int64 id { get; set; }
		public string title { get; set; }
		public string developer { get; set; }
		public string icon { get; set; default = null; } // The icon name
		public string cover { get; set; } // The path to the cover
		public string released { get; set; }
		public System system { get; set; }
		public string genre { get; set; }
		public double played { get; set; }
		public double playedlast { get; set; }
		public string online { get; set; }
		public string description { get; set; }
		public string rank { get; set; }
		public string players { get; set; }
		
		/**
		 * Return a pixbuf representing the game (a cover or an icon) or None if it wasn't able to load one.
		 * size :  the desired icon size
		 * flags : the flags modifying the behavior of the icon lookup
		 */
		public Gdk.Pixbuf? get_pixbuf (int size, Gtk.IconLookupFlags flags) {
			// Try to load and return the cover.
			
			if (cover != null) {
				try {
					var pixbuf = new Gdk.Pixbuf.from_file_at_scale(cover, size, size, true);
					
					return pixbuf;
				}
				catch (Error e) {
					// Can't load the pixbuf.
				}
			}
			
			var icon_theme = Gtk.IconTheme.get_default();
			
			// Try to load and return the icon.
			if (icon != null) {
				var icon_info = icon_theme.lookup_icon(icon.split(".")[0], size, flags);
				if (icon_info != null) {
					try {
						var filename = icon_info.get_filename();
						var pixbuf = new Gdk.Pixbuf.from_file_at_scale(filename, size, size, true);
						
						return pixbuf;
					}
					catch (Error e) {
						// Can't load the pixbuf.
					}
				}
			}
			
			return null;
		}
		
		public void set_icon_lol(string iconname) {
			icon = iconname;
		}
	}
}
