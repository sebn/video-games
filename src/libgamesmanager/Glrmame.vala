namespace GamesManager.Glrmame {
	public class Document : Object {
		public string path { construct; get; }
		public List<Game> games;
		
		public string name { construct; get; }
		public string description { construct; get; }
		public string version { construct; get; }
		public string author { construct; get; }
		public string comment { construct; get; }
		
		public Document (string path) {
			Object (path: path);
		}
		
		construct {
			stdout.printf ("Parsing `%s`.\n", path);
			games = new List<Game>();
			Game? game = null;
			
			var words = get_words ();
			
			var tags_path = new string[0];
			var last_path = new string[0];
			
			string? tag = null;
			for (size_t i = 1 ; i < words.length ; i+=2) {
				unowned string word = words[i];
				if (last_path.length > 0 && tags_path.length == 0) {
					if (game != null) {
						games.append(game);
						game = null;
					}
				}
				else last_path = tags_path;
				
				if (tag == null) {
					if (word == ")") {
						// Go up in the tree.
						tags_path.resize(tags_path.length - 1);
					}
					else tag = word.down();
				}
				else {
					if (word == "(") {
						// Add a new depth in the tree.
						tags_path += tag;
					}
					else {
						if (tags_path.length > 0) {
							if (tags_path[0] == "game") {
								if (tags_path.length > 1 && tags_path[1] == "rom") {
									// Set the rom property of the game.
									if (game.rom == null) game.rom = new Rom();
									switch (tag.down()) {
										case "name":
											game.rom.name = word;
											break;
										case "size":
											game.rom.size = word;
											break;
										case "baddump":
											game.rom.baddump = word;
											break;
										case "nodump":
											game.rom.nodump = word;
											break;
										case "crc":
											game.rom.crc = word;
											break;
										case "crc32":
											game.rom.crc32 = word;
											break;
										case "md5":
											game.rom.md5 = word;
											break;
										case "sha1":
											game.rom.sha1 = word;
											break;
										default:
											stderr.printf("Error: while parsing file `%s`, in path `%s` encountered unknown tag `%s`.\n", path, string.joinv(" ", tags_path), tag);
											break;
									}
								}
								else {
									// Set properties of the game.
									if (game == null) game = new Game();
									switch (tag.down()) {
										case "name":
											game.name = word;
											break;
										case "cloneof":
											game.cloneof = word;
											break;
										case "description":
											game.description = word;
											break;
										case "sample":
											game.sample = word;
											break;
										case "sampleof":
											game.sampleof = word;
											break;
										case "year":
											game.year = word;
											break;
										case "manufacturer":
											game.manufacturer = word;
											break;
										default:
											stderr.printf("Error: while parsing file `%s`, in path `%s` encountered unknown tag `%s`.\n", path, string.joinv(" ", tags_path), tag);
											break;
									}
								}
							}
							else if (tags_path[0] == "clrmamepro") {
								switch (tag.down()) {
									case "name":
										name = word;
										break;
									case "description":
										description = word;
										break;
									case "version":
										version = word;
										break;
									case "author":
										author = word;
										break;
									case "comment":
										comment = word;
										break;
									default:
										stderr.printf("Error: while parsing file `%s`, in path `%s` encountered unknown tag `%s`.\n", path, string.joinv(" ", tags_path), tag);
										break;
								}
							}
							else {
								stderr.printf("Error: the file is malformed. Current path: `%s`. Expected tag `clrmamepro` or `game`, got `%s` for word `%s`.\n", string.joinv(" ", tags_path), tag, word);
							}
						}
					}
					tag = null;
				}
			}
			stdout.printf ("Parsed `%s`.\n", path);
		}
		
		public string[]
		get_words () {
			stdout.printf ("Retrieving words of `%s`.\n", path);
			var file = File.new_for_path (path);
			var info = file.query_info("*", FileQueryInfoFlags.NONE);
			var data = new uint8[info.get_size()];
			file.read().read(data);
			
			var regex = new Regex ("""((?:[^ \n\r\t"]|"[^"]*")+)""");
			
			return regex.split((string) data);
		}
		
		public Game?
		search_game (File file) {
			var info = file.query_info("*", FileQueryInfoFlags.NONE);
			
			var size = info.get_size();
			var data = new uchar[size];
			file.read().read(data);
			
			var md5 = Checksum.compute_for_data (ChecksumType.MD5, data);
			var sha1 = Checksum.compute_for_data (ChecksumType.SHA1, data);
			
			stdout.printf ("Searching `%s`.\n", file.get_path());
			
			foreach (Game game in games) {
				if (game.rom != null && game.rom.size != null && int64.parse (game.rom.size) == size) {
					if (game.rom.md5 != null && game.rom.md5.down() == md5) {
						stdout.printf ("Found `%s` !\n", file.get_path());
						return game;
					}
					if (game.rom.sha1 != null && game.rom.sha1.down() == sha1) {
						stdout.printf ("Found `%s` !\n", file.get_path());
						return game;
					}
				}
			}
			
			return null;
		}
	}
	
	public class Game : Object {
		public string? name { construct set; get; }
		public string? cloneof { construct set; get; }
		public string? description { construct set; get; }
		public Rom? rom { construct set; get; }
		public string? sample { construct set; get; }
		public string? sampleof { construct set; get; }
		public string? year { construct set; get; }
		public string? manufacturer { construct set; get; }
		
		public TOSECInfo query_tosec_info () throws Error {
			var tosec_error = new Error (Quark.from_string ("tosec-name-parsing"), 1, "The name don't uses the TOSEC conventions.");
			var regex_error = new Error (Quark.from_string ("regex-scheme"), 1, "The programmer can't do regex, blame him.");
			
			Regex regex;
			var result = new string[0];
			try {
				regex = new Regex ("^\"([^\\(\\)\\[\\]]+) .*?(\\(?[^\\[\\]]*\\)?)(\\[?[^\\(\\)]*\\]?)\"");
				result = regex.split(name);
			}
			catch (RegexError e) {
				throw regex_error;
			}
			
			var info = new TOSECInfo();
			
			if (result.length < 4) throw tosec_error;
			
			var title_info = result[1];
			var game_info = result[2];  // The groups between parenthesis.
			var rom_info = result[3];   // The groups between brackets.
			
			// Look for the title and the version.
			
			try {
				regex = new Regex ("^(.*?)(?: (v[^ ]+?|Rev [^ ]+?))?$");
				result = regex.split(title_info);
			}
			catch (RegexError e) {
				throw regex_error;
			}
			
			if (result.length < 3) throw tosec_error;
			
			info.title = result[1];
			info.version = (result.length > 3 && result[2] != "") ? result[2] : null;
			
			// Look for the demo, the date and the publisher.
			
			try {
				regex = new Regex ("""^(?:\((demo.*?)\) )?\(([^()]*?)\)\(([^()]*?)\)(.*?$)""");
				result = regex.split(game_info);
			}
			catch (RegexError e) {
				throw regex_error;
			}
			
			if (result.length < 5) throw tosec_error;
			
			info.demo = (result[1] != "") ? result[1] : null;
			info.date = result[2];
			info.publisher = result[3];
			
			var game_info_rest = result[4];
			
			/* Look for the system, the video, the country, the language, the copyright,
			 * the status, the development status, the media type and the media label.
			 */
			
			var system_ex = """(?:\(([^()]*?)\))?"""; // May be too greedy because it is too generic.
			var video_ex = """(?:\((CGA|EGA|HGC|MCGA|MDA|NTSC|NTSC-PAL|PAL|PAL-60|PAL-NTSC|SVGA|VGA|XGA)\))?""";
			var countries_ex = """(?:\(([A-Z]{2}(?:-[A-Z]{2})?)\))?""";
			var languages_ex = """(?:\(((?:[a-z]{2}(?:-[a-z]{2})?)|M[0-9])\))?""";
			var copyright_ex = """(?:\((CW|CW-R|FW|GW|GW-R|LW|PD|SW|SW-R)\))?""";
			var development_ex = """(?:\((alpha|beta|preview|pre-release|proto)\))?""";
			var media_type_ex = """(?:\(((?:Disc|Disk|File|Part|Side|Tape) [^()]*?)\))?""";
			var media_label_ex = """(?:\(([^()]*?)\))?"""; // May be too greedy because it is too generic.
			
			try {
				regex = new Regex ("^" + video_ex + countries_ex + languages_ex + copyright_ex + development_ex + media_type_ex + "(.*?$)");
				result = regex.split(game_info_rest);
			}
			catch (RegexError e) {
				throw regex_error;
			}
			
			uint i = 1;
			//info.system = result[i] != "" ? result[i] : null; i++;
			info.video = result[i] != "" ? result[i] : null; i++;
			info.countries = result[i] != null && result[i] != "" ? result[i].split("-") : new string[0]; i++;/*
			info.languages = result[i] != null && result[i] != "" ? result[i].split("-") : new string[0]; i++;
			info.copyright = result[i] != "" ? result[i] : null; i++;
			info.development = result[i] != "" ? result[i] : null; i++;
			info.media_type = result[i] != "" ? result[i] : null; i++;*/
			//info.media_label = result[i] != "" ? result[i] : null; i++;
			
			return info;
		}
	}
	
	public class TOSECInfo : Object {
		public string title { construct set; get; }
		public string? version { construct set; get; }
		public string? demo { construct set; get; }
		public string date { construct set; get; }
		public string publisher { construct set; get; }
		public string? system { construct set; get; }
		public string? video { construct set; get; }
		public string[] countries { construct set; get; default = {}; }
		public string[] languages { construct set; get; default = {}; }
		public string? copyright { construct set; get; }
		public string? development { construct set; get; }
		public string? media_type { construct set; get; }
		public string? media_label { construct set; get; }
		public string? dump_info_flags { construct set; get; }
		public string? more_info { construct set; get; }
	}
	
	public class Rom : Object {
		public string? name { construct set; get; }
		public string? size { construct set; get; }
		public string? baddump { construct set; get; }
		public string? nodump { construct set; get; }
		public string? crc { construct set; get; }
		public string? crc32 { construct set; get; }
		public string? md5 { construct set; get; }
		public string? sha1 { construct set; get; }
	}
	
	public string? get_clrmamepro_dir () {
		foreach (string dir in Environment.get_system_data_dirs ()) {
			var file = File.new_for_path (dir);
			file = file.get_child("libgamesmanager/clrmamepro");
			if (file.query_exists()) return file.get_path();
		}
		return null;
	}
}
