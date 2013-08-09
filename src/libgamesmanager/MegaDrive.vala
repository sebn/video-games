namespace GamesManager {
	public class MegaDriveROMHeader : Object {
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
	}
	
	public abstract class MegaDrive : System {
		private const string[] BLACK_LIST = {
			"gens.desktop", 
			"dribble-gens.desktop" };
		
		public MegaDrive () {
			//Object (reference: "megadrive", game_search_type: GameSearchType.APPLICATIONS);
		}
		
		public override string[]
		get_application_black_list () {
			return BLACK_LIST;
		}
		/*
		public override GameInfo
		get_game_info (Library library, int game_id) {
			
		}
		
		public override string
		get_game_exec (Library library, int game_id) {
			
		}
		*/
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
			var extension = splitted_name[splitted_name.length - 1];
			
			if (extension != "bin" && extension != "md") return false;
			
			try {
				var header = new MegaDriveROMHeader (file.get_path ());
				return header.console_name == "SEGA GENESIS    " || header.console_name == "SEGA MEGA DRIVE ";
			}
			catch (Error e) {
				return false;
			}
		}
		/*
		public override string
		get_game_reference_for_uri (string uri) {
			
		}
		
		public override GameInfo
		download_game_metadata (Library library, int game_id) {
			
		}*/
	}
}
