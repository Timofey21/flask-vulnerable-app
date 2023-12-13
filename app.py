import sqlite3

from flask import Flask, render_template, render_template_string, request, redirect, session, abort
from database import init_db

app = Flask(__name__)

app.secret_key = 'BAD_SECRET_KEY'


@app.before_request
def require_login():
    allowed_routes = ["login", "register"]
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():  # put application's code here

    init_db()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        connection = sqlite3.connect('demo.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            if user[-2] == 'admin':
                session['user'] = user[-2]
                return redirect('/admin')
            else:
                session['user'] = user[-2]
                return redirect('/')

        else:
            message = "Login failed!"
            return render_template_string(open('templates/login.html').read(), message=message)
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':

        connection = sqlite3.connect('demo.db')
        cursor = connection.cursor()

        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        cursor.execute("SELECT * FROM users WHERE username = '{}'".format(username))
        username_check = cursor.fetchone()
        connection.commit()

        if username_check == username:
            message = "User is already existed "
            return render_template_string(open('templates/register.html').read(), message=message)

        if username and password1 == password2:
            cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password1))
            connection.commit()

        if username == 'admin':
            return redirect('/admin')

        return redirect('/login')

    return render_template("register.html")


@app.route('/', methods=['POST', 'GET'])
def main_page():
    with sqlite3.connect('demo.db') as db:
        db.execute('CREATE TABLE IF NOT EXISTS blogs (id INTEGER PRIMARY KEY, message TEXT)')
        # db.execute("INSERT INTO blogs (message) VALUES ('bla bla')")

    connection = sqlite3.connect('demo.db')
    cursor = connection.cursor()

    if request.method == 'POST':

        message = request.form.get('message')

        if message:
            cursor.execute('INSERT INTO blogs (message) VALUES (?)', (message,))
            connection.commit()

        delete_id = request.form.get('delete-btn')

        if delete_id:
            cursor.execute("DELETE FROM blogs WHERE id = ('{}')".format(delete_id))
            connection.commit()

        logout_button = request.form.get('logout-button')

        if logout_button:
            session.pop('user', default=None)
            return redirect('/login')

    cursor.execute("SELECT * FROM blogs")
    connection.commit()
    blogs = cursor.fetchall()
    connection.close()
    return render_template("index.html", blogs=blogs)


@app.route('/admin', methods=['POST', 'GET'])
def admin():
    if session['user'] != 'admin':
        abort(403)

    if request.method == 'POST':
        logout_button = request.form.get('logout-button')
        if logout_button:
            session.pop('user', default=None)
            return redirect('/login')

    return render_template("admin.html")


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
