import atexit

from flask import Flask, render_template, url_for, request
from functools import lru_cache

from werkzeug.utils import redirect

from lru import *

app = Flask(__name__)

@app.route('/')
def index():
	_cache=get_cache()
	print(_cache)
	return render_template('index.html',students=get_all(),cache=_cache,count=get_cache_size())

@app.route('/create')
def create():
	return render_template('create.html')

@app.route('/student/<_id>')
def student_preview(_id):
	return render_template('student.html',student=get_item(_id),name=get_name(_id),id=_id)

@app.route('/student/edit/<_id>')
def student_edit(_id):
	return render_template('edit.html',student=get_item(_id),name=get_name(_id),id=_id)

@app.route('/student/delete/<_id>')
def student_delete(_id):
	delete_item(_id)
	return redirect(url_for('index'))

@app.route('/update',methods=['POST'])
def update_data():
	student=get_list(request)
	_id=request.form['_id']
	update_item(_id,student)
	return redirect(url_for('index'))

@app.route('/save',methods=['POST'])
def save_data():
	student=get_list(request)
	_id=request.form['_id']
	add_item(_id,student)
	return redirect(url_for('index'))

def get_list(request):
	student={}

	_id=request.form['_id']
	name=request.form['name']

	marks=request.form.getlist('marks[]')
	subject=request.form.getlist('subject[]')
	
	student['name']=name

	i=0
	for sub in subject:
		student[sub]=marks[i]
		i+=1

	return student

def onExit():
	on_exit_restore()
	print('gopal')

if __name__ == '__main__':
	init()
	atexit.register(onExit)
	app.run()