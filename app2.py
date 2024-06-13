from flask import Flask, render_template, request, redirect, url_for, session, g
import sqlite3

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database initialization
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

@app.route('/', methods=['GET', 'POST'])
def home():
    if 'username' in session:
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
                username = session['username']  # Get the username from the session
                cursor.execute("INSERT INTO tasks (name, category, description, start_date, end_date, completed, username) VALUES (?, ?, ?, ?, ?, 'No', ?)", (task_name, task_category, task_description, start_date, end_date, username))
                db.commit()

            elif 'project_name' in request.form:
                # Handling project form submission
                project_name = request.form['project_name']
                project_tasks = request.form.getlist('task_name')
                task_category = request.form['task_category']
                task_description = request.form['task_description']
                start_date = request.form['start_date']
                end_date = request.form['end_date']
                username = session['username']  # Get the username from the session
                cursor.execute("INSERT INTO projects (name, task_name, task_category, task_description, start_date, end_date, completed, username) VALUES (?, ?, ?, ?, ?, ?, 'No', ?)", (project_name, ', '.join(project_tasks), task_category, task_description, start_date, end_date, username))
                project_id = cursor.lastrowid

                for task_name in project_tasks:
                    cursor.execute("INSERT INTO tasks (name, category, description, start_date, end_date, project_id, completed, username) VALUES (?, ?, ?, ?, ?, ?, 'No', ?)", (task_name, task_category, task_description, start_date, end_date, project_id, username))
                db.commit()

        # Retrieve task details for the current user
        username = session['username']
        cursor.execute("SELECT * FROM tasks WHERE username = ?", (username,))
        tasks = cursor.fetchall()

        # Retrieve project details for the current user
        cursor.execute("SELECT * FROM projects WHERE username = ?", (username,))
        projects = cursor.fetchall()

        return render_template('home.html', username=session['username'], tasks=tasks, projects=projects)
    else:
        return render_template('home.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        db = get_db()
        cur = db.execute("SELECT username, password FROM tbl_users WHERE username = ?", (username,))
        user = cur.fetchone()
        cur.close()
        if user and pwd == user[1]:
            session['username'] = user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
        db = get_db()
        db.execute("INSERT INTO tbl_users (username, password) VALUES (?, ?)", (username, pwd))
        db.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

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
