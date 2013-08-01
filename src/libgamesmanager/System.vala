namespace GamesManager {
	public abstract class System : Object {
		public Library? library { set; get; default = null; }
		public string id { construct; get; }
		
		public abstract GameInfo get_game_info (int id);
		public abstract string get_game_exec (int id);
		public abstract bool is_game_available (int id);
		public abstract void search_new_games ();
	}
}
