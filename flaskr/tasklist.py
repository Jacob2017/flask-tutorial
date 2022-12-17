from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('tasklist', __name__)

@bp.route('/')
def index():
    db = get_db()
    tasks = db.execute(
        'SELECT t.id, title, body, created, creator_id, username'
        ' FROM tasklist t JOIN user u ON t.creator_id = u.id'
        ' WHERE completed != 1'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('tasklist/index.html', tasks=tasks)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None 
        
        if not title:
            error = 'Title is required.'
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO tasklist (title, body, creator_id)'
                ' VALUES (?,?,?)',
                (title, body, g.user['id'])
            )
            db.commit()
            return redirect(url_for('tasklist.index'))
    
    return render_template('tasklist/create.html')

def get_task(id, check_creator=True):
    task = get_db().execute(
        'SELECT t.id, title, body, created, creator_id, username'
        ' FROM tasklist t JOIN user u ON t.creator_id = u.id'
        ' WHERE t.id = ?',
        (id,)
    ).fetchone()

    if task is None:
        abort(404, f"Task id {id} doesn't exist.")
    
    if check_creator and task['creator_id'] != g.user['id']:
        abort(403)
    
    return task

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    task = get_task(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None 

        if not title:
            error = "Title is required."
        
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE tasklist SET title = ?, body = ?'
                ' WHERE id = ?',
                (title, body, id)
            )
            db.commit()
            return redirect(url_for('tasklist.index'))
    
    return render_template('tasklist/update.html', task=task)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_task(id)
    db = get_db()
    db.execute('DELETE FROM tasklist WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('tasklist.index'))