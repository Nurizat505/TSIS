import psycopg2
from config import DATABASE_ACCESS

def connect_db():
    return psycopg2.connect(**DATABASE_ACCESS)

def setup_tables():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY KEY,
                    nickname VARCHAR(30) UNIQUE NOT NULL
                );
                CREATE TABLE IF NOT EXISTS match_history (
                    id SERIAL PRIMARY KEY,
                    acc_id INTEGER REFERENCES accounts(id),
                    points INTEGER,
                    difficulty_level INTEGER,
                    date_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()

def record_match(name, score, lvl):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO accounts (nickname) VALUES (%s) ON CONFLICT (nickname) DO NOTHING", (name,))
            cur.execute("SELECT id FROM accounts WHERE nickname = %s", (name,))
            acc_id = cur.fetchone()[0]
            cur.execute("INSERT INTO match_history (acc_id, points, difficulty_level) VALUES (%s, %s, %s)", 
                        (acc_id, score, lvl))
            conn.commit()

def fetch_leaderboard():
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT a.nickname, m.points, m.difficulty_level, m.date_played 
                FROM match_history m JOIN accounts a ON a.id = m.acc_id 
                ORDER BY m.points DESC LIMIT 10
            """)
            return cur.fetchall()

def fetch_best_score(name):
    with connect_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT COALESCE(MAX(points), 0) FROM match_history m 
                JOIN accounts a ON a.id = m.acc_id WHERE a.nickname = %s
            """, (name,))
            res = cur.fetchone()
            return res[0] if res else 0