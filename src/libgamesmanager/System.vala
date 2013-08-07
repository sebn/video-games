namespace GamesManager {
	public enum GameSearchType {
		NONE,         // No searchis possible for the games of this system, they have to be set maually (Web games for example).
		STANDARD,     // Games for the system can be search in the whole file system.
		APPLICATIONS  // Games have to be searched only in standard XDG applications directories (the Desktop system uses it).
	}
	
	public abstract class System : Object {
		public GameSearchType game_search_type { construct set; get; default = GameSearchType.STANDARD; }
		public int64 id { set; get; }
		public string reference { construct; get; }
		
		protected GameInfo
		_get_game_info (Library library, int game_id) {
			var info = new GameInfo();
			
			var cnn = library.open_connection();
			
			try {
				var datamodel = cnn.execute_select_command ("SELECT games.id, games.title, games.developer, games.icon, games.cover, games.released, systems.ref, games.genre, games.played, games.playedlast, games.online, games.description, games.rank, games.players FROM games, systems WHERE games.systemid = systems.id AND games.id = " + game_id.to_string("%i"));
				
				if (datamodel.get_n_rows() > 0) {
					info.id = datamodel.get_value_at(0, 0).get_int();
					info.title = datamodel.get_value_at(1, 0).get_string();
					info.developer = datamodel.get_value_at(2, 0).get_string();
					info.icon = datamodel.get_value_at(3, 0).get_string();
					info.cover = datamodel.get_value_at(4, 0).get_string();
					info.released = datamodel.get_value_at(5, 0).get_string();
					info.system = datamodel.get_value_at(6, 0).get_string();
					info.genre = datamodel.get_value_at(7, 0).get_string();
					info.played = datamodel.get_value_at(8, 0).get_double();
					info.playedlast = datamodel.get_value_at(9, 0).get_double();
					info.online = datamodel.get_value_at(10, 0).get_string();
					info.description = datamodel.get_value_at(11, 0).get_string();
					info.rank = datamodel.get_value_at(12, 0).get_string();
					info.players = datamodel.get_value_at(13, 0).get_string();
				}
				else {
					stderr.printf("Error: there is no such game identifier in the database: %i.\n", game_id);
				}
			}
			catch (Error e) {
				stderr.printf("Error: can't retrieve game informations from the database.\n");
			}
			
			cnn.close();
			
			return info;
		}
		
		/**
		 * Return a GameInfo object containing as much informations as possible about the game.
		 */
		public abstract GameInfo get_game_info (Library library, int game_id);
		
		/**
		 * Return a string containing the command line to start the game.
		 */
		public abstract string get_game_exec (Library library, int game_id);
		
		/**
		 * Check if the game can actually be played (if its launcher is installed, if its files are actually present...).
		 */
		public abstract bool query_is_game_available (Library library, int game_id);
		
		/**
		 * Check if the given URI actually represents a game for this system.
		 */
		public abstract bool query_is_a_game (string uri);
		
		/**
		 * Return an unique reference for this game on this system.
		 */
		public abstract string get_game_reference_for_uri (string uri);
	}
}
