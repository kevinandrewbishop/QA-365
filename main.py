from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import table, column, select, update, insert
from flask import session, request
from getpass import getpass
import sqlalchemy as sql
from config import url
from sys import argv
import pandas as pd
import datetime
import flask

app = flask.Flask(__name__)

@app.route('/get_old_questions', methods = ['GET', 'POST'])
def get_earlier_questions():
    user = session['user']
    today = pd.datetime.today()
    shift = int(request.args['shift'])
    n = int(request.args['n'])
    query = 'WHERE ('
    for i in range(shift, shift + n):
        day = today - datetime.timedelta(i)
        query += '(month_ = "%s" AND day_ = "%s") \nOR ' %(day.month, day.day)
    query = query[:-3] + ')'
    q = '''SELECT a.*, b.year_, b.answer
        FROM questions a
        LEFT JOIN (
            SELECT * FROM user_answers
            WHERE email = "%s") b
        ON a.question_id = b.question_id
        %s
        ORDER BY a.question_id DESC
        LIMIT 5;''' %(user, query)
    df = pd.read_sql_query(q, engine)
    print q
    print df
    return df.to_json()


@app.route('/')
def index():
    name = session.get('first_name')
    return flask.render_template('index.html', name = name)

@app.route('/home', methods=['GET', 'POST'])
def home():
    name = session['first_name']
    user = session['user']
    today = pd.datetime.today()
    month = today.month
    month_name = today.strftime('%B')
    day = today.day
    year = today.year
    q = '''SELECT a.*, b.year_, b.answer
        FROM questions a
        LEFT JOIN (
            SELECT * FROM user_answers
            WHERE email = "%s") b
        ON a.question_id = b.question_id
        WHERE month_ = "%s" and day_ = "%s"''' %(user, month, day)
    todays_question = pd.read_sql_query(q, engine)
    if not todays_question['answer'][0]:
        todays_question['answer'] = 'Enter your answer here...'
    #foo = get_earlier_questions(session['user'], today)

    if request.method == 'POST':
        form = request.form
        delete_q = '''DELETE FROM user_answers
            WHERE email = "%s"
            AND year_ = %s
            AND question_id = %s;
                ''' %(user, year, form['id'])
        engine.execute(delete_q)
        df = {'email': session['user'], 'year_': year}
        df['question_id'] = form['id']
        df['answer'] = form['answer']
        df = pd.DataFrame(df, index = [0])
        df.to_sql('user_answers', engine, if_exists = 'append', index = False)
    return flask.render_template('home.html', todays_question = todays_question, name = name)


@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.form:
        form = request.form
        df = pd.DataFrame(form, index = [0])
        df['pwd'] = generate_password_hash(form['pwd'])
        print(df)
        email = form['email']
        check_user = engine.execute('SELECT * FROM users where email = "%s"' %email)
        if check_user.rowcount > 0:
            return flask.render_template('register.html', exists = True)
        else:
            df.to_sql('users', engine, if_exists = 'append', index = False)
            session['user'] = email
            session['first_name'] = form['first_name']
            return flask.redirect(flask.url_for('index'))
    return flask.render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.form:
        form = request.form
        email = form['email']
        pwd = form['pwd']
        user = pd.read_sql_query('SELECT * FROM users where email = "%s"' %email, engine)
        if user.empty:
            error = "Sorry, we can't find your email address in our database."
            error += 'Try <a href="/register">registering</a> here.'
            return flask.render_template('login.html', error = error)
        else:
            if check_password_hash(user['pwd'][0], pwd):
                session['user'] = user['email'][0]
                session['first_name'] = user['first_name'][0]
                return flask.redirect(flask.url_for('index'))
            else:
                return flask.render_template('login.html', error = "Sorry, your password does not match.")

    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    session['user'] = None
    session['first_name'] = None
    return flask.redirect(flask.url_for('index'))


if __name__ == '__main__':
    app.secret_key = 'chooseALongAndDifficultString!'
    args = argv[1:]
    args = [arg.replace('-', '').split('=') for arg in args]
    args = {key: value for key, value in args}

    if 'port' in args:
        args['port'] = int(args['port'])
    if 'debug' in args:
        args['debug'] = bool(args['debug'])
    sql_pwd = getpass("Enter MySQL Password:")
    url = url %sql_pwd
    engine = sql.create_engine(url)
    app.run(**args)
