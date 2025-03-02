from flask import Flask, render_template, request, flash, redirect, url_for, session
from app import app
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        cpassword = request.form.get('cpassword', '').strip()
        name = request.form.get('name', '').strip()
        qualification = request.form.get('qualification', '').strip()
        dob = request.form.get('dob', '').strip()

        if not all([username, password, cpassword, name, qualification, dob]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if password != cpassword:
            flash('Password does not match', 'danger')
            return redirect(url_for('register'))
        
        #check user in database
        user = User.query.filter_by(username=username).first()
        if user:
            flash('User already exists!', 'danger')
            return redirect(url_for('register'))

        #hashing the password
        hash_password = generate_password_hash(password)   

        #create user
        new_user = User(username=username, password=hash_password, name=name, qualification=qualification, dob=dob)

     
        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully', 'success')
        return redirect(url_for('login'))
    

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()

        if not all([username, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('login'))
        
        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist', 'danger')
            return redirect(url_for('login'))
        
        if not check_password_hash(user.password, password):
            flash('Password is incorrect', 'danger')
            return redirect(url_for('login'))
        
        session['id'] = user.id
        session['user'] = user.username
        session['name'] = user.name
        session['is_admin'] = user.is_admin

        if user.is_admin:
            flash('Admin login successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Login successfully', 'success')
            return redirect(url_for('user_dashboard'))
    return render_template('login.html')

# decorator for auth required
def user_required(func):
    """Restrict access to user-only pages (block admins)."""
    @wraps(func)
    def inner(*args, **kwargs):
        if "id" not in session:
            flash('Please login to continue', 'info')
            return redirect(url_for('login'))
        
        user = User.query.get(session['id'])
        if not user:  
            flash('User not found, please login again', 'danger')
            return redirect(url_for('login'))

        if user.is_admin:  # Block admin access
            flash('You are not allowed to access this page', 'danger')
            return redirect(url_for('home'))  # Redirect admin to home

        return func(*args, **kwargs)

    return inner

#decorator for admin required
def admin_required(func):
    """Restrict access to admin-only pages (block normal users)."""
    @wraps(func)
    def inner(*args, **kwargs):
        if 'id' not in session:
            flash('Please login to continue', 'danger')
            return redirect(url_for('login'))

        user = User.query.get(session['id'])
        if not user:  
            flash('User not found, please login again', 'danger')
            return redirect(url_for('login'))

        if not user.is_admin:  # Block normal user access
            flash('You are not authorized to access this page', 'danger')
            return redirect(url_for('home'))  # Redirect user to home

        return func(*args, **kwargs)

    return inner 

#logout route
@app.route('/logout')
def logout():
    session.clear()
    flash('Logout Successfully', 'info')
    return redirect(url_for('login'))

#admin dashboard
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template("admin_side/admin_dashboard.html")

#Admin side view Quizzes
@app.route('/admin/view_quizzes')
@admin_required
def view_quizzes():
    return render_template("admin_side/view_quizzes.html")

#Admin side summary
@app.route('/admin/summary')
@admin_required
def summary():
    return render_template("admin_side/summary.html")

#User Side Routes
#User side dashboard
@app.route('/user/dashboard')
@user_required
def user_dashboard():
    return render_template("user_side/user_dashboard.html")

#User side score route
@app.route('/user/score')
@user_required
def user_score():
    return render_template("user_side/user_score.html")

#user side summary route
@app.route('/user/summary')
@user_required
def user_summary():
    return render_template("user_side/user_summary.html")

#user profile update route
@app.route('/user/profile')
@user_required
def user_profile():
    return render_template("user_side/user_profile.html")
