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
			if (! systems.contains(system.reference)) {
				systems.insert(system.reference, system);
				
				var cnn = open_connection();
				var datamodel = cnn.execute_select_command ("SELECT id FROM systems WHERE ref = '" + system.reference + "'");
				
				if (datamodel.get_n_rows() > 0) {
					system.id = datamodel.get_value_at(0, 0).get_int();
				}
				else {
					cnn.execute_non_select_command ("INSERT INTO systems (id, ref) VALUES (NULL, '" + system.reference + "')");
					datamodel = cnn.execute_select_command ("SELECT id FROM systems WHERE ref = '" + system.reference + "'");
					if (datamodel.get_n_rows() > 0) {
						system.id = datamodel.get_value_at(0, 0).get_int();
					}
					else {
						stdout.printf("error: can't get the system id\n");
					}
				}
				
				cnn.close();
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
			var standard = new List<System>();
			var applications = new List<System>();
			foreach (System system in systems.get_values()) {
				switch (system.game_search_type) {
				case GameSearchType.APPLICATIONS:
					applications.append(system);
					break;
				case GameSearchType.STANDARD:
					standard.append(system);
					break;
				}
			}
			if (standard.length() > 0) {
				foreach (System system in standard) {
					//system.search_new_games();
				}
			}
			if (applications.length() > 0) {
				foreach (System system in standard) {
					//system.search_new_games();
				}
			}
			//
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
			return system.get_game_info(this, game_id);
		}
		
		public string
		get_game_exec (int game_id) {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.get_game_exec(this, game_id);
		}
		
		public bool
		is_game_available (int game_id) {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.is_game_available(this, game_id);
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
		
		private void add_new_game (System system, string uri) {
			if (system.is_a_game(uri)) {
				var reference = system.get_game_reference_for_uri(uri);
				if (!get_game_exists_for_reference(system, reference)) {
					var cnn = open_connection();
					cnn.execute_non_select_command ("INSERT INTO games (id, systemid, ref, played, playedlast) VALUES (NULL, " + system.id.to_string("%i") + ", '" + reference + "', 0, 0)");
					cnn.close();
				}
				if (!get_uri_exists(uri)) {
					var game_id = get_game_id_for_reference(system, reference);
					add_uri_for_game(game_id, uri);
					game_updated(game_id);
				}
			}
		}
		
		private bool get_game_exists_for_reference (System system, string game_reference) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT games.id FROM games, systems WHERE games.systemid = systems.id AND games.ref = '" + game_reference + "' AND systems.id = " + system.id.to_string("%i"));
			var exists = (datamodel.get_n_rows() == 0);
			cnn.close();
			return exists;
		}
		
		private int get_game_id_for_reference (System system, string game_reference) throws Error {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT games.id FROM games, systems WHERE games.systemid = systems.id AND games.ref = '" + game_reference + "' AND systems.id = " + system.id.to_string("%i"));
			if (datamodel.get_n_rows() == 0) {
				cnn.close();
				//throw new Error("Lol");
				return 0;
			}
			else {
				var game_id = datamodel.get_value_at(0, 0).get_int();
				cnn.close();
				return game_id;
			}
		}
		
		
		
		public string get_game_uri (int game_id) {
			var uri = "";
			
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT uri FROM uris WHERE gameid = " + game_id.to_string("%i"));
			
			if (datamodel.get_n_rows() > 0) {
				uri = datamodel.get_value_at(0, 0).get_string();
			}
			
			cnn.close();
			
			return uri;
		}
		
		private void add_uri_for_game (int game_id, string uri) {
			var cnn = open_connection();
			cnn.execute_non_select_command ("INSERT INTO uris (id, uri, gameid) VALUES (NULL, '" + uri + "', " + game_id.to_string("%i") + ")");
			cnn.close();
		}
		
		protected bool get_uri_exists (string uri) {
			var cnn = open_connection();
			var datamodel = cnn.execute_select_command ("SELECT id FROM uri WHERE uri = '" + uri + "'");
			var exists = (datamodel.get_n_rows() != 0);
			cnn.close();
			return exists;
		}
	}
}
