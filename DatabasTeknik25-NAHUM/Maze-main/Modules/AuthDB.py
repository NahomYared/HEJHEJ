# Modules/AuthDB.py — SQL-backend (kompatibel signatur med pickle-versionen)
import os, sqlite3, hashlib, secrets, time, pickle
from typing import List, Tuple, Optional, Any, Iterable

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "game.db")
# För engångsmigrering från tidigare pickle (om sådan fanns)
PICKLE_PATH = os.path.join(DB_DIR, "game.pickle")

# ---------- Intern SQL-hjälp ----------

def _connect() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _exec(conn: sqlite3.Connection, sql: str, params: Iterable[Any] = ()):
    cur = conn.execute(sql, params)
    return cur

def _hash_password(password: str, salt: bytes) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)

def _table_exists(conn: sqlite3.Connection, name: str) -> bool:
    row = _exec(conn, "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
    return row is not None

def _ensure_schema(conn: sqlite3.Connection):
    _exec(conn, """
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        pw_salt BLOB NOT NULL,
        pw_hash BLOB NOT NULL,
        created_at INTEGER NOT NULL
    )""")
    _exec(conn, """
    CREATE TABLE IF NOT EXISTS scores(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        level INTEGER NOT NULL,
        time_sec INTEGER NOT NULL,
        created_at INTEGER NOT NULL
    )""")
    _exec(conn, """
    CREATE TABLE IF NOT EXISTS progress(
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        country_id TEXT NOT NULL,
        PRIMARY KEY(user_id, country_id)
    )""")
    conn.commit()

def _maybe_migrate_from_pickle(conn: sqlite3.Connection):
    """Migrera från tidigare pickle-fil om DB är tom och pickle finns."""
    # Migrera bara om users-tabellen är tom
    count = _exec(conn, "SELECT COUNT(*) FROM users").fetchone()[0]
    if count != 0: 
        return
    if not os.path.exists(PICKLE_PATH):
        return
    try:
        with open(PICKLE_PATH, "rb") as f:
            db = pickle.load(f)
    except Exception:
        return
    # förväntad struktur i pickle: {"users":[{id,username,pw_salt,pw_hash,created_at,progress:[]},...],
    #                               "scores":[{id,user_id,level,time_sec,created_at},...]}
    users = db.get("users", [])
    scores = db.get("scores", [])
    # infoga users
    for u in users:
        _exec(conn, "INSERT OR IGNORE INTO users(id,username,pw_salt,pw_hash,created_at) VALUES(?,?,?,?,?)",
              (int(u["id"]), u["username"], u["pw_salt"], u["pw_hash"], int(u.get("created_at", int(time.time())))))
        for c in u.get("progress", []) or []:
            _exec(conn, "INSERT OR IGNORE INTO progress(user_id, country_id) VALUES(?,?)", (int(u["id"]), str(c)))
    # infoga scores
    for s in scores:
        _exec(conn, "INSERT INTO scores(id,user_id,level,time_sec,created_at) VALUES(?,?,?,?,?)",
              (int(s["id"]), int(s["user_id"]), int(s["level"]), int(s["time_sec"]), int(s.get("created_at", int(time.time())))))
    conn.commit()

# ---------- Publikt API (samma som tidigare) ----------

def init_db():
    """Skapa tabeller och migrera ev. pickle-data en gång."""
    conn = _connect()
    try:
        _ensure_schema(conn)
        _maybe_migrate_from_pickle(conn)
    finally:
        conn.close()

def create_user(username: str, password: str):
    username = (username or "").strip()
    password = (password or "")
    if len(username) < 3 or len(password) < 3:
        return False, "Användarnamn och lösenord måste vara minst 3 tecken."
    conn = _connect()
    try:
        # finns?
        row = _exec(conn, "SELECT id FROM users WHERE username=?", (username,)).fetchone()
        if row:
            return False, "Användarnamnet är upptaget."
        salt = secrets.token_bytes(16)
        pw_hash = _hash_password(password, salt)
        ts = int(time.time())
        cur = _exec(conn, "INSERT INTO users(username,pw_salt,pw_hash,created_at) VALUES(?,?,?,?)",
                    (username, salt, pw_hash, ts))
        conn.commit()
        return True, {"user_id": cur.lastrowid}
    finally:
        conn.close()

def verify_user(username: str, password: str):
    conn = _connect()
    try:
        row = _exec(conn, "SELECT id,pw_salt,pw_hash FROM users WHERE username=?", (username.strip(),)).fetchone()
        if not row:
            return False, "Hittar inte användaren."
        uid, salt, pw_hash = row
        if _hash_password(password, salt) == pw_hash:
            return True, {"user_id": uid}
        return False, "Fel lösenord."
    finally:
        conn.close()

def record_score(user_id: int, level: int, time_sec: int):
    conn = _connect()
    try:
        _exec(conn, "INSERT INTO scores(user_id,level,time_sec,created_at) VALUES(?,?,?,?)",
              (int(user_id), int(level), int(time_sec), int(time.time())))
        conn.commit()
    finally:
        conn.close()

def top_times(level: int, limit: int = 10) -> List[Tuple[str, int]]:
    """[(username, best_time_sec), ...] sorterat på kortast tid."""
    conn = _connect()
    try:
        # Minsta tid per user på angiven level
        rows = _exec(conn, """
            SELECT u.username, MIN(s.time_sec) AS best
            FROM scores s
            JOIN users u ON u.id = s.user_id
            WHERE s.level = ?
            GROUP BY s.user_id
            ORDER BY best ASC
            LIMIT ?
        """, (int(level), int(limit))).fetchall()
        return [(r[0], int(r[1])) for r in rows]
    finally:
        conn.close()

# ---------- Progress (länder) ----------

def add_country_progress(user_id: int, country_id: str) -> bool:
    conn = _connect()
    try:
        _exec(conn, "INSERT OR IGNORE INTO progress(user_id, country_id) VALUES(?,?)",
              (int(user_id), str(country_id)))
        conn.commit()
        return True
    finally:
        conn.close()

def remove_country_progress(user_id: int, country_id: str) -> bool:
    conn = _connect()
    try:
        _exec(conn, "DELETE FROM progress WHERE user_id=? AND country_id=?",
              (int(user_id), str(country_id)))
        conn.commit()
        return True
    finally:
        conn.close()

def get_progress(user_id: int) -> List[str]:
    conn = _connect()
    try:
        rows = _exec(conn, "SELECT country_id FROM progress WHERE user_id=? ORDER BY country_id", (int(user_id),)).fetchall()
        return [r[0] for r in rows]
    finally:
        conn.close()

def has_access(user_id: int, country_id: str) -> bool:
    conn = _connect()
    try:
        row = _exec(conn, "SELECT 1 FROM progress WHERE user_id=? AND country_id=?",
                    (int(user_id), str(country_id))).fetchone()
        return row is not None
    finally:
        conn.close()

def user_id_by_username(username: str) -> Optional[int]:
    conn = _connect()
    try:
        row = _exec(conn, "SELECT id FROM users WHERE username=?", (username.strip(),)).fetchone()
        return int(row[0]) if row else None
    finally:
        conn.close()
