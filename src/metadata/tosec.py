#!/usr/bin/python3
#    tosec.py A Python module to use TOSEC data files as a SQLite database.
#    Copyright (C) 2013 Adrien Plazas
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#    
#    Adrien Plazas <mailto:kekun.plazas@laposte.net>

from gi.repository import GamesManager

import re
import sqlite3
import hashlib
import os.path
import datetime

class TOSEC:
	'''A class to ease the use of TOSEC data files as a SQLite database.'''
	def __init__(self, directory):
		self.path = os.path.join(directory, "tosec.db")
		
		# Init the database
		db = sqlite3.connect(self.path)
		db.execute('''CREATE TABLE IF NOT EXISTS systems
				          (
				            id TEXT PRIMARY KEY,
				            version TEXT
				          )''')
		db.execute('''CREATE TABLE IF NOT EXISTS games
				          (
				            id INTEGER PRIMARY KEY,
				            title TEXT,
				            flags TEXT,
				            system TEXT,
				            UNIQUE (title, flags, system)
				          )''')
		db.execute('''CREATE TABLE IF NOT EXISTS roms
				          (
				            id INTEGER PRIMARY KEY,
				            flags TEXT,
				            size INTEGER,
				            crc TEXT,
				            md5 TEXT,
				            sha1 TEXT,
				            game INTEGER,
				            FOREIGN KEY(game) REFERENCES game(id)
				          )''')
		db.commit()
		db.close()
	
	def parse_file(self, file, system):
		'''Add a data file for the given system and update the database if this data file's version is newer than the previous one for the given system or simply add it if there was no database for this system.'''
		words = tosec_to_words(file)
		info, games = get_games_from_words(words)
		
		db = sqlite3.connect(self.path)
		
		# If the info don't have a version, it is not valid and the file shouldn't be added
		if not "version" in info:
			return False
		
		new_version = info["version"]
		
		# Check the version actually in the database
		actual_version = None
		for row in db.execute('SELECT version FROM systems WHERE id = ?', [system]):
			actual_version = row[0]
		
		# If the old version is more recent thab the new one, the new one shouldn't be added
		if actual_version and datefromiso(actual_version) >= datefromiso(new_version):
			return False
		
		# What if we have to update the version instead of adding it ?
		if actual_version:
			db.execute('UPDATE systems SET version = ? WHERE id = ?', [new_version, system])
		else:
			db.execute('INSERT INTO systems (id, version) VALUES (?, ?)', [system, new_version])
		
		for game in games:
			rom = game["rom"]
			title, game_flags, rom_flags = split_game_title(game["name"])
			
			game_id = None
			
			# Adding game
			game_info = [title, game_flags, system]
			for row in db.execute('SELECT id FROM games WHERE title = ? AND flags = ? AND system = ?', game_info):
				game_id = row[0]
			if not game_id:
				db.execute('INSERT INTO games(id, title, flags, system) VALUES (NULL, ?, ?, ?)', game_info)
				for row in db.execute('SELECT id FROM games WHERE title = ? AND flags = ? AND system = ?', game_info):
					game_id = row[0]
			
			# Adding rom
			rom_info = [rom_flags, rom["size"], rom["crc"], rom["md5"], rom["sha1"]]
			rom_exists = False
			for row in db.execute('SELECT id FROM roms WHERE flags = ? AND size = ? AND crc = ? AND md5 = ? AND sha1 = ?', rom_info):
				rom_exists = True
			if not rom_exists:
				rom_info.append(game_id)
				rom_info = [rom_flags, rom["size"], rom["crc"], rom["md5"], rom["sha1"], game_id]
				db.execute('INSERT INTO roms(id, flags, size, crc, md5, sha1, game) VALUES (NULL, ?, ?, ?, ?, ?, ?)', rom_info)
		
		db.commit()
		db.close()
		return True
	
	def parse_file_with_vala(self, file, system):
		'''Add a data file for the given system and update the database if this data file's version is newer than the previous one for the given system or simply add it if there was no database for this system.'''
		document = GamesManager.Glrmame.Document(path = file)
		
		db = sqlite3.connect(self.path)
		
		# If the info don't have a version, it is not valid and the file shouldn't be added
		if document.version == None:
			return False
		
		new_version = document.version
		
		# Check the version actually in the database
		actual_version = None
		for row in db.execute('SELECT version FROM systems WHERE id = ?', [system]):
			actual_version = row[0]
		
		# If the old version is more recent thab the new one, the new one shouldn't be added
		if actual_version and datefromiso(actual_version) >= datefromiso(new_version):
			return False
		
		# What if we have to update the version instead of adding it ?
		if actual_version:
			db.execute('UPDATE systems SET version = ? WHERE id = ?', [new_version, system])
		else:
			db.execute('INSERT INTO systems (id, version) VALUES (?, ?)', [system, new_version])
		
		for game in document.games:
			rom = game.rom
			title, game_flags, rom_flags = split_game_title(game.name)
			
			game_id = None
			
			# Adding game
			game_info = [title, game_flags, system]
			for row in db.execute('SELECT id FROM games WHERE title = ? AND flags = ? AND system = ?', game_info):
				game_id = row[0]
			if not game_id:
				db.execute('INSERT INTO games(id, title, flags, system) VALUES (NULL, ?, ?, ?)', game_info)
				for row in db.execute('SELECT id FROM games WHERE title = ? AND flags = ? AND system = ?', game_info):
					game_id = row[0]
			
			# Adding rom
			rom_info = [rom_flags, rom.size, rom.crc, rom.md5, rom.sha1]
			rom_exists = False
			for row in db.execute('SELECT id FROM roms WHERE flags = ? AND size = ? AND crc = ? AND md5 = ? AND sha1 = ?', rom_info):
				rom_exists = True
			if not rom_exists:
				rom_info.append(game_id)
				rom_info = [rom_flags, rom["size"], rom["crc"], rom["md5"], rom["sha1"], game_id]
				db.execute('INSERT INTO roms(id, flags, size, crc, md5, sha1, game) VALUES (NULL, ?, ?, ?, ?, ?, ?)', rom_info)
		
		db.commit()
		db.close()
		return True
	
	def get_rom_id(self, rom):
		input = open(rom, "rb")
		data = input.read()
		
		md5 = hashlib.md5(data).hexdigest()
		sha1 = hashlib.sha1(data).hexdigest()
		
		db = sqlite3.connect(self.path)
		
		id = None
		for row in db.execute('SELECT id FROM roms WHERE md5 = ? AND sha1 = ?', [md5, sha1]):
			id = row[0]
		
		db.close()
		return id
	
	def get_game_title(self, rom):
		id = self.get_rom_id(rom)
		
		if id:
			db = sqlite3.connect(self.path)
			title = None
			for row in db.execute('SELECT title FROM games, roms WHERE roms.game = games.id AND roms.id = ?', [id]):
				title = row[0]
			db.close()
		return os.path.basename(rom)

