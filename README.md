from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

DB_NAME = 'bookings.db'

# สร้างตารางถ้ายังไม่มี
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ตรวจสอบเวลาซ้ำ
def is_conflict(date, start, end):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        SELECT * FROM bookings 
        WHERE date = ? AND (
            (start_time < ? AND end_time > ?) OR
            (start_time < ? AND end_time > ?) OR
            (start_time >= ? AND end_time <= ?)
        )
    ''', (date, end, end, start, start, start, end))
    result = c.fetchall()
    conn.close()
    return len(result) > 0

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']

        if is_conflict(date, start_time, end_time):
            flash('❌ เวลานี้มีคนจองแล้ว กรุณาเลือกช่วงเวลาอื่น')
        else:
            c.execute('INSERT INTO bookings (name, date, start_time, end_time) VALUES (?, ?, ?, ?)',
                      (name, date, start_time, end_time))
            conn.commit()
            flash('✅ จองห้องสำเร็จ!')

    c.execute('SELECT * FROM bookings ORDER BY date, start_time')
    bookings = c.fetchall()
    conn.close()
    return render_template('index.html', bookings=bookings)

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
