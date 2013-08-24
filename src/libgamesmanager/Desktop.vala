namespace GamesManager {
	public abstract class Desktop : System {
		private const string[] BLACK_LIST = {
			"badnik.desktop",
			"steam.desktop", 
			"lutris.desktop" };
		
		public Desktop () {
			//Object (reference: "desktop", game_search_type: GameSearchType.APPLICATIONS);
		}
		
		public override string[]
		get_application_black_list () {
			return BLACK_LIST;
		}
		
		public override string
		get_name () {
			return "Desktop entry";
		}
		
		public override GameInfo
		get_game_info (Library library, int game_id) throws Error {
			var info = library.get_default_game_info(game_id);
			
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			var desktop_app_info = new DesktopAppInfo.from_filename(file.get_path());
			
			info.title = desktop_app_info.get_name();
			info.icon = desktop_app_info.get_icon().to_string();
			
			return info;
		}
		
		public override string
		get_game_exec (Library library, int game_id) throws Error {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			var desktop_app_info = new DesktopAppInfo.from_filename(file.get_path());
			
			return desktop_app_info.get_executable();
		}
		
		public override bool
		query_is_game_available (Library library, int game_id) throws Error {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			if (file.query_exists()) {
				foreach (string black_listed in library.get_application_black_list())
					if (file.get_basename() == black_listed) return false;
				return true;
			}
			else return false;
		}
		/*
		public override bool
		query_is_a_game (string uri) {
			
		}*/
		
		public override string
		get_game_reference_for_uri (string uri) {
			var file = File.new_for_uri(uri);
			return file.get_basename().split(".")[0];
		}
		/*
		public override GameMetadataInfo
		download_game_metadata (Library library, int game_id) {
			return new GameMetadataInfo ();
		}*/
	}
}
