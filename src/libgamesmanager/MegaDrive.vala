namespace GamesManager {
	public class MegaDriveROMHeader : Object {
		private string path { set; get; }
		
		public string console_name { set; get; }
		public string release_date { set; get; }
		public string domestic_name { set; get; }
		public string international_name { set; get; }
		public string version { set; get; }
		public uint16 checksum { set; get; }
		public string IO_support { set; get; }
		public uint32 ROM_start { set; get; }
		public uint32 ROM_end { set; get; }
		public uint32 RAM_start { set; get; }
		public uint32 RAM_end { set; get; }
		public string enables_SRAM { set; get; }
		public uint32 SRAM_start { set; get; }
		public uint32 SRAM_end { set; get; }
		public string notes { set; get; }
		
		public MegaDriveROMHeader (string path) throws Error {
			this.path = path;
			var file = File.new_for_path(path);
			var file_stream = file.read ();
			var data_stream = new DataInputStream (file_stream);
			data_stream.set_byte_order (DataStreamByteOrder.BIG_ENDIAN);
			
			data_stream.seek(0x100, SeekType.SET);
			
			var buffer = new uint8[16];
			
			data_stream.read (buffer);
			console_name = (string) buffer;
			
			data_stream.read (buffer);
			release_date = (string) buffer;
			
			buffer = new uint8[48];
			
			data_stream.read (buffer);
			domestic_name = (string) buffer;
			
			data_stream.read (buffer);
			international_name = (string) buffer;
			
			buffer = new uint8[14];
			
			data_stream.read (buffer);
			version = (string) buffer;
			
			checksum = data_stream.read_uint16 ();
			
			buffer = new uint8[16];
			
			data_stream.read (buffer);
			IO_support = (string) buffer;
			
			ROM_start = data_stream.read_uint32 ();
			ROM_end = data_stream.read_uint32 ();
			
			RAM_start = data_stream.read_uint32 ();
			RAM_end = data_stream.read_uint32 ();
			
			buffer = new uint8[3];
			
			data_stream.read (buffer);
			enables_SRAM = (string) buffer;
			
			data_stream.skip (1);
			
			SRAM_start = data_stream.read_uint32 ();
			SRAM_end = data_stream.read_uint32 ();
			
			buffer = new uint8[68];
			
			data_stream.read (buffer);
			notes = (string) buffer;
		}
		
		public bool
		query_is_valid () {
			return console_name == "SEGA GENESIS    " || console_name == "SEGA MEGA DRIVE ";
		}
		
		public string
		query_release_date () throws Error {
			try {
				var regex = new Regex ("""([0-9]{4}).([A-Z]{3})$""");
				var result = regex.split(release_date);
				
				if (result.length < 3) throw new Error (Quark.from_string ("megadrive-header-format"), 1, "The header of the megadrive ROM `%s' is malformed: can't retrieve the release date.", path);
				
				var year = result [1];
				var month = "";
				
				string[] months = { "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC" };
				for (int i = 0 ; i < 12 && month == "" ; i++) {
					if (months[i] == result[2]) {
						month = (i+1).to_string ("%.2i");
					}
				}
				return year + "-" + month;
			}
			catch (RegexError e) {
				throw new Error (Quark.from_string ("regex-scheme"), 1, "The programmer can't do regex, blame him.");
			}
		}
	}
	
	public class MegaDrive : System {
		private const string[] BLACK_LIST = {
			"gens.desktop", 
			"dribble-gens.desktop" };
		
		private Glrmame.Document nointro_doc;
		private Glrmame.Document tosec_doc;
		
		public MegaDrive () {
			Object (reference: "megadrive", game_search_type: GameSearchType.STANDARD);
		}
		
		construct {
			var clrmamepro_dir = Glrmame.get_clrmamepro_dir ();
			
			if (clrmamepro_dir != null) {
				var dir = File.new_for_path (clrmamepro_dir);
				
				var nointro_file = dir.get_child (@"$(reference)-nointro.dat");
				if (nointro_file.query_exists ())
					nointro_doc = new Glrmame.Document(nointro_file.get_path ());
				
				var tosec_file = dir.get_child (@"$(reference)-tosec.dat");
				if (tosec_file.query_exists ())
					tosec_doc = new Glrmame.Document(tosec_file.get_path ());
			}
		}
		
		public override string[]
		get_application_black_list () {
			return BLACK_LIST;
		}
		
		public override string
		get_name () {
			return "Mega Drive / Genesis";
		}
		
		public override GameInfo
		get_game_info (Library library, int game_id) {
			var info = library.get_default_game_info (game_id);
			
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			
			var header = new MegaDriveROMHeader (file.get_path ());
			
			Glrmame.TOSEC? tosec_info = null;
			Glrmame.NoIntro? nointro_info = null;
			
			try {
				var game = tosec_doc.search_game(file);
				if (game != null) tosec_info = new Glrmame.TOSEC (game);
			}
			catch (Error e) { }
			
			try {
				var game = nointro_doc.search_game(file);
				if (game != null) nointro_info = new Glrmame.NoIntro (game);
			}
			catch (Error e) { }
			
			string[] countries = {};
			
			try {
				info.released = header.query_release_date ();
			}
			catch (Error e) { }
			
			// Try to get info from TOSEC.
			if (tosec_info != null) {
				info.title = tosec_info.title;
				info.developer = tosec_info.publisher;
				if (info.released == null) info.released = tosec_info.date;
				
				countries = tosec_info.countries;
			}
			
			// Try to get info from No-Intro.
			if (nointro_info != null) {
				if (info.title == null) info.title = nointro_info.title;
			}
			
			info.icon = "game-system-megadrive-jp";
			
			// Get the available countries for the game.
			var available_countries = new string[0];
			
			var enumerator = File.new_for_path (@"$(library.covers_dir)/$(reference)").enumerate_children (FileAttribute.STANDARD_NAME, 0);
			FileInfo file_info;
			while ((file_info = enumerator.next_file ()) != null) {
				try {
					var regex = new Regex (@"$(info.title)-([A-Z]{2}).jpg");
					var result = regex.split (file_info.get_name ());
					if (result.length > 1) available_countries += result [1];
				}
				catch (RegexError e) { }
			}
			foreach (string s in available_countries) stdout.printf ("available_countries: %s\n", s);
			
			// If a country is defined for the game, use the cover of this country.
			if (countries.length == 1) {
				info.cover = @"$(library.covers_dir)/$(reference)/$(info.title)-$(countries[0]).jpg";
			}
			
			// If no country is defined for the game, use the local country.
			if (info.cover == null || ! File.new_for_path (info.cover).query_exists ()) {
				var local_country = Pango.Language.get_default ().to_string ().split ("-")[1].up ();
				info.cover = @"$(library.covers_dir)/$(reference)/$(info.title)-$(local_country).jpg";
			}
			
			// If the local country don't haves a cover, guess its world region (JA, EU or US) and use it.
			
			// If there is no cover still, use a the first one available.
			if ((info.cover == null || ! File.new_for_path (info.cover).query_exists ()) && available_countries.length > 0) {
				info.cover = @"$(library.covers_dir)/$(reference)/$(info.title)-$(available_countries[0]).jpg";
			}
			
			return info;
		}
		
		public override string
		get_game_exec (Library library, int game_id) {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			
			if (query_program_exists ("gens"))
				return @"gens --fs --render-mode 2 --quickexit --enable-perfectsynchro \"$(file.get_path())\"";
			else
				return "";
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
			
			if (extension != "bin" && extension != "md") return false;
			
			try {
				var header = new MegaDriveROMHeader (file.get_path ());
				return header.query_is_valid ();
			}
			catch (Error e) {
				return false;
			}
		}
		
		public override string
		get_game_reference_for_uri (string uri) {
			var file = File.new_for_uri (uri);
			var header = new MegaDriveROMHeader (file.get_path ());
			return header.international_name;
		}
		
		public override GameInfo
		download_game_metadata (Library library, int game_id) {
			var info = get_game_info (library, game_id);
			
			var cover_dir = File.new_for_path (@"$(library.covers_dir)/$(reference)");
			if (!cover_dir.query_exists ()) cover_dir.make_directory_with_parents ();
			
			stdout.printf("try to get covers uris\n");
			foreach (string uri in Guardiana.get_cover_uris (info.title)) {
				stdout.printf("try to get country from %s\n", uri);
				var country = Guardiana.query_country_for_cover_uri (uri);
				
				var file = cover_dir.get_child (@"$(info.title)-$(country).jpg");
				
				if (!file.query_exists ()) {
					try {
						stdout.printf("try to download %s\n", uri);
						File.new_for_uri (uri).copy (file, FileCopyFlags.NONE);
					stdout.printf("just downloaded %s\n", uri);
					}
					catch (Error e) {
						stderr.printf ("Error: can't copy `%s' in `%s'.\n", uri, file.get_path ());
					}
				}
			}
			
			return info;
		}
	}
	
	public class Guardiana : Object {
		public const string[] flags = {"error", "JP", "EU", "US", "CN", "BR", "pirate", "KR", "AU", "FR", "BE", "ES", "GB", "IT", "PT", "SE", "CA", "LU", "unknown", "not-understood"};
		
		public static string[]
		get_cover_uris (string title) {
			var guardiana_uri = @"http://www.guardiana.net/MDG-Database/Mega Drive/$(title)/";
			
			var session = new Soup.Session ();
			var message = new Soup.Message ("GET", guardiana_uri);
			
			session.send_message (message);
			
			var page = (string) message.response_body.data;
			
			string[] covers = {};
			try {
				var cover_re = "src=\"(http://media[0-9]*.sega-database.com//front//[0-9]+/[0-9]+/[0-9]+\\.jpg)\"";
				var regex = new Regex (cover_re);
				var result = regex.split(page);
				for (int i = 1 ; i < result.length ; i+=2) covers += result[i];
			}
			catch (RegexError e) { }
			
			return covers;
		}
		
		public static string
		query_country_for_cover_uri (string uri) {
			try {
				var country_re = "/([0-9]+)/[0-9]+\\.jpg";
				var regex = new Regex (country_re);
				var result = regex.split(uri);
				stdout.printf("lal\n");
				if (result.length < 2)
					return flags[0];
				stdout.printf("lel\n");
				var country_index = int.parse(result[1]);
				stdout.printf("lil %i %i\n", country_index, flags.length);
				if (country_index < flags.length) {
					stdout.printf("lol %i\n", country_index);
					return flags[country_index];
				}
				else {
					stdout.printf("lul\n");
					return flags[0];
				}
			}
			catch (RegexError e) {
				return flags[0];
			}
		}
	}
}
