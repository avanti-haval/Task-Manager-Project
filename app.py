from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('tasks_projects.db')
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Create tables
with app.app_context():
    db = get_db()
    c = db.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, category TEXT, description TEXT, start_date TEXT, end_date TEXT, project_id INTEGER, completed TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, task_name TEXT, task_category TEXT, task_description TEXT, start_date TEXT, end_date TEXT, completed TEXT)''')
    db.commit()

@app.route('/')
def index():
    if 'username' in session:
        return render_index()
    return redirect(url_for('login'))

def render_index():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    cursor.execute("SELECT * FROM projects")
    projects = cursor.fetchall()
    return render_template('index.html', tasks=tasks, projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()

        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        existing_user = cursor.fetchone()

        if existing_user:
            error = 'Username already exists'
            return render_template('signup.html', error=error)
        else:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            db.commit()
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/index', methods=['GET', 'POST'])
def index_form():
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        if 'task_name' in request.form:
            # Handling task form submission
            task_name = request.form['task_name']
            task_category = request.form['task_category']
            task_description = request.form['task_description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            cursor.execute("INSERT INTO tasks (name, category, description, start_date, end_date, completed) VALUES (?, ?, ?, ?, ?, 'No')", (task_name, task_category, task_description, start_date, end_date))
            db.commit()

        elif 'project_name' in request.form:
            # Handling project form submission
            project_name = request.form['project_name']
            project_tasks = request.form.getlist('task_name')
            task_category = request.form['task_category']
            task_description = request.form['task_description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            cursor.execute("INSERT INTO projects (name, task_name, task_category, task_description, start_date, end_date, completed) VALUES (?, ?, ?, ?, ?, ?, 'No')", (project_name, ', '.join(project_tasks), task_category, task_description, start_date, end_date))
            project_id = cursor.lastrowid

            for task_name in project_tasks:
                cursor.execute("INSERT INTO tasks (name, category, description, start_date, end_date, project_id, completed) VALUES (?, ?, ?, ?, ?, ?, 'No')", (task_name, task_category, task_description, start_date, end_date, project_id))
            db.commit()

    return render_index()

# Route for deleting a task
@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    db.commit()
    return '', 204

# Route for marking a task as complete/incomplete
@app.route('/mark_task_complete/<int:task_id>', methods=['POST'])
def mark_task_complete(task_id):
    db = get_db()
    cursor = db.cursor()
    completed = request.args.get('completed')
    cursor.execute("UPDATE tasks SET completed = ? WHERE id = ?", (completed, task_id))
    db.commit()
    return '', 204

# Route for deleting a project
@app.route('/delete_project/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    db.commit()
    return '', 204

# Route for marking a project as complete/incomplete
@app.route('/mark_project_complete/<int:project_id>', methods=['POST'])
def mark_project_complete(project_id):
    db = get_db()
    cursor = db.cursor()
    completed = request.args.get('completed')
    cursor.execute("UPDATE projects SET completed = ? WHERE id = ?", (completed, project_id))
    db.commit()
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)