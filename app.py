from flask import Flask, request, jsonify, render_template, redirect
import hashlib
import sqlite3

app = Flask(__name__)

# Database Initialization
def initialize_db():
    conn = sqlite3.connect("url_shortener.db")
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS url_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        long_url TEXT NOT NULL,
        short_url TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

initialize_db()

# Generate short URL
def generate_short_url(long_url):
    key = hashlib.md5(long_url.encode()).hexdigest()[:8]
    short_url = f"http://127.0.0.1:5000/{key}"
    return key, short_url

# Route for serving the frontend
@app.route('/')
def index():
    return render_template('index.html')

# Route for shortening the URL
@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get('long_url')

    if not long_url:
        return jsonify({'error': 'No URL provided'}), 400

    conn = sqlite3.connect("url_shortener.db")
    cursor = conn.cursor()

    # Check if the URL already exists in the database
    cursor.execute('SELECT short_url FROM url_mapping WHERE long_url = ?', (long_url,))
    result = cursor.fetchone()

    if result:
        conn.close()
        return jsonify({'short_url': result[0]})

    # If not, generate a new short URL
    key, short_url = generate_short_url(long_url)
    cursor.execute('INSERT INTO url_mapping (long_url, short_url) VALUES (?, ?)', (long_url, short_url))
    conn.commit()
    conn.close()

    return jsonify({'short_url': short_url})

# Route for redirection
@app.route('/<short_url_key>')
def redirect_to_long_url(short_url_key):
    conn = sqlite3.connect("url_shortener.db")
    cursor = conn.cursor()
    cursor.execute('SELECT long_url FROM url_mapping WHERE short_url LIKE ?', (f"%/{short_url_key}",))
    result = cursor.fetchone()
    conn.close()

    if result:
        return redirect(result[0])  # Redirect to the original URL
    else:
        return "Short URL not found.", 404

if __name__ == '__main__':
    app.run(debug=True)
