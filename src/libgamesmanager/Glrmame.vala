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
}
