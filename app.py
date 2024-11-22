from flask import Flask, render_template, request, redirect, url_for, flash, session 
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'test'

DATABASE = 'database.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL UNIQUE, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL)''')
    conn.commit()
    conn.close()
init_db()

@app.route('/')
def home():
    return redirect(url_for('login'))
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['user'] = username 
            return redirect(url_for('welcome'))
        else:
            flash('Invalid username or password', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if len(username) < 3:
            flash('Username must be at least 3 characters long.', 'error')
            return redirect(url_for('register'))
        
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email address.', 'error')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return redirect(url_for('register'))
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, password))
            conn.commit()
            conn.close()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError as e: 
            if 'UNIQUE constraint failed' in str(e):
                flash('Username or Email already exists. Please choose another.', 'error')
            else: 
                flash('An error occured. Please try again.', 'error')
            return redirect(url_for('register'))
    return render_template('register.html')

@app.route("/welcome")
def welcome():
    if 'user' in session:
        username = session['user']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM users WHERE username = ?', (username,))
        email = cursor.fetchone()[0]
        conn.close()
        return render_template("welcome.html", username=username, email=email)
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)       
