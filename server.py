from flask import Flask, render_template, redirect, url_for, g
import secrets, db_connector


app = Flask(__name__)
app.debug = True
app.secret_key = secrets.token_hex(8)


@app.teardown_appcontext  #this is called whenever a view is closed. by doing this, if a view was using db, it closes with it
def close_database(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def index():
    db = db_connector.get_database(g)
    query = 'SELECT * FROM users'
    cur = db.execute(query)
    results = cur.fetchall()
    return render_template('index.html', results=results)


if __name__ == '__main__':
    app.run()