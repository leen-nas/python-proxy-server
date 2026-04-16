#author:Antonio
from flask import Flask, jsonify, request, render_template_string
from cache.cache_manager import CacheManager
from blacklist import BLACKLIST
import threading

app = Flask(__name__)

# counters for stats
stats = {
    "requests": 0,
    "blocked": 0,
    "cache_hits": 0,
    "cache_misses": 0,
    "active_connections": 0
}

cache = CacheManager()


# HTML DASHBOARD
HTML = """
<h1>Proxy Admin Panel</h1>

<h2>Stats</h2>
<ul>
  <li>Total Requests: {{stats.requests}}</li>
  <li>Blocked Requests: {{stats.blocked}}</li>
  <li>Cache Hits: {{stats.cache_hits}}</li>
  <li>Cache Misses: {{stats.cache_misses}}</li>
  <li>Active Connections: {{stats.active_connections}}</li>
</ul>

<h2>Blacklist</h2>
<ul>
{% for item in blacklist %}
  <li>{{item}}</li>
{% endfor %}
</ul>

<h2>Add to Blacklist</h2>
<form method="POST" action="/add">
  <input name="site" placeholder="example.com">
  <button type="submit">Add</button>
</form>
"""

#Routes
@app.route("/")
def home():
    return render_template_string(HTML, stats=stats, blacklist=BLACKLIST)


@app.route("/add", methods=["POST"])
def add():
    site = request.form.get("site")
    if site:
        BLACKLIST.add(site)
    return ("Added", 200)


@app.route("/stats")
def get_stats():
    return jsonify(stats)


# THREAD RUNNER
def run_admin():
    app.run(port=5000, debug=False)


def start_admin_interface():
    thread = threading.Thread(target=run_admin)
    thread.daemon = True
    thread.start()