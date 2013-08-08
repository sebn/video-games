namespace GamesManager {
	public abstract class Desktop : System {
		public Desktop () {
			//Object (reference: "desktop", game_search_type: GameSearchType.APPLICATIONS);
		}
		
		public override GameInfo
		get_game_info (Library library, int game_id) {
			var info = library.get_default_game_info(game_id);
			
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			var desktop_app_info = new DesktopAppInfo.from_filename(file.get_path());
			
			info.system = reference;
			info.title = desktop_app_info.get_name();
			info.icon = desktop_app_info.get_icon().to_string();
			
			return info;
		}
		
		public override string
		get_game_exec (Library library, int game_id) {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			var desktop_app_info = new DesktopAppInfo.from_filename(file.get_path());
			
			return desktop_app_info.get_executable();
		}
		
		public override bool
		query_is_game_available (Library library, int game_id) {
			var uri = library.get_game_uri(game_id);
			var file = File.new_for_uri(uri);
			if (file.query_exists()) {
				foreach (string black_listed in library.get_application_black_list())
					if (file.get_basename() == black_listed) return false;
				return true;
			}
			else return false;
		}
	}
}
