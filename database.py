import sqlite3
import json
from datetime import datetime, timedelta

DB_NAME = "evolution.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    # Основная таблица игроков
    cur.execute('''
        CREATE TABLE IF NOT EXISTS players (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            stage INTEGER DEFAULT 0,
            day INTEGER DEFAULT 1,
            strength INTEGER DEFAULT 10,
            intelligence INTEGER DEFAULT 10,
            endurance INTEGER DEFAULT 10,
            speed INTEGER DEFAULT 10,
            luck INTEGER DEFAULT 10,
            resources INTEGER DEFAULT 100,
            exp INTEGER DEFAULT 0,
            total_exp INTEGER DEFAULT 0,
            health INTEGER DEFAULT 100,
            max_health INTEGER DEFAULT 100,
            last_played TEXT,
            daily_bonus TEXT,
            achievements TEXT DEFAULT '[]',
            completed_events TEXT DEFAULT '[]',
            died INTEGER DEFAULT 0,
            donates INTEGER DEFAULT 0
        )
    ''')
    
    # Таблица событий (история)
    cur.execute('''
        CREATE TABLE IF NOT EXISTS events_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_id INTEGER,
            result TEXT,
            date TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def get_player(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT * FROM players WHERE user_id = ?", (user_id,))
    data = cur.fetchone()
    conn.close()
    return data

def create_player(user_id, username):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO players (user_id, username, last_played, daily_bonus) 
           VALUES (?, ?, ?, ?)""",
        (user_id, username, datetime.now().isoformat(), 
         (datetime.now() - timedelta(days=1)).isoformat())
    )
    conn.commit()
    conn.close()

def update_player(user_id, **kwargs):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    for key, value in kwargs.items():
        cur.execute(f"UPDATE players SET {key} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()
    conn.close()

def get_achievements(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT achievements FROM players WHERE user_id = ?", (user_id,))
    data = cur.fetchone()
    conn.close()
    return json.loads(data[0]) if data else []

def add_achievement(user_id, ach_name):
    achievements = get_achievements(user_id)
    if ach_name not in achievements:
        achievements.append(ach_name)
        update_player(user_id, achievements=json.dumps(achievements))
        return True
    return False

def get_completed_events(user_id):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT completed_events FROM players WHERE user_id = ?", (user_id,))
    data = cur.fetchone()
    conn.close()
    return json.loads(data[0]) if data else []

def add_event_to_history(user_id, event_id, result):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO events_history (user_id, event_id, result, date) VALUES (?, ?, ?, ?)",
        (user_id, event_id, result, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def reset_daily_events(user_id):
    """Очищает список выполненных событий в начале дня"""
    update_player(user_id, completed_events=json.dumps([]))
