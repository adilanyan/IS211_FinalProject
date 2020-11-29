
import sqlite3

with sqlite3.connect("password.db") as connection:
    c = connection.cursor()

    setup = open('schema.sql', 'r').read()
    c.executescript(setup)
    connection.commit()
