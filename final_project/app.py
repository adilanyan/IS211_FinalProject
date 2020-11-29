from flask import Flask
app = Flask(__name__)
from flask import (Flask, render_template, redirect,
                   url_for, request, session, flash, g)
from functools import wraps
import sqlite3
from wtforms import Form, StringField, validators



app = Flask(__name__)

app.secret_key = "test key"
app.database = "password.db"


class PasswordForm(Form):
    provider = StringField('Provider', [validators.Length(min=1, max=200)])
    username = StringField('Username', [validators.Length(min=1, max=200)])
    password = StringField('Password', [validators.Length(min=3)])


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first')
            return redirect(url_for('login'))
    return wrapper


@app.route('/')
@login_required
def home():
    g.db = connect_db()
    cur = g.db.execute('SELECT * FROM passwords')
    passwords = [dict(id=row[0],
                      provider=row[1],
                      username=row[2],
                      password=row[3]) for row in cur.fetchall()]
    g.db.close()
    return render_template("index.html", passwords=passwords)


@app.route('/welcome')
def welcome():
    return render_template("welcome.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid creds'
        else:
            session['logged_in'] = True
            flash('you were just logged in')
            return redirect(url_for('home'))
    return render_template('login.html', error=error)


@app.route('/password/add', methods=['GET', 'POST'])
@login_required
def add_password():
    form = PasswordForm(request.form)
    if request.method == 'POST' and form.validate():
        provider = form.provider.data
        username = form.username.data
        password = form.password.data

        con = connect_db()
        c = con.cursor()

        c.execute("INSERT INTO passwords(provider, username, password) VALUES(?,?,?)", (provider, username, password))
        con.commit()
        con.close()
        return redirect(url_for('home'))
    return render_template('add_password.html', form=form)


@app.route('/delete_password/<string:id>', methods=['POST'])
@login_required
def delete_password(id):
    if request.method == 'POST':
        con = connect_db()
        c = con.cursor()
        c.execute("DELETE FROM passwords WHERE id = {}".format(id))
        con.commit()
        con.close()
        return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    flash('you were just logged out')

    return redirect(url_for('welcome'))


def connect_db():
    return sqlite3.connect(app.database)


if __name__ == '__main__':
    app.run(debug=True)
