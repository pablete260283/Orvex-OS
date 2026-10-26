-- Frozen schema of the first native launch delivery (before this audit).
CREATE TABLE settings (key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE TABLE favorites (profile TEXT NOT NULL,item_id TEXT NOT NULL,PRIMARY KEY(profile,item_id));
CREATE TABLE real_games (id TEXT PRIMARY KEY,name TEXT NOT NULL,platform TEXT NOT NULL,executable TEXT NOT NULL UNIQUE,trusted_hash TEXT,cover TEXT,backdrop TEXT,created_at TEXT NOT NULL);
CREATE TABLE play_sessions (id INTEGER PRIMARY KEY,game_id TEXT NOT NULL,started_at TEXT NOT NULL,ended_at TEXT,duration_ms INTEGER NOT NULL DEFAULT 0,status TEXT NOT NULL,exit_code INTEGER);
PRAGMA user_version=3;
