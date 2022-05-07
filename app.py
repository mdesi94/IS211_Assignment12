from sqlite3.dbapi2 import Connection

from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3 as sql

STUDENTS_TABLE = """
CREATE TABLE IF NOT EXISTS students(
    student_id integer PRIMARY KEY AUTOINCREMENT,
    firstname TEXT,
    lastname TEXT
)
"""

QUIZZES_TABLE = """
CREATE TABLE IF NOT EXISTS quizzes(
    quiz_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject TEXT,
    total_questions TEXT,
    quiz_date TEXT
)
"""

RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS student_results(
    student_id INTEGER,
    quiz_id INTEGER,
    score INTEGER
)
"""
app = Flask(__name__)

# connect to db and create tables
conn = sql.connect('hw13.db')
cur = conn.cursor()


cur.execute(STUDENTS_TABLE)
cur.execute(QUIZZES_TABLE)
cur.execute(RESULTS_TABLE)

conn.commit()

check_username = 'admin'
check_password = 'password'
student_grades = []
student_quizzes = []

app.config['SECRET_KEY'] = 'key12348'


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    login_error = 'Username/password incorrect'
    conn = sql.connect('hw13.db')
    cur = conn.cursor()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == check_username and password == check_password:
            session.clear()
            return redirect(url_for('dashboard'))
        elif username is None:
            flash(login_error)
        elif password is None:
            flash(login_error)
        elif username != check_username:
            flash(login_error)
        elif password != check_password:
            flash(login_error)
            return redirect(url_for('login'))

    return render_template('login.html')
# fix flash messages---not working


# view student and grade tables---choose options to add student/quiz/grade
@app.route('/dashboard', methods=['GET'])
def dashboard():
    conn = sql.connect('hw13.db')
    cur = conn.cursor()
    student = cur.execute('SELECT * FROM students').fetchall()
    quizzes = cur.execute('SELECT * FROM quizzes').fetchall()
    results = cur.execute('SELECT student_id, score FROM student_results').fetchall()

    students = student
    students_quizzes = quizzes
    student_grades.append(students)
    student_quizzes.append(students_quizzes)

    return render_template('dashboard.html', student_grades=student_grades, student_quizzes=student_quizzes)


# add a new student to database
@app.route('/student/add', methods=['GET', 'POST'])
def add_student():
    conn = sql.connect('hw13.db')
    cur = conn.cursor()
    if request.method == 'GET':
        return render_template('addstudent.html')
    if request.method == 'POST':
        first_name = request.form['first']
        last_name = request.form['last']

        student = (None, first_name, last_name)
        cur.execute('INSERT OR IGNORE INTO students VALUES(?,?,?)', student)
        conn.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/quiz/add', methods=['GET', 'POST'])
def add_quiz():
    conn = sql.connect('hw13.db')
    cur = conn.cursor()
    if request.method == 'GET':
        return render_template('addquiz.html')
    if request.method == 'POST':
        subject = request.form['subject']
        total_questions = request.form['total_questions']
        quiz_date = request.form['quiz_date']

        quiz = (None, subject, total_questions, quiz_date)
        cur.execute('INSERT OR IGNORE INTO quizzes VALUES(?,?,?,?)', quiz)
        conn.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/grade/add', methods=['GET', 'POST'])
def add_grade():
    conn = sql.connect('hw13.db')
    cur = conn.cursor()
    if request.method == 'GET':
        cur.execute('''SELECT rowid, firstname || "" || lastname FROM students''')
        students = cur.fetchall()
        cur.execute('''SELECT rowid, subject FROM quizzes''')
        quizzes = cur.fetchall()
        print(students)
        return render_template('addgrade.html', students=students, quizzes=quizzes)
    elif request.method == 'POST':
        student = request.form['student']
        quiz = request.form['quiz']
        grade = request.form['grade']
        cur.execute('INSERT INTO student_results VALUES (?,?,?)', ('student_id', 'quiz_id', 'score'))
        conn.commit()
        return redirect(url_for('dashboard'))
    return redirect(url_for('dashboard'))


@app.route('/student/<id>', methods=['POST', 'GET'])
def student_id(id):
    conn = sql.connect('hw13.db')
    cur = conn.cursor()
    if request.method == 'GET':
        result = cur.execute(
            'SELECT student_id, quiz_id,  score FROM student_results WHERE id=?',
            (id,)).fetchone()

        test_scores = result
        quiz_results = []
        quiz_results.append(test_scores)
        print(test_scores)
        print(quiz_results)
        return render_template('results.html', quiz_results=quiz_results)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
