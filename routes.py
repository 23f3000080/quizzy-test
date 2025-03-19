from flask import Flask, render_template, request, flash, redirect, url_for, session
from app import app
from models import db, User, Subject, Quiz, Question, QuizResult
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
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
    user = session.get('name', 'User')
    subjects = Subject.query.all()
    return render_template("admin_side/admin_dashboard.html", user=user, subjects=subjects)

#Admin side view Quizzes
@app.route('/admin/view_quizzes')
@admin_required
def view_quizzes():
    quizzes = Quiz.query.all()
    return render_template("admin_side/view_quizzes.html", quizzes=quizzes)

#Admin side summary
@app.route('/admin/summary')
@admin_required
def summary():
    return render_template("admin_side/summary.html")

#admin seach route
@app.route('/admin/search')
@admin_required
def search():
    return render_template("admin_side/search.html")

#User Side Routes
#User side dashboard
@app.route('/user/dashboard')
@user_required
def user_dashboard():
    user_id = session.get('id')
    user = session.get('name', 'User')
    quizzes = Quiz.query.all()

    # Get the list of quiz IDs that the user has attempted
    attempted_quiz = (
        db.session.query(QuizResult.quiz_id)
        .filter(QuizResult.user_id == user_id)
        .all()
    )
    attempted_quiz_id = [attempt.quiz_id for attempt in attempted_quiz]
    return render_template("user_side/user_dashboard.html", user=user, quizzes=quizzes, attempted_quiz_id=attempted_quiz_id)

#User side score route
@app.route('/user/score')
@user_required
def user_score():
    user_id = session.get('id')

    if not user_id:
        flash("You must be logged in to view results.", "danger")
        return redirect(url_for('login'))

    # Fetch all quiz attempts by the user
    attempts = (
        db.session.query(QuizResult, Quiz.title)
        .join(Quiz, QuizResult.quiz_id == Quiz.id)
        .filter(QuizResult.user_id == user_id)
        .order_by(QuizResult.quiz_attempt_date.desc())  # Show latest attempts first
        .all()
    )
    return render_template("user_side/user_score.html", attempts=attempts)

#user side summary route
@app.route('/user/summary')
@user_required
def user_summary():
    return render_template("user_side/user_summary.html")

#user profile update route
@app.route('/user/profile', methods=['GET', 'POST'])
@user_required
def user_profile():
    user = User.query.get(session['id'])
    if request.method == 'POST':
        cpassword = request.form.get('cpassword')
        name = request.form.get('name')
        dob = request.form.get('dob')
        qualification = request.form.get('qualification')

        if not all([cpassword, name, dob, qualification]):
            flash('Please fill all the fields', 'danger')
            return redirect(url_for('user_profile'))
        
        if not check_password_hash(user.password, cpassword):
            flash('Incorrect Current Password', 'danger')
            return redirect(url_for('user_profile'))
        
        if name == user.name and dob == user.dob and qualification == user.qualification:
            flash('No changes found', 'info')
            return redirect(url_for('user_profile'))
        
        session['name'] = name
        user.name = name
        user.dob = dob
        user.qualification = qualification
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user_profile'))

    return render_template("user_side/user_profile.html", user=user)

#start quiz route
@app.route('/quiz/start/<int:quiz_id>')
@user_required
def start_quiz(quiz_id):
    quiz = Quiz.query.get(quiz_id)
    user_id = session.get('id')
    questions = Question.query.filter_by(chapter_id=quiz.chapter_id)

    # Check if the user has already attempted the quiz
    attempt = QuizResult.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if attempt:
        flash("You have already attempted this quiz.", "danger")
        return redirect(url_for('user_dashboard'))
    return render_template("user_side/start_quiz.html", quiz=quiz, questions=questions)

#submit quiz route
@app.route('/submit/quiz/<quiz_id>', methods=['POST'])
@user_required
def submit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    user_id = session.get('id')

    if not user_id:
        flash("You must be logged in to submit the quiz.", "danger")
        return redirect(url_for('login'))

    questions = Question.query.filter_by(chapter_id=quiz.chapter_id).all()
    total_marks = sum(q.marks for q in questions)
    
    # Create an attempt entry before checking answers
    attempt = QuizResult(
        user_id=user_id,
        quiz_id=quiz.id,
        score=0,  # Initial score, updated later
        total_marks=total_marks,
        total_questions=len(questions)
    )
    db.session.add(attempt)
    db.session.commit()

    score = 0
    for question in questions:
        user_answer = request.form.get(f'question_{question.id}')
        if user_answer and str(user_answer) == str(question.correct_option):
            score += question.marks

    # Update the attempt record with the final score
    attempt.score = score
    db.session.commit()

    percentage_score = (score / total_marks) * 100
    flash(f"Quiz submitted successfully! You scored {score} out of {total_marks} ({percentage_score:.2f}%)", "success")
    return redirect(url_for('user_dashboard'))

@app.route('/user/view/quiz/<quiz_id>')
@user_required
def view_attempted_quiz(quiz_id):
    user_id = session.get('id')
    quiz = Quiz.query.get_or_404(quiz_id)
    questions = Question.query.filter_by(chapter_id=quiz.chapter_id).all()

    # Fetch the user's attempt for this quiz
    attempt = QuizResult.query.filter_by(user_id=user_id, quiz_id=quiz_id).first()
    if not attempt:
        flash("You have not attempted this quiz yet.", "danger")
        return redirect(url_for('user_dashboard'))

    return render_template("user_side/view_attempted_quiz.html", quiz=quiz, questions=questions, attempt=attempt)

@app.route('/forget/password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        dob = request.form.get('dob').strip()
        password = request.form.get('password').strip()

        if not all([username, dob, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('forget_password'))

        user = User.query.filter_by(username=username).first()
        if not user:
            flash('User does not exist', 'danger')
            return redirect(url_for('forget_password'))
        
        if user.dob != dob:
            flash('Date of birth is incorrect', 'danger')
            return redirect(url_for('forget_password'))
        
        user.password = generate_password_hash(password)
        db.session.commit()
        flash('Password updated successfully', 'success')
        return redirect(url_for('login'))

    return render_template('forget_password.html')