def tosec_to_words(file):
	input = open(file, "r")
	data = input.read()
	result = re.split(r'''((?:[^ \n\r\t"]|"[^"]*")+)''', data)
	
	return result[1::2]

def get_games_from_words(words):
	'''Transform a list of words into a tuple containing the clrmamepro object and a list of the game objects both as nested dictionnaries having the same structure than the original TOSEC file'''
	clrmamepro = None
	games = []
	game = {}
	
	last_path = ""
	path = ""
	tag = None
	for word in words:
		if last_path != "" and path == "":
			if "game" in game:
				games.append(game["game"])
			elif "clrmamepro" in game:
				clrmamepro = game["clrmamepro"]
			game = {}
		else:
			last_path = path
		if not tag:
			if word == ")":
				# Go up in the dictionaries tree
				splitted_path = path.split(" ")
				path = ""
				for element in splitted_path[:-1]:
					if path == "":
						path = element
					else:
						path = path + " " + element
			else:
				tag = word
		else:
			if word == "(":
				# Add a new depth in the dictionaries tree
				dict = game
				for element in path.split(" "):
					if element != "":
						dict = dict[element]
				dict[tag] = {}
				if path == "":
					path = tag
				else:
					path = path + " " + tag
			else:
				dict = game
				for element in path.split(" "):
					dict = dict[element]
				dict[tag] = word
			tag = None
	
	return (clrmamepro, games)

def split_game_title(game):
	'''Return a tuple containg the game title, the game flags and the ROM flags'''
	title = ""
	game_flags = ""
	rom_flags = ""
	result = re.match(r'''^"([^\(\)\[\]]+) .*?(\(?[^\[\]]*\)?)(\[?[^\(\)]*\]?)"''', game)
	if result:
		title = result.group(1)
		game_flags = result.group(2)
		rom_flags = result.group(3)
	return (title, game_flags, rom_flags)

def datefromiso(isoformat):
	date = isoformat.split('-')
	return datetime.date(int(date[0]), int(date[1]), int(date[2]))

