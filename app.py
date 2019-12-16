import sqlite3
from flask import Flask, render_template, g, request, redirect
from datetime import datetime


app = Flask(__name__)
app.debug = True


def connect_db():
    sql = sqlite3.connect('/home/jane/Desktop/flask_ultimate/food_log.db')
    sql.row_factory = sqlite3.Row
    return sql


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext  #this is called whenever a view is closed. by doing this, if a view was using db, it closes with it
def close_database(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/', methods=["GET", "POST"])
def index():
    db = get_db()
    if request.method == "POST":
        date = request.form['date']
        date = datetime.strptime(date, '%Y-%m-%d')
        db_date = datetime.strftime(date, '%Y%m%d')
        well_formated_date= datetime.strftime(date, '%B %d, %Y')
        query = 'INSERT INTO log_date(entry_date) values(?)'
        db.execute(query, [db_date])
        db.commit()
        # return f"input date: {date} database date:{db_date} pretty formatted date {well_formated_date}"

    get_dates_query = """SELECT entry_date, SUM(protein) AS protein , SUM(fat) AS fat, SUM(carbohydrates) AS carbs, SUM(calories) AS calories
                          FROM log_date 
                          LEFT JOIN food_date ON log_date.id = food_date.log_date_id
                          LEFT JOIN food ON food.id = food_date.food_id
                          GROUP BY entry_date
                          ORDER BY entry_date DESC """
    results_cur = db.execute(get_dates_query)
    query_results = results_cur.fetchall()  # a list with special objects Rows as elements
    food_summary = []
    for each_row_dict in query_results:
        date_dict = dict()
        date_dict['date'] = each_row_dict['entry_date']  # this will be passed to the url for each day
        date = datetime.strptime(str(each_row_dict['entry_date']), '%Y%m%d')
        date_dict['pretty_date'] = datetime.strftime(date, '%B %d, %Y')  # looks like January 27, 2019
        date_dict['protein'] = each_row_dict['protein']
        date_dict['fat'] = each_row_dict['fat']
        date_dict['carbs'] = each_row_dict['carbs']
        date_dict['calories'] = each_row_dict['calories']
        food_summary.append(date_dict)

    return render_template('home.html', food_summary=food_summary)


@app.route('/view-day/<date>', methods=["GET", "POST"])
def view_day(date):
    # populate the drop menu with different food kinds
    db = get_db()
    if request.method == 'POST':
        # get the id of the date for the join statement
        query = 'SELECT id FROM log_date WHERE entry_date = ?'
        cur = db.execute(query, [date])
        date_res = cur.fetchone()
        query = 'INSERT INTO food_date(food_id, log_date_id) VALUES(?, ?)'
        db.execute(query,[request.form['food_name'], date_res['id']])
        db.commit()
        # return f"{request.form['food_name']} {date_res['id']}"

    #dropdown menu for food available
    query = '''
            SELECT id, name FROM food
            '''
    cur = db.execute(query)
    food_names = cur.fetchall()

    # all food on this date
    query = '''
            SELECT name, protein, carbohydrates, fat, calories 
            FROM food
            JOIN food_date ON food.id = food_date.food_id
            JOIN log_date ON food_date.log_date_id = log_date.id
            WHERE entry_date = ?
            '''
    cur = db.execute(query, [date])
    all_food = cur.fetchall()

    # total of the food for this date
    total_calc = {}
    total_calc['fat'] = 0
    total_calc['carbs'] = 0
    total_calc['protein'] = 0
    total_calc['calories'] = 0
    for every_row in all_food:
        total_calc['fat'] += every_row['fat']
        total_calc['carbs'] += every_row['carbohydrates']
        total_calc['calories'] += every_row['calories']
        total_calc['protein'] += every_row['protein']

    return render_template('day.html', food_names=food_names, date=date, all_food=all_food, total_calc=total_calc)


@app.route('/add-food', methods=["GET", "POST"])
def add_food():
    db = get_db()
    if request.method == "POST":
        name = request.form['food-name']
        fat = int(request.form['fat'])
        carbohydrates = int(request.form['carbohydrates'])
        protein = int(request.form['protein'])
        calories = fat * 9 + 4 * protein + 4 * carbohydrates
        query = """
                INSERT INTO food(name, protein, carbohydrates, fat, calories) VALUES (?, ?, ?, ?, ?);
                """
        db.execute(query, (name, protein, carbohydrates, fat, calories))
        db.commit()
    get_data_query = 'SELECT name, protein, carbohydrates, fat, calories FROM food'
    cur  = db.cursor()
    cur.execute(get_data_query)
    results = cur.fetchall()
    return render_template('add_food.html', results=results)


if __name__ == '__main__':
    app.run()


