import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('motion.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS motion_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# function add event to db
def add_motion_event(timestamp):
    conn = sqlite3.connect('motion.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO motion_events (timestamp) VALUES (?)', (timestamp,))
    conn.commit()
    conn.close()

# function retrieve to db
def get_motion_events():
    conn = sqlite3.connect('motion.db')
    cursor = conn.cursor()
    cursor.execute('SELECT timestamp FROM motion_events')
    events = cursor.fetchall()
    conn.close()
    return [{'timestamp': event[0]} for event in events]

# handle motion detection
@app.route('/motion', methods=['POST'])
def motion():
    # Get date and time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # add motion to db
    add_motion_event(timestamp)
    
    return jsonify({"message": "Motion detected", "timestamp": timestamp})

@app.route('/display')
def display():
    # Retrieve motion events from the database
    events = get_motion_events()
    return render_template('display.html', events=events)

if __name__ == '__main__':
    # Initialize the database
    init_db()
    app.run(debug=True)
