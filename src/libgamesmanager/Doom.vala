namespace GamesManager {
	
	/**
	 * For more information on Doom WADs: http://doomwiki.org/wiki/WAD
	 */
	public class DoomWADHeader : Object {
		public string identification { set; get; }
		public int32 numlumps { set; get; }
		public int32 infotableofs { set; get; }
		
		public DoomWADHeader (string path) throws Error {
			var file = File.new_for_path(path);
			var file_stream = file.read ();
			var data_stream = new DataInputStream (file_stream);
			data_stream.set_byte_order (DataStreamByteOrder.LITTLE_ENDIAN);
			
			var buffer = new uint8[4];
			
			data_stream.read (buffer);
			identification = (string) buffer;
			
			numlumps = data_stream.read_int32 ();
			infotableofs = data_stream.read_int32 ();
		}
		
		public bool
		query_is_valid () {
			return identification == "IWAD";
		}
	}
	
	public class Doom : System {
		private Glrmame.Document document;
		
		public Doom () {
			Object (reference: "doom", game_search_type: GameSearchType.STANDARD);
		}
		
		construct {
			var clrmamepro_dir = Glrmame.get_clrmamepro_dir ();
			
			if (clrmamepro_dir != null) {
				var file = File.new_for_path (clrmamepro_dir);
				file = file.get_child (@"$(reference).dat");
				if (file.query_exists ())
					document = new Glrmame.Document(file.get_path ());
			}
		}
		
		public override string[]
		get_application_black_list () {
			return {};
		}
		
		public override string
		get_name () {
			return "Doom engine";
		}
		
		public override GameInfo
		get_game_info (Library library, int game_id) {
			var info = library.get_default_game_info (game_id);
			
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			
			var glrmame_info = document.search_game(file);
			
			try {
				var regex = new Regex ("^\"(?:\\[[^\\[\\]]*?\\] )?(.*?)(?: \\([^()]*?\\))?(?: v[^ ]*?)?(?: \\([^()]*?\\))?\"$");
				var result = regex.split(glrmame_info.name);
				
				info.title = (result.length > 2) ? result[1] : file.get_basename ();
			}
			catch (RegexError e) {
				info.title = file.get_basename ();
			}
			info.icon = "gtk-floppy";
			
			return info;
		}
		
		public override string
		get_game_exec (Library library, int game_id) {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			return @"prboom -vidmode gl -nowindow -iwad $(file.get_path())";
		}
		
		public override bool
		query_is_game_available (Library library, int game_id) {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			return file.query_exists() && (query_is_a_game (library, library.get_game_uri(game_id)));
		}
		
		public override bool
		query_is_a_game (Library library, string uri) {
			var file = File.new_for_uri (uri);
			var splitted_name = file.get_basename().split(".");
			var extension = splitted_name[splitted_name.length - 1].down();
			
			if (extension != "wad") return false;
			
			try {
				var header = new DoomWADHeader (file.get_path ());
				return header.query_is_valid ();
			}
			catch (Error e) {
				return false;
			}
		}
		
		public override string
		get_game_reference_for_uri (string uri) {
			var file = File.new_for_uri (uri);
			var glrmame_info = document.search_game(file);
			try {
				var regex = new Regex ("^\"(?:\\[[^\\[\\]]*?\\] )?(.*?)(?: \\([^()]*?\\))?(?: v[^ ]*?)?(?: \\([^()]*?\\))?\"$");
				var result = regex.split(glrmame_info.name);
				
				return (result.length > 2) ? result[1] : file.get_basename ();
			}
			catch (RegexError e) {
				return file.get_basename ();
			}
		}
		
		public override GameInfo
		download_game_metadata (Library library, int game_id) {
			return get_game_info (library, game_id);
		}
	}
}
