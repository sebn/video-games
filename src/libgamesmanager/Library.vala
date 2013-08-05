namespace GamesManager {
	public class Library : Object {
		public string provider { set; get; default = "SQLite"; }
		public string db_name { construct; get; }
		public string db_dir { construct; get; }
		
		private const string systems_table = "
		CREATE TABLE IF NOT EXISTS systems (
			id INTEGER PRIMARY KEY,
			ref TEXT, 
			name TEXT,
			UNIQUE (id, ref)
		)";
		
		/* Add constraints :
		   // favuriid->uris.gameid == id
		   0 <= rank <= 1
		 */
		private const string games_table = "
		CREATE TABLE IF NOT EXISTS games (
			id INTEGER PRIMARY KEY,
			systemid INTEGER,
			ref TEXT,
			played REAL,
			playedlast REAL,
			datamtime REAL,
			title TEXT,
			developer TEXT,
			icon TEXT,
			cover TEXT,
			description TEXT,
			released REAL,
			genre TEXT,
			players INTEGER,
			online TEXT,
			rank REAL,
			FOREIGN KEY(systemid) REFERENCES systems(id)
			UNIQUE (id, systemid, ref)
		)";
		
		private const string uris_table = "
		CREATE TABLE IF NOT EXISTS uris (
			id INTEGER PRIMARY KEY,
			uri TEXT,
			gameid INTEGER,
			FOREIGN KEY(gameid) REFERENCES games(id),
			UNIQUE (id, uri)
		)";
		
		private HashTable<string, System> systems;
		
		public signal void game_updated (int game_id);
		
		public
		Library (string db_name, string db_dir) {
			Object (db_name: db_name, db_dir: db_dir);
		}
		
		construct {
			systems = new HashTable<string, System> (str_hash, str_equal);
			
			var cnn = open_connection();
			
			cnn.execute_non_select_command (systems_table);
			cnn.execute_non_select_command (games_table);
			cnn.execute_non_select_command (uris_table);
			
			cnn.close();
		}
		
		/*
		 * Manage database connections
		 */
		
		public Gda.Connection?
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
		
		/*
		 * Manage systems
		 */
		
		public void
		add_system (System system) {
			if (systems.contains(system.reference)) {
				// Trow error : A Library can't contain two systems with the same id
			}
			else {
				systems.insert(system.reference, system);
				system.library = this;
			}
		}
		
		private string
		get_system_reference (int game_id) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT systems.ref FROM games, systems WHERE games.systemid = systems.id AND games.id = " + game_id.to_string("%i"));
			
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
		get_game_info (int game_id) {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.get_game_info(game_id);
		}
		
		public string
		get_game_exec (int game_id) {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.get_game_exec(game_id);
		}
		
		public bool
		is_game_available (int game_id) {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.is_game_available(game_id);
		}
		
		/*
		 * Game informations setters
		 */
		
		public void
		update_game_play_time (int game_id, double start, double end) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT played FROM games WHERE id = " + game_id.to_string("%i"));
			
			if (datamodel.get_n_rows() > 0) {
				var time_played =  datamodel.get_value_at(0, 0).get_double();
				time_played += end - start;
				
				cnn.execute_non_select_command ("UPDATE games SET played = " + time_played.to_string() + ", playedlast = " + end.to_string() + " WHERE id = " + game_id.to_string("%i"));
				
				this.game_updated (game_id);
			}
			else {
				// Throw error
			}
			
			cnn.close();
		}
	}
}
