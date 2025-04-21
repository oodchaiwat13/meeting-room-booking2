from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("""
              CREATE TABLE IF NOT EXISTS bookings (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  date TEXT,
                  start_time TEXT,
                  end_time TEXT
              )
              """)
    conn.commit()
    conn.close()

def is_conflict(date, start_time, end_time):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM bookings WHERE date = ? AND (
                 (start_time <= ? AND end_time > ?) OR
                 (start_time < ? AND end_time >= ?) OR
                 (start_time >= ? AND end_time <= ?)
                )""", (date, start_time, start_time, end_time, end_time, start_time, end_time))
    result = c.fetchone()
    conn.close()
    return result is not None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        if is_conflict(date, start_time, end_time):
            return render_template('index.html', error="ช่วงเวลานี้ถูกจองแล้ว", bookings=get_bookings())
        else:
            conn = sqlite3.connect('bookings.db')
            c = conn.cursor()
            c.execute('INSERT INTO bookings (name, date, start_time, end_time) VALUES (?, ?, ?, ?)',
                      (name, date, start_time, end_time))
            conn.commit()
            conn.close()
            return redirect('/')
    return render_template('index.html', bookings=get_bookings())

def get_bookings():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bookings ORDER BY date, start_time')
    bookings = c.fetchall()
    conn.close()
    return bookings

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
