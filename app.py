import sqlite3


from flask import Flask, render_template, render_template_string, request, redirect

app = Flask(__name__)


def init_db():
    with sqlite3.connect('demo.db') as db:
        db.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')

        # db.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('admin', 'password123')")
        # db.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('bob', 'bobpass')")
        # db.execute("INSERT OR IGNORE INTO users (username, password) VALUES ('alice', 'alicepass')")


@app.route('/login', methods=['POST', 'GET'])
def login():  # put application's code here

    init_db()
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = sqlite3.connect('demo.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = '{}' AND password = '{}'".format(username, password))
        user = cursor.fetchone()
        connection.close()

        if user:
            message = "Login successful!"
            return redirect('/', code=302)
        else:
            message = "Login failed!"

    return render_template_string(open('templates/login.html').read(), message=message)


@app.route('/register')
def register():
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

    cursor.execute("SELECT * FROM blogs")
    connection.commit()
    blogs = cursor.fetchall()
    connection.close()
    return render_template("index.html", blogs=blogs)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
