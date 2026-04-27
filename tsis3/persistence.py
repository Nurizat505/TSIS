import json
import os

def load_json(filename, default):
    if not os.path.exists(filename):
        return default
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def update_leaderboard(name, score, distance):
    data = load_json('leaderboard.json', [])
    data.append({"name": name, "score": int(score), "distance": int(distance)})
    data = sorted(data, key=lambda x: x['score'], reverse=True)[:10]
    save_json('leaderboard.json', data)