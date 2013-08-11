namespace GamesManager {
	public enum GameSearchType {
		NONE,         // No searchis possible for the games of this system, they have to be set maually (Web games for example).
		STANDARD,     // Games for the system can be search in the whole file system.
		APPLICATIONS  // Games have to be searched only in standard XDG applications directories (the Desktop system uses it).
	}
	
	public abstract class System : Object {
		public GameSearchType game_search_type { construct set; get; default = GameSearchType.STANDARD; }
		public int64 id { set; get; }
		public string reference { construct set; get; }
		
		/**
		 * Return the balck list of applications.
		 */
		public abstract string[] get_application_black_list ();
		
		/**
		 * Return the name of the system.
		 */
		public abstract string get_name ();
		
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
		public abstract bool query_is_a_game (Library library, string uri);
		
		/**
		 * Return an unique reference for this game on this system.
		 */
		public abstract string get_game_reference_for_uri (string uri);
		
		/**
		 * Return an unique reference for this game on this system.
		 */
		public abstract GameInfo download_game_metadata (Library library, int game_id);
	}
}
