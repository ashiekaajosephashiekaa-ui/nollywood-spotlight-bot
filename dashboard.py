import sqlite3
from datetime import datetime
from flask import Flask, render_template_string
from config import DB_PATH, BOT_USERNAME, WEBSITE_URL

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Nollywood Spotlight — Dashboard</title>
<script src="https://cdn.tailwindcss.com"></script>
<meta http-equiv="refresh" content="30">
<style>
  body { background: #0a0a14; font-family: 'Inter', -apple-system, sans-serif; }
  .card { background: linear-gradient(135deg, #1a1a2e 0%, #16162a 100%); border: 1px solid #2a2a45; }
  .glow { box-shadow: 0 0 40px rgba(139, 92, 246, 0.15); }
  .gradient-text { background: linear-gradient(135deg, #a855f7 0%, #f59e0b 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
</style>
</head>
<body class="min-h-screen text-white p-6">

  <div class="max-w-6xl mx-auto">

    <!-- Header -->
    <div class="flex items-center justify-between mb-10">
      <div>
        <h1 class="text-4xl font-bold gradient-text">🎬 Nollywood Spotlight</h1>
        <p class="text-gray-400 mt-1">Live Bot Analytics Dashboard</p>
      </div>
      <a href="https://t.me/{{ bot_username }}" target="_blank"
         class="px-5 py-3 rounded-xl bg-purple-600 hover:bg-purple-700 transition font-semibold">
        Open Bot ↗
      </a>
    </div>

    <!-- Stat Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">

      <div class="card glow rounded-2xl p-8">
        <div class="text-gray-400 text-sm uppercase tracking-wider mb-2">Total Users</div>
        <div class="text-6xl font-bold gradient-text">{{ total_users }}</div>
        <div class="text-gray-500 text-sm mt-2">👥 All-time signups</div>
      </div>

      <div class="card rounded-2xl p-8">
        <div class="text-gray-400 text-sm uppercase tracking-wider mb-2">New Today</div>
        <div class="text-6xl font-bold text-emerald-400">{{ today_users }}</div>
        <div class="text-gray-500 text-sm mt-2">🆕 Last 24 hours</div>
      </div>

      <div class="card rounded-2xl p-8">
        <div class="text-gray-400 text-sm uppercase tracking-wider mb-2">Active (7d)</div>
        <div class="text-6xl font-bold text-amber-400">{{ week_active }}</div>
        <div class="text-gray-500 text-sm mt-2">⚡ Weekly activity</div>
      </div>

    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Recent Signups -->
      <div class="card rounded-2xl p-6">
        <h2 class="text-xl font-bold mb-4">📈 Recent Signups</h2>
        {% if recent %}
          {% for u in recent %}
          <div class="flex items-center justify-between py-3 border-b border-gray-800 last:border-0">
            <div>
              <div class="font-semibold">{{ u[2] or "Unknown" }}</div>
              <div class="text-gray-500 text-sm">@{{ u[1] or "no_username" }}</div>
            </div>
            <div class="text-gray-500 text-xs">{{ u[3] }}</div>
          </div>
          {% endfor %}
        {% else %}
          <p class="text-gray-500">No users yet.</p>
        {% endif %}
      </div>

      <!-- Top Referrers -->
      <div class="card rounded-2xl p-6">
        <h2 class="text-xl font-bold mb-4">🏆 Top Referrers</h2>
        {% if referrers %}
          {% for r in referrers %}
          <div class="flex items-center justify-between py-3 border-b border-gray-800 last:border-0">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center font-bold">{{ loop.index }}</div>
              <div class="font-semibold">User {{ r[0] }}</div>
            </div>
            <div class="text-amber-400 font-bold">{{ r[1] }} invites</div>
          </div>
          {% endfor %}
        {% else %}
          <p class="text-gray-500">No referrals yet.</p>
        {% endif %}
      </div>

    </div>

    <div class="text-center text-gray-600 text-sm mt-10">
      Last updated: {{ updated }} • Auto-refreshes every 30s •
      <a href="{{ website }}" class="text-purple-400 hover:underline" target="_blank">nollywoodspotlight.org</a>
    </div>

  </div>
</body>
</html>
"""

def query_db(sql, params=()):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

@app.route("/")
def index():
    total_users = query_db("SELECT COUNT(*) FROM users")
    total_users = total_users[0][0] if total_users else 0

    today_users = query_db(
        "SELECT COUNT(*) FROM users WHERE date(joined_at) = date('now')"
    )
    today_users = today_users[0][0] if today_users else 0

    week_active = query_db(
        "SELECT COUNT(*) FROM users WHERE last_active >= datetime('now', '-7 days')"
    )
    week_active = week_active[0][0] if week_active else 0

    recent = query_db(
        "SELECT user_id, username, first_name, joined_at FROM users "
        "ORDER BY joined_at DESC LIMIT 8"
    )

    referrers = query_db(
        "SELECT referrer_id, COUNT(*) as cnt FROM users "
        "WHERE referrer_id IS NOT NULL "
        "GROUP BY referrer_id ORDER BY cnt DESC LIMIT 5"
    )

    return render_template_string(
        HTML,
        total_users=total_users,
        today_users=today_users,
        week_active=week_active,
        recent=recent,
        referrers=referrers,
        updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        bot_username=BOT_USERNAME,
        website=WEBSITE_URL,
    )

@app.route("/health")
def health():
    return {"status": "ok"}, 200
