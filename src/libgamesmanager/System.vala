namespace GamesManager {
	public abstract class System : Object {
		public Library? library { set; get; default = null; }
		public string id { construct; get; }
		
		public abstract GameInfo get_game_info (int id);
	}
}
