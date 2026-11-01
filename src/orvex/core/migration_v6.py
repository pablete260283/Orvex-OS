"""Additive foundation schema. Existing games, preferences and history stay authoritative."""

STATEMENTS = [
    """CREATE TABLE profiles (
        id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('adult','child')),
        name TEXT NOT NULL, max_age INTEGER,
        enabled INTEGER NOT NULL DEFAULT 1 CHECK(enabled IN (0,1)),
        created_at TEXT NOT NULL,
        CHECK((kind='adult' AND max_age IS NULL) OR
              (kind='child' AND typeof(max_age)='integer' AND max_age BETWEEN 0 AND 17)))""",
    "INSERT INTO profiles(id,kind,name,max_age,created_at) VALUES('adult','adult','Adulto',NULL,CURRENT_TIMESTAMP)",
    "INSERT INTO profiles(id,kind,name,max_age,created_at) VALUES('child','child','Infantil',7,CURRENT_TIMESTAMP)",
    "ALTER TABLE play_sessions ADD COLUMN profile_id TEXT REFERENCES profiles(id)",
    """CREATE TABLE content_items (
        id TEXT PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('game','movie','series','episode','application')),
        title TEXT NOT NULL, alternate_title TEXT NOT NULL DEFAULT '',
        format TEXT NOT NULL DEFAULT '', source_type TEXT NOT NULL,
        source_ref TEXT NOT NULL, source_key TEXT NOT NULL,
        metadata TEXT NOT NULL DEFAULT '{}', cover TEXT, backdrop TEXT,
        age INTEGER CHECK(age IS NULL OR (typeof(age)='integer' AND age BETWEEN 0 AND 21)),
        import_state TEXT NOT NULL DEFAULT 'registered' CHECK(import_state IN ('registered','available','missing','pending')),
        hidden INTEGER NOT NULL DEFAULT 0 CHECK(hidden IN (0,1)),
        parent_id TEXT REFERENCES content_items(id) ON DELETE RESTRICT,
        created_at TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 0,
        UNIQUE(source_type,source_key),
        CHECK((kind='episode' AND parent_id IS NOT NULL) OR (kind!='episode' AND parent_id IS NULL)))""",
    """CREATE TABLE game_catalog_details (
        game_id TEXT PRIMARY KEY REFERENCES real_games(id) ON DELETE CASCADE,
        alternate_title TEXT NOT NULL DEFAULT '',
        age INTEGER CHECK(age IS NULL OR (typeof(age)='integer' AND age BETWEEN 0 AND 21)),
        import_state TEXT NOT NULL DEFAULT 'registered' CHECK(import_state IN ('registered','available','missing','pending')),
        revision INTEGER NOT NULL DEFAULT 0)""",
    """CREATE TABLE content_activity (
        id TEXT PRIMARY KEY, profile_id TEXT NOT NULL REFERENCES profiles(id),
        content_id TEXT NOT NULL, event TEXT NOT NULL CHECK(event IN ('opened','started','finished')),
        occurred_at TEXT NOT NULL, duration_ms INTEGER CHECK(duration_ms IS NULL OR duration_ms>=0),
        evidence TEXT NOT NULL CHECK(evidence IN ('manual','observed')))""",
    """CREATE TABLE metadata_proposals (
        id TEXT PRIMARY KEY, content_id TEXT NOT NULL, changes TEXT NOT NULL,
        source TEXT NOT NULL, expected_fingerprint TEXT NOT NULL,
        state TEXT NOT NULL DEFAULT 'pending' CHECK(state IN ('pending','approved','rejected')),
        created_at TEXT NOT NULL, decided_at TEXT, decided_by TEXT REFERENCES profiles(id))""",
    "CREATE INDEX content_kind_format ON content_items(kind,format)",
    "CREATE INDEX content_parent ON content_items(parent_id)",
    "CREATE INDEX activity_profile_recent ON content_activity(profile_id,occurred_at DESC)",
    "CREATE INDEX sessions_profile_recent ON play_sessions(profile_id,started_at DESC)",
    "CREATE INDEX proposals_content_state ON metadata_proposals(content_id,state)",
    """CREATE TRIGGER catalog_id_new BEFORE INSERT ON content_items
        WHEN EXISTS(SELECT 1 FROM real_games WHERE id=NEW.id)
        BEGIN SELECT RAISE(ABORT,'content id already used by a game'); END""",
    """CREATE TRIGGER catalog_id_legacy BEFORE INSERT ON real_games
        WHEN EXISTS(SELECT 1 FROM content_items WHERE id=NEW.id)
        BEGIN SELECT RAISE(ABORT,'game id already used by content'); END""",
]
