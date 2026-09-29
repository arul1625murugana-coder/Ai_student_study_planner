import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user,
    logout_user, login_required, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config["SECRET_KEY"] = os.getenv(
    "SECRET_KEY",
    "student-planner-development-secret"
)

app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///study_planner.db"
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# =========================================================
# DATABASE MODELS
# =========================================================

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)

    email = db.Column(
        db.String(150),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    course = db.Column(db.String(100))

    department = db.Column(db.String(100))

    year = db.Column(db.String(20))

    semester = db.Column(db.String(20))

    study_hours = db.Column(
        db.Float,
        default=2
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Subject(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    difficulty = db.Column(
        db.String(30),
        default="Medium"
    )

    exam_date = db.Column(
        db.Date
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    chapters = db.relationship(
        "Chapter",
        backref="subject",
        cascade="all, delete-orphan"
    )


class Chapter(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(200),
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Not Started"
    )

    difficulty = db.Column(
        db.String(30),
        default="Medium"
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subject.id"),
        nullable=False
    )


class StudyTask(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    study_date = db.Column(
        db.Date,
        nullable=False
    )

    duration = db.Column(
        db.Integer,
        default=60
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


class Note(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    category = db.Column(
        db.String(100)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


class Assignment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    subject = db.Column(
        db.String(150)
    )

    due_date = db.Column(
        db.Date,
        nullable=False
    )

    priority = db.Column(
        db.String(30),
        default="Medium"
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =========================================================
# AUTHENTICATION
# =========================================================

@app.route("/")
def home():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )

    return redirect(
        url_for("login")
    )


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"].strip()

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        course = request.form.get("course")

        department = request.form.get("department")

        year = request.form.get("year")

        semester = request.form.get("semester")

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect(
                url_for("register")
            )

        user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            course=course,
            department=department,
            year=year,
            semester=semester
        )

        db.session.add(user)

        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "register.html"
    )


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"].strip().lower()

        password = request.form["password"]

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "login.html"
    )


@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(
        url_for("login")
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    subjects = Subject.query.filter_by(
        user_id=current_user.id
    ).all()

    tasks = StudyTask.query.filter_by(
        user_id=current_user.id
    ).order_by(
        StudyTask.study_date
    ).all()

    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Assignment.due_date
    ).all()

    total_chapters = 0

    completed_chapters = 0

    for subject in subjects:

        total_chapters += len(subject.chapters)

        completed_chapters += sum(
            1
            for chapter in subject.chapters
            if chapter.status == "Completed"
        )

    if total_chapters > 0:

        progress = round(
            completed_chapters /
            total_chapters * 100
        )

    else:

        progress = 0

    return render_template(
        "dashboard.html",
        subjects=subjects,
        tasks=tasks,
        assignments=assignments,
        progress=progress
    )


# =========================================================
# SUBJECTS
# =========================================================

@app.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():

    if request.method == "POST":

        name = request.form["name"]

        difficulty = request.form.get(
            "difficulty",
            "Medium"
        )

        exam_date_text = request.form.get(
            "exam_date"
        )

        exam_date = None

        if exam_date_text:

            exam_date = datetime.strptime(
                exam_date_text,
                "%Y-%m-%d"
            ).date()

        subject = Subject(
            name=name,
            difficulty=difficulty,
            exam_date=exam_date,
            user_id=current_user.id
        )

        db.session.add(subject)

        db.session.commit()

        flash(
            "Subject added successfully.",
            "success"
        )

        return redirect(
            url_for("subjects")
        )

    subjects = Subject.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "subjects.html",
        subjects=subjects
    )


@app.route("/subjects/<int:subject_id>/chapter", methods=["POST"])
@login_required
def add_chapter(subject_id):

    subject = Subject.query.filter_by(
        id=subject_id,
        user_id=current_user.id
    ).first_or_404()

    chapter = Chapter(
        name=request.form["name"],
        difficulty=request.form.get(
            "difficulty",
            "Medium"
        ),
        subject_id=subject.id
    )

    db.session.add(chapter)

    db.session.commit()

    return redirect(
        url_for("subjects")
    )


@app.route(
    "/chapter/<int:chapter_id>/complete",
    methods=["POST"]
)
@login_required
def complete_chapter(chapter_id):

    chapter = Chapter.query.get_or_404(
        chapter_id
    )

    subject = Subject.query.get(
        chapter.subject_id
    )

    if subject.user_id != current_user.id:

        return jsonify({
            "error": "Unauthorized"
        }), 403

    chapter.status = "Completed"

    db.session.commit()

    return jsonify({
        "success": True
    })


# =========================================================
# AI STUDY PLANNER
# =========================================================

@app.route("/planner")
@login_required
def planner():

    tasks = StudyTask.query.filter_by(
        user_id=current_user.id
    ).order_by(
        StudyTask.study_date
    ).all()

    return render_template(
        "planner.html",
        tasks=tasks
    )


@app.route(
    "/api/planner/generate",
    methods=["POST"]
)
@login_required
def generate_plan():

    subjects = Subject.query.filter_by(
        user_id=current_user.id
    ).all()

    if not subjects:

        return jsonify({
            "success": False,
            "message": "Please add subjects first."
        })

    today = date.today()

    created = []

    for index, subject in enumerate(subjects):

        pending_chapters = [
            c for c in subject.chapters
            if c.status != "Completed"
        ]

        if not pending_chapters:
            continue

        chapter = pending_chapters[0]

        task_date = today

        task = StudyTask(
            title=f"{subject.name} - {chapter.name}",
            study_date=task_date,
            duration=60,
            user_id=current_user.id
        )

        db.session.add(task)

        created.append(task.title)

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Study plan generated.",
        "tasks": created
    })


# =========================================================
# NOTES
# =========================================================

@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes():

    if request.method == "POST":

        note = Note(
            title=request.form["title"],
            content=request.form["content"],
            category=request.form.get("category"),
            user_id=current_user.id
        )

        db.session.add(note)

        db.session.commit()

        flash(
            "Note saved.",
            "success"
        )

    notes = Note.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Note.created_at.desc()
    ).all()

    return render_template(
        "notes.html",
        notes=notes
    )


# =========================================================
# ASSIGNMENTS
# =========================================================

@app.route("/assignments", methods=["GET", "POST"])
@login_required
def assignments():

    if request.method == "POST":

        assignment = Assignment(
            title=request.form["title"],
            subject=request.form.get("subject"),
            due_date=datetime.strptime(
                request.form["due_date"],
                "%Y-%m-%d"
            ).date(),
            priority=request.form.get(
                "priority",
                "Medium"
            ),
            user_id=current_user.id
        )

        db.session.add(assignment)

        db.session.commit()

        flash(
            "Assignment added.",
            "success"
        )

    assignments = Assignment.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Assignment.due_date
    ).all()

    return render_template(
        "assignments.html",
        assignments=assignments
    )


