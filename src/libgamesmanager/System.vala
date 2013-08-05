namespace GamesManager {
	public abstract class System : Object {
		private Library? _library = null;
		
		public Library? library {
			get { return _library; }
			set {
				_library = value;
				if (_library != null) {
					_library.add_system(this);
					init_system();
				}
			}
		}
		
		public int64 id { private set; get; }
		public string reference { construct; get; }
		
		
		public abstract GameInfo get_game_info (int game_id);
		protected GameInfo _get_game_info (int game_id) {
			var info = new GameInfo();
			/*
			if (library != null) {
				var cnn = library.open_connection();
				
				var datamodel = cnn.execute_select_command ("SELECT games.id, games.title, games.developer, games.icon, games.cover, games.released systems.ref, games.genre, games.played, games.playedlast, games.online, games.description, games.rank, games.players FROM games, systems WHERE games.systemid = systems.id AND games.id = " + game_id.to_string("%i"));
				
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
					// Throw error
				}
				
				cnn.close();
			}*/
			return info;
		}
		
		private void init_system () {
			if (library != null) {
				var cnn = library.open_connection();
				var datamodel = cnn.execute_select_command ("SELECT id FROM systems WHERE ref = '" + reference + "'");
				
				if (datamodel.get_n_rows() > 0) {
					this.id = datamodel.get_value_at(0, 0).get_int();
				}
				else {
					cnn.execute_non_select_command ("INSERT INTO systems (id, ref) VALUES (NULL, '" + reference + "')");
					datamodel = cnn.execute_select_command ("SELECT id FROM systems WHERE ref = '" + reference + "'");
					if (datamodel.get_n_rows() > 0) {
						this.id = datamodel.get_value_at(0, 0).get_int();
					}
					else {
						stdout.printf("error: can't get the system id\n");
					}
				}
				
				cnn.close();
			}
		}
		
		public abstract string get_game_exec (int game_id);
		public abstract bool is_game_available (int game_id);
		
		public abstract void search_new_games ();
	}
}
