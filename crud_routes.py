from flask import Flask, render_template, request, flash, redirect, url_for, session
from app import app
from models import db, Subject, Chapter, Question, Quiz
from routes import user_required, admin_required
import json

@app.route('/admin/add_subject', methods=['GET', 'POST'])
@admin_required
def add_subject():
    if request.method == 'POST':
        sub_name = request.form.get('subjectName', '').strip()
        description = request.form.get('description')

        subject = Subject.query.filter_by(sub_name=sub_name).first()
        if subject:
            flash('Subject already exists!', 'danger')
            return redirect(url_for('add_subject'))
        
        new_subject = Subject(sub_name=sub_name, description=description)
        db.session.add(new_subject)
        db.session.commit()
        flash('Subject added successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_side/crud_temp/add_subject.html')

@app.route('/admin/edit/subject/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def edit_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if not subject:
        flash('Subject not found', 'info')
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        sub_name = request.form.get('subjectName', '').strip()
        description = request.form.get('description')

        subject.sub_name = sub_name
        subject.description = description
        db.session.commit()
        flash('Subject updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_side/crud_temp/edit_subject.html', subject=subject)


@app.route('/admin/delete/<int:subject_id>', methods=['GET','POST'])
@admin_required
def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/add_chapter/<int:subject_id>', methods=['GET', 'POST'])
@admin_required
def add_chapter(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':
        chapter_name = request.form.get('chapterName', '').strip()
        description = request.form.get('description')

        chapter = Chapter.query.filter_by(chapter_name=chapter_name, subject_id=subject_id).first()
        if chapter:
            flash('Chapter already exists!', 'danger')
            return redirect(url_for('add_chapter'))
        
        new_chapter = Chapter(chapter_name=chapter_name, description=description, subject_id=subject_id)
        db.session.add(new_chapter)
        db.session.commit()
        flash('Chapter added successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_side/crud_temp/add_chapter.html', subject=subject)

@app.route('/admin/delete_chapter/<int:chapter_id>', methods=['GET','POST'])
@admin_required
def delete_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    db.session.delete(chapter)
    db.session.commit()
    flash('Chapter deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/edit_chapter/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def edit_chapter(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    if request.method == 'POST':
        chapter_name = request.form.get('chapterName', '').strip()
        description = request.form.get('description')

        chapter.chapter_name = chapter_name
        chapter.description = description
        db.session.commit()
        flash('Chapter updated successfully', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_side/crud_temp/edit_chapter.html', chapter=chapter)

@app.route('/admin/add_question/<int:chapter_id>', methods=['GET', 'POST'])
@admin_required
def add_question(chapter_id):
    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        option1 = request.form.get('option1', '').strip()
        option2 = request.form.get('option2', '').strip()
        option3 = request.form.get('option3', '').strip()
        option4 = request.form.get('option4', '').strip()
        answer = request.form.get('answer', '').strip()
        marks = request.form.get('marks', '').strip()

        if not all([question, option1, option2, option3, option4, answer, marks]):
            flash('All fields are required', 'danger')
            return redirect(url_for('add_question', chapter_id=chapter_id))

        new_question = Question(title=question, option1=option1, option2=option2, option3=option3, option4=option4, correct_option=answer, marks=marks, chapter_id=chapter_id)
        db.session.add(new_question)
        db.session.commit()
        flash('Question added successfully', 'success')
        return redirect(url_for('add_question', chapter_id=chapter_id))
    return render_template('admin_side/crud_temp/add_question.html', chapter_id=chapter_id)

@app.route('/admin/view/questions/<int:chapter_id>', methods=['GET','POST'])
@admin_required
def view_questions(chapter_id):
    chapter = Chapter.query.get(chapter_id)
    questions = Question.query.filter_by(chapter_id=chapter_id).all()
    return render_template('admin_side/crud_temp/view_question.html', chapter=chapter, questions=questions)

@app.route('/admin/edit/question/<int:question_id>', methods=['GET', 'POST'])
@admin_required
def edit_question(question_id):
    question = Question.query.get(question_id)

    if not question:
        flash("Question not found!", "danger")
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        question.title = request.form.get('question', question.title)
        question.option1 = request.form.get('option1', question.option1)
        question.option2 = request.form.get('option2', question.option2)
        question.option3 = request.form.get('option3', question.option3)
        question.option4 = request.form.get('option4', question.option4)
        question.correct_option = request.form.get('answer', question.correct_option)
        question.marks = request.form.get('marks', question.marks)
        try:
            db.session.commit()
            flash("Question updated successfully!", "success")
            return redirect(url_for('view_questions', chapter_id=question.chapter_id))
        except Exception as e:
            db.session.rollback()
            flash("An error occurred while updating the question.", "danger")

    return render_template('admin_side/crud_temp/edit_question.html', question=question)

@app.route('/admin/delete_question/<int:question_id>', methods=['GET','POST'])
@admin_required
def delete_question(question_id):
    question = Question.query.get(question_id)
    db.session.delete(question)
    db.session.commit()
    flash('Question deleted successfully', 'success')
    return redirect(url_for('view_questions', chapter_id=question.chapter_id))

# Create Quiz
@app.route('/admin/create/quiz', methods=['GET', 'POST'])
@admin_required
def create_quiz():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        subject_id = request.form['subject']
        chapter_id = request.form['chapter']
        num_questions = request.form['num_questions']
        duration = request.form['duration']

        new_quiz = Quiz(title=title, description=description, subject_id=subject_id, chapter_id=chapter_id, number_of_questions=num_questions, duration=duration)
        db.session.add(new_quiz)
        db.session.commit()
        flash('Quiz created successfully!', 'success')
        return redirect(url_for('view_quizzes'))

    subjects = Subject.query.all()
    chapters = {
        subject.id: [{"id": ch.id, "name": ch.chapter_name, "question_count": len(ch.questions)} for ch in subject.chapters]
        for subject in subjects
    }

    return render_template('admin_side/crud_temp/create_quiz.html', subjects=subjects, chapters=json.dumps(chapters))


# edit quiz
@app.route('/edit/quiz/<int:quiz_id>', methods=['GET', 'POST'])
@admin_required
def edit_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    subjects = Subject.query.all()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        subject_id = request.form['subject']
        chapter_id = request.form['chapter']
        num_questions = request.form['num_questions']
        duration = request.form['duration']

        # Updating quiz details
        quiz.title = title
        quiz.description = description
        quiz.subject_id = subject_id
        quiz.chapter_id = chapter_id
        quiz.number_of_questions = num_questions
        quiz.duration = duration

        db.session.commit()
        flash('Quiz updated successfully!', 'success')
        return redirect(url_for('view_quizzes'))

    return render_template('admin_side/crud_temp/edit_quiz.html', quiz=quiz, subjects=subjects)

# Route to delete a quiz
@app.route('/admin/delete_quiz/<int:quiz_id>', methods=['POST'])
@admin_required
def delete_quiz(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    quiz.is_deleted = True
    db.session.commit()
    flash("Quiz deleted successfully!", "success")
    return redirect(url_for('view_quizzes'))
