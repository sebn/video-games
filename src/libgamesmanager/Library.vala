namespace GamesManager {
	public class Library : Object {
		public string provider { set; get; default = "SQLite"; }
		public string db_name { construct; get; }
		public string db_dir { construct; get; }
		
		private HashTable<string, System> systems;
		
		public signal void game_updated (int id);
		
		public
		Library (string db_name, string db_dir) {
			Object (db_name: db_name, db_dir: db_dir);
		}
		
		construct {
			systems = new HashTable<string, System> (str_hash, str_equal);
			
			var cnn = open_connection();
			string games_table = "
			CREATE TABLE IF NOT EXISTS games (
				id INTEGER PRIMARY KEY,
				gameid INTEGER,
				system TEXT,
				time_played REAL,
				last_played REAL,
				UNIQUE (id, system)
			)";
			cnn.execute_non_select_command (games_table);
		}
		
		/*
		 * Manage database connections
		 */
		
		protected Gda.Connection?
		open_connection () {
			// TODO Gda.Connection.open_from_string raise a warning (not caused by get_connection_string)
			Gda.Connection cnn = null;
			try {
				cnn = Gda.Connection.open_from_string (null, get_connection_string(), null, Gda.ConnectionOptions.NONE);
			}
			catch (Error e) {
				
			}
			return cnn;
		}
		
		private string
		get_connection_string () {
			return string.join("", this.provider, "://DB_DIR=", this.db_dir, ";DB_NAME=", this.db_name);
		}
		
		public void
		print_games () {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT * FROM games");
			int columns = datamodel.get_n_columns();
			int rows = datamodel.get_n_rows();
			for (int row = 0 ; row < rows ; row++ ) {
				var id = datamodel.get_value_at(0, row).get_int();
				var gameid = datamodel.get_value_at(1, row).get_int();
				var system = datamodel.get_value_at(2, row).get_string();
				var time_played = datamodel.get_value_at(3, row).get_double();
				var last_played = datamodel.get_value_at(4, row).get_double();
			}
			cnn.close();
		}
		
		/*
		 * Manage systems
		 */
		
		public void
		add_system (System system) {
			if (systems.contains(system.id)) {
				// Trow error : A Library can't contain two systems with the same id
			}
			else {
				systems.insert(system.id, system);
				system.library = this;
			}
		}
		
		private int
		get_system_game_id (int id) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT gameid FROM games WHERE id = " + id.to_string("%i"));
			
			if (datamodel.get_n_rows() > 0) {
				return datamodel.get_value_at(0, 0).get_int();
			}
			else {
				// Throw error
				return 0;
			}
		}
		
		private string
		get_system_name (int id) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT system FROM games WHERE id = " + id.to_string("%i"));
			
			if (datamodel.get_n_rows() > 0) {
				return datamodel.get_value_at(0, 0).get_string();
			}
			else {
				// Throw error
				return "";
			}
		}
		
		public void
		search_new_games () {
			foreach (System system in systems.get_values()) {
				system.search_new_games();
			}
		}
		
		/*
		 * Game informations getters
		 */
		
		public int[]
		get_games_id () {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT id FROM games");
			
			int rows = datamodel.get_n_rows();
			var ids = new int[rows];
			
			for (int row = 0 ; row < rows ; row++ ) {
				ids[row] = datamodel.get_value_at(0, row).get_int();
			}
			
			cnn.close();
			
			return ids;
		}
		
		public GameInfo
		get_game_info (int id) {
			var systemid = get_system_name(id); // Cause warnings
			var gameid = get_system_game_id(id); // Cause warnings
			var system = systems.get(systemid);
			return system.get_game_info(gameid);
		}
		
		public string
		get_game_exec (int id) {
			var systemid = get_system_name(id);
			var gameid = get_system_game_id(id);
			
			var system = systems.get(systemid);
			return system.get_game_exec(gameid);
		}
		
		public bool
		is_game_available (int id) {
			var systemid = get_system_name(id);
			var gameid = get_system_game_id(id);
			
			var system = systems.get(systemid);
			return system.is_game_available(gameid);
		}
		
		/*
		 * Game informations setters
		 */
		
		public void
		update_game_play_time (int id, double start, double end) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT time_played FROM games WHERE id = " + id.to_string("%i"));
			
			if (datamodel.get_n_rows() > 0) {
				var time_played =  datamodel.get_value_at(0, 0).get_double();
				time_played += end - start;
				
				cnn.execute_non_select_command ("UPDATE games SET time_played = " + time_played.to_string() + ", last_played = " + end.to_string() + " WHERE id = " + id.to_string("%i"));
				
				this.game_updated (id);
			}
			else {
				// Throw error
			}
			
			cnn.close();
		}
	}
}
