import psycopg2
from config import load_config

def connect():
    try:
        return psycopg2.connect(**load_config())
    except Exception as e:
        print("DB error:", e)
        return None