# =========================================================
# ANALYTICS API
# =========================================================

@app.route("/analytics")
@login_required
def analytics():

    subjects = Subject.query.filter_by(
        user_id=current_user.id
    ).all()

    subject_data = []

    for subject in subjects:

        total = len(subject.chapters)

        completed = sum(
            1 for c in subject.chapters
            if c.status == "Completed"
        )

        percentage = (
            round(completed / total * 100)
            if total else 0
        )

        subject_data.append({
            "name": subject.name,
            "progress": percentage
        })

    return render_template(
        "analytics.html",
        subject_data=subject_data
    )


# =========================================================
# PROFILE
# =========================================================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():

    if request.method == "POST":

        current_user.name = request.form["name"]

        current_user.course = request.form.get(
            "course"
        )

        current_user.department = request.form.get(
            "department"
        )

        current_user.year = request.form.get(
            "year"
        )

        current_user.semester = request.form.get(
            "semester"
        )

        current_user.study_hours = float(
            request.form.get(
                "study_hours",
                2
            )
        )

        db.session.commit()

        flash(
            "Profile updated.",
            "success"
        )

    return render_template(
        "profile.html"
    )


# =========================================================
# DATABASE
# =========================================================

with app.app_context():

    db.create_all()


if __name__ == "__main__":

    app.run(
        debug=True
    )