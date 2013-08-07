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
			
			try {
				cnn.execute_non_select_command (systems_table);
				cnn.execute_non_select_command (games_table);
				cnn.execute_non_select_command (uris_table);
			}
			catch {
				stderr.printf("Error: can't initiate the database.");
			}
			
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
		
		/**
		 * Add a game system to your game library.
		 * Each game system must have a _unique_ reference.
		 */
		public void
		add_system (System system) {
			if (! systems.contains(system.reference)) {
				systems.insert(system.reference, system);
				
				var cnn = open_connection();
				try {
					var datamodel = cnn.execute_select_command ("SELECT id FROM systems WHERE ref = '" + system.reference + "'");
					
					if (datamodel.get_n_rows() > 0) {
						system.id = datamodel.get_value_at(0, 0).get_int();
					}
					else {
						stdout.printf("Add system %s to the DB\n", system.reference);
						cnn.execute_non_select_command ("INSERT INTO systems (id, ref) VALUES (NULL, '" + system.reference + "')");
						datamodel = cnn.execute_select_command ("SELECT id FROM systems WHERE ref = '" + system.reference + "'");
						if (datamodel.get_n_rows() > 0) {
							system.id = datamodel.get_value_at(0, 0).get_int();
						}
						else {
							stderr.printf("Error: can't get the identifier for system %s.\n", system.reference);
						}
					}
				}
				catch (Error e) {
					stderr.printf("Error: can't add the system %s to the database.\n", system.reference);
				}
				
				cnn.close();
			}
		}
		
		/**
		 * Get the reference of the system of a game.
		 */
		private string
		get_system_reference (int game_id) throws Error {
			var cnn = open_connection();
			try {
				var datamodel = cnn.execute_select_command ("SELECT systems.ref FROM games, systems WHERE games.systemid = systems.id AND games.id = " + game_id.to_string("%i"));
				
				var reference = datamodel.get_value_at(0, 0).get_string();
				cnn.close();
				return reference;
			}
			catch (Error e) {
				stderr.printf("Error: can't get the system reference for the game identifier %i.\n", game_id);
				cnn.close();
				throw e;
			}
		}
		
		/**
		 * Search for new games on the filesystem in the g.
		 * If new games are found, they are added.
		 */
		public void
		search_new_games (string path = Environment.get_home_dir()) {
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
				var file = File.new_for_path(path);
				if (file.query_exists())
					search_new_games_in_path(standard, file);
			}
			
			if (applications.length() > 0) {
				var application_dirs = new List<File>();
				
				application_dirs.append (File.new_for_path(Environment.get_user_data_dir()).get_child("applications"));
				
				foreach (string system_data_dir in Environment.get_system_data_dirs()) {
					application_dirs.append (File.new_for_path(system_data_dir).get_child("applications"));
				}
				
				foreach (File application_dir in application_dirs) {
					if (application_dir.query_exists())
						search_new_games_in_path(applications, application_dir);
				}
			}
		}
		
		private void
		search_new_games_in_path (List<System> systems, File file) {
			foreach (System system in systems)
				add_new_game (system, file.get_uri ());
			
			var file_type = file.query_file_type (FileQueryInfoFlags.NONE);
			
			if (file_type == FileType.DIRECTORY) {
				try {
					var enumerator = file.enumerate_children (FileAttribute.STANDARD_NAME, 0);
					
					FileInfo file_info;
					while ((file_info = enumerator.next_file ()) != null) {
						search_new_games_in_path (systems, file.get_child (file_info.get_name ()));
					}
				}
				catch (Error e) {
					stderr.printf("Error: can't enumerate children of the file %s.\n", file.get_path());
				}
			}
		}
		
		/*
		 * Game informations getters
		 */
		
		public List<int>
		get_games_id () {
			var cnn = open_connection();
			
			var ids = new List<int>();
			
			try {
				var datamodel = cnn.execute_select_command ("SELECT id FROM games");
				
				int rows = datamodel.get_n_rows();
				
				for (int row = 0 ; row < rows ; row++ ) {
					ids.append(datamodel.get_value_at(0, row).get_int());
				}
			}
			catch (Error e) {
				stderr.printf("Error: can't retrieve game identifiers from the database.\n");
			}
			
			cnn.close();
			
			return ids;
		}
		
		public GameInfo
		get_game_info (int game_id) throws Error {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.get_game_info(this, game_id);
		}
		
		public string
		get_game_exec (int game_id) throws Error {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.get_game_exec(this, game_id);
		}
		
		public bool
		query_is_game_available (int game_id) throws Error {
			var system_ref = get_system_reference(game_id);
			var system = systems.get(system_ref);
			return system.query_is_game_available(this, game_id);
		}
		
		/*
		 * Game informations setters
		 */
		
		public void
		update_game_play_time (int game_id, double start, double end) {
			var cnn = open_connection();
			
			try {
				var datamodel = cnn.execute_select_command ("SELECT played FROM games WHERE id = " + game_id.to_string("%i"));
			
				if (datamodel.get_n_rows() > 0) {
					var time_played =  datamodel.get_value_at(0, 0).get_double();
					time_played += end - start;
				
					cnn.execute_non_select_command ("UPDATE games SET played = " + time_played.to_string() + ", playedlast = " + end.to_string() + " WHERE id = " + game_id.to_string("%i"));
				
					this.game_updated (game_id);
				}
			}
			catch (Error e) {
				stderr.printf("Error: can't update the play time for game identifier %i.\n", game_id);
			}
			
			cnn.close();
		}
		
		private void
		add_new_game (System system, string uri) {
			if (system.query_is_a_game(uri)) {
				var reference = system.get_game_reference_for_uri(uri);
				if (!query_game_exists_for_reference(system, reference)) {
					var cnn = open_connection();
					try {
						stdout.printf("Add game %s for system %s to the DB\n", reference, system.reference);
						cnn.execute_non_select_command ("INSERT INTO games (id, systemid, ref, played, playedlast) VALUES (NULL, " + system.id.to_string("%i") + ", '" + reference + "', 0, 0)");
					}
					catch (Error e) {
						stderr.printf("Error: can't add game for reference %s and URI %s to the database.\n", reference, uri);
					}
					cnn.close();
				}
				if (!query_uri_exists(uri)) {
					try {
						var game_id = get_game_id_for_reference(system, reference);
						add_uri_for_game(game_id, uri);
						game_updated(game_id);
					}
					catch (Error e) {
						stderr.printf("Error: can't add URI %s to game reference %s for system %s.\n", uri, reference, system.reference);
					}
				}
			}
		}
		
		private bool
		query_game_exists_for_reference (System system, string game_reference) {
			var cnn = open_connection();
			try {
				var datamodel = cnn.execute_select_command ("SELECT games.id FROM games, systems WHERE games.systemid = systems.id AND games.ref = '" + game_reference + "' AND systems.id = " + system.id.to_string("%i"));
				var exists = (datamodel.get_n_rows() != 0);
				cnn.close();
				return exists;
			}
			catch (Error e) {
				cnn.close();
				return false;
			}
		}
		
		private int
		get_game_id_for_reference (System system, string game_reference) throws Error {
			var cnn = open_connection();
			try {
				var datamodel = cnn.execute_select_command ("SELECT games.id FROM games, systems WHERE games.systemid = systems.id AND games.ref = '" + game_reference + "' AND systems.id = " + system.id.to_string("%i"));
				var game_id = datamodel.get_value_at(0, 0).get_int();
				cnn.close();
				return game_id;
			}
			catch (Error e) {
				stderr.printf("Error: can't get the game identifiers for reference %s on system %s.\n", game_reference, system.reference);
				cnn.close();
				throw e;
			}
		}
		
		
		
		public string get_game_uri (int game_id) throws Error {
			var uri = "";
			
			var cnn = open_connection();
			
			try {
				var datamodel = cnn.execute_select_command ("SELECT uri FROM uris WHERE gameid = " + game_id.to_string("%i"));
			
				if (datamodel.get_n_rows() > 0) {
					uri = datamodel.get_value_at(0, 0).get_string();
				}
				
				cnn.close();
				
				return uri;
			}
			catch (Error e) {
				stderr.printf("Error: can't get the URI for the game identifier %i.\n", game_id);
				cnn.close();
				throw e;
			}
		}
		
		private void add_uri_for_game (int game_id, string uri) {
			var cnn = open_connection();
			try {
				stdout.printf("Add uri %s to game %i to the DB\n", uri, game_id);
				cnn.execute_non_select_command ("INSERT INTO uris (id, uri, gameid) VALUES (NULL, '" + uri + "', " + game_id.to_string("%i") + ")");
			}
			catch (Error e) {
				stderr.printf("Error: can't add URI %s to thegame identifiers %i.\n", uri, game_id);
			}
			cnn.close();
		}
		
		protected bool query_uri_exists (string uri) {
			var cnn = open_connection();
			try {
				var datamodel = cnn.execute_select_command ("SELECT id FROM uris WHERE uri = '" + uri + "'");
				var exists = (datamodel.get_n_rows() != 0);
				cnn.close();
				return exists;
			}
			catch (Error e) {
				cnn.close();
				return false;
			}
		}
	}
}
