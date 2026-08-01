from graci import get_db

SQL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS players (
        player_id TEXT PRIMARY KEY,
        nickname  TEXT DEFAULT '',
        gold      INTEGER DEFAULT 0,
        gem       INTEGER DEFAULT 0,
        rank_points INTEGER DEFAULT 0,
        rank_tier TEXT DEFAULT '青铜',
        exp       INTEGER DEFAULT 0,
        level     INTEGER DEFAULT 1,
        joined_at TEXT DEFAULT (datetime('now','localtime')),
        last_checkin TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS inventory (
        player_id TEXT,
        item_id   TEXT,
        quantity  INTEGER DEFAULT 0,
        PRIMARY KEY (player_id, item_id)
    )""",
    """CREATE TABLE IF NOT EXISTS dungeon_progress (
        player_id   TEXT,
        dungeon_id  TEXT,
        completed   INTEGER DEFAULT 0,
        stars       INTEGER DEFAULT 0,
        PRIMARY KEY (player_id, dungeon_id)
    )""",
    """CREATE TABLE IF NOT EXISTS checkin_log (
        player_id TEXT,
        date      TEXT,
        PRIMARY KEY (player_id, date)
    )""",
    """CREATE TABLE IF NOT EXISTS explore_log (
        player_id  TEXT,
        country    TEXT,
        location   TEXT,
        discovered TEXT DEFAULT (datetime('now','localtime')),
        PRIMARY KEY (player_id, location)
    )""",
]

_db_instance = None


async def _get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = await get_db("解谜游戏")
        for stmt in SQL_STATEMENTS:
            await _db_instance.execute(stmt)
    return _db_instance


async def ensure_player(player_id: str, nickname: str = ""):
    db = await _get_db()
    existing = await db.fetchone("SELECT player_id FROM players WHERE player_id = ?", player_id)
    if not existing:
        await db.execute(
            "INSERT INTO players (player_id) VALUES (?)",
            player_id,
        )


async def get_player(player_id: str):
    db = await _get_db()
    row = await db.fetchone("SELECT * FROM players WHERE player_id = ?", player_id)
    if row:
        return dict(row)
    return None


async def update_player(player_id: str, **kwargs):
    db = await _get_db()
    sets = ", ".join(f"{k} = ?" for k in kwargs)
    vals = list(kwargs.values()) + [player_id]
    await db.execute(f"UPDATE players SET {sets} WHERE player_id = ?", *vals)


async def get_inventory(player_id: str):
    db = await _get_db()
    rows = await db.fetchall(
        "SELECT item_id, quantity FROM inventory WHERE player_id = ? AND quantity > 0",
        player_id,
    )
    return {row["item_id"]: row["quantity"] for row in rows}


async def add_item(player_id: str, item_id: str, qty: int = 1):
    db = await _get_db()
    await db.execute(
        "INSERT INTO inventory (player_id, item_id, quantity) VALUES (?, ?, ?) "
        "ON CONFLICT(player_id, item_id) DO UPDATE SET quantity = quantity + ?",
        player_id, item_id, qty, qty,
    )


async def remove_item(player_id: str, item_id: str, qty: int = 1):
    db = await _get_db()
    row = await db.fetchone(
        "SELECT quantity FROM inventory WHERE player_id = ? AND item_id = ?",
        player_id, item_id,
    )
    if row and row["quantity"] >= qty:
        await db.execute(
            "UPDATE inventory SET quantity = quantity - ? WHERE player_id = ? AND item_id = ?",
            qty, player_id, item_id,
        )
        return True
    return False


async def has_checkin_today(player_id: str) -> bool:
    db = await _get_db()
    from datetime import date
    today = date.today().isoformat()
    row = await db.fetchone(
        "SELECT 1 FROM checkin_log WHERE player_id = ? AND date = ?",
        player_id, today,
    )
    return row is not None


async def mark_checkin(player_id: str):
    db = await _get_db()
    from datetime import date
    today = date.today().isoformat()
    await db.execute(
        "INSERT INTO checkin_log (player_id, date) VALUES (?, ?)",
        player_id, today,
    )
    await db.execute(
        "UPDATE players SET last_checkin = ? WHERE player_id = ?",
        today, player_id,
    )


async def get_leaderboard(by: str = "gold", limit: int = 10):
    db = await _get_db()
    allowed = {"gold", "gem", "rank_points"}
    if by not in allowed:
        by = "gold"
    rows = await db.fetchall(
        f"SELECT player_id, nickname, {by} FROM players ORDER BY {by} DESC LIMIT ?",
        limit,
    )
    return [dict(r) for r in rows]


_RANK_ALLOWED = {"gold", "gem", "rank_points", "exp"}

async def get_rank(player_id: str, by: str = "rank_points") -> int:
    if by not in _RANK_ALLOWED:
        by = "rank_points"
    db = await _get_db()
    row = await db.fetchone(
        f"SELECT COUNT(*) + 1 AS rank FROM players WHERE {by} > "
        f"(SELECT COALESCE({by}, 0) FROM players WHERE player_id = ?)",
        player_id,
    )
    return row["rank"] if row else 0


async def get_dungeon_progress(player_id: str):
    db = await _get_db()
    rows = await db.fetchall(
        "SELECT dungeon_id, completed, stars FROM dungeon_progress WHERE player_id = ?",
        player_id,
    )
    return {row["dungeon_id"]: {"completed": row["completed"], "stars": row["stars"]} for row in rows}


async def complete_dungeon(player_id: str, dungeon_id: str, stars: int):
    db = await _get_db()
    existing = await db.fetchone(
        "SELECT stars FROM dungeon_progress WHERE player_id = ? AND dungeon_id = ?",
        player_id, dungeon_id,
    )
    if existing:
        if stars > existing["stars"]:
            await db.execute(
                "UPDATE dungeon_progress SET completed = 1, stars = ? WHERE player_id = ? AND dungeon_id = ?",
                stars, player_id, dungeon_id,
            )
    else:
        await db.execute(
            "INSERT INTO dungeon_progress (player_id, dungeon_id, completed, stars) VALUES (?, ?, 1, ?)",
            player_id, dungeon_id, stars,
        )


async def get_explored_locations(player_id: str):
    db = await _get_db()
    rows = await db.fetchall(
        "SELECT country, location FROM explore_log WHERE player_id = ?",
        player_id,
    )
    return {row["location"]: row["country"] for row in rows}


async def mark_location_discovered(player_id: str, country: str, location: str):
    db = await _get_db()
    await db.execute(
        "INSERT OR IGNORE INTO explore_log (player_id, country, location) VALUES (?, ?, ?)",
        player_id, country, location,
    )
