from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
import os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# =========================================================
# CONFIGURATION
# =========================================================

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///chess_academy.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# =========================================================
# USER MODEL
# =========================================================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


# =========================================================
# REGISTRATION MODEL
# =========================================================

class Registration(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_name = db.Column(
        db.String(100),
        nullable=False
    )

    age = db.Column(
        db.Integer,
        nullable=False
    )

    parent_name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    chess_level = db.Column(
        db.String(50),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Pending"
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


# =========================================================
# ENQUIRY MODEL
# =========================================================

class Enquiry(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        nullable=False
    )

    subject = db.Column(
        db.String(150),
        nullable=False
    )

    message = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    registration_status = request.args.get("status")

    return render_template(
        "index.html",
        registration_status=registration_status
    )

# =========================================================
# CREATE ACCOUNT
# =========================================================

@app.route("/create-account", methods=["GET", "POST"])
def create_account():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Check required fields
        if not name or not email or not phone or not password:

            flash(
                "Please fill all required fields.",
                "error"
            )

            return redirect(
                url_for("create_account")
            )

        # Check password
        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("create_account")
            )

        # Check existing email
        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return redirect(
                url_for("create_account")
            )

        # Hash password
        password_hash = generate_password_hash(
            password
        )

        # Create user
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            password_hash=password_hash
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Account created successfully! Please sign in.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "create_account.html"
    )


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        password = request.form.get(
            "password",
            ""
        )

        # Find user
        user = User.query.filter_by(
            email=email
        ).first()

        # Check login
        if user and check_password_hash(
            user.password_hash,
            password
        ):

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_email"] = user.email

            return redirect(
                url_for("home")
            )

        flash(
            "Invalid email or password.",
            "error"
        )

    return render_template(
        "login.html"
    )


# =========================================================
# FORGOT PASSWORD
# =========================================================

@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash(
                "No account found with this email.",
                "error"
            )

            return redirect(
                url_for("forgot_password")
            )

        session["reset_email"] = email

        return redirect(
            url_for("reset_password")
        )

    return render_template(
        "forgot_password.html"
    )


# =========================================================
# RESET PASSWORD
# =========================================================

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    if not session.get("reset_email"):

        flash(
            "Please enter your email first.",
            "error"
        )

        return redirect(
            url_for("forgot_password")
        )

    if request.method == "POST":

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not password or not confirm_password:

            flash(
                "Please enter both passwords.",
                "error"
            )

            return redirect(
                url_for("reset_password")
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("reset_password")
            )

        email = session.get(
            "reset_email"
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            session.pop(
                "reset_email",
                None
            )

            flash(
                "Account not found.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        user.password_hash = generate_password_hash(
            password
        )

        db.session.commit()

        session.pop(
            "reset_email",
            None
        )

        flash(
            "Password reset successfully! Please sign in.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "reset_password.html"
    )


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# =========================================================
# CHESS CLASS REGISTRATION
# =========================================================

@app.route("/register", methods=["POST"])
def register():

    student_name = request.form.get(
        "student_name",
        ""
    ).strip()

    age = request.form.get(
        "age",
        ""
    ).strip()

    parent_name = request.form.get(
        "parent_name",
        ""
    ).strip()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    chess_level = request.form.get(
        "chess_level",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()

    # Check empty fields
    if not student_name or not age or not parent_name or not phone or not email or not chess_level:

        flash(
            "Please fill all required registration fields.",
            "error"
        )

        return redirect(
            url_for("home") + "#registration"
        )

    # Check age
    try:

        age = int(age)

    except ValueError:

        flash(
            "Please enter a valid age.",
            "error"
        )

        return redirect(
            url_for("home") + "#registration"
        )

    if age < 3 or age > 100:

        flash(
            "Age must be between 3 and 100.",
            "error"
        )

        return redirect(
            url_for("home") + "#registration"
        )

    # Create registration
    new_registration = Registration(
        student_name=student_name,
        age=age,
        parent_name=parent_name,
        phone=phone,
        email=email,
        chess_level=chess_level,
        message=message
    )

    db.session.add(
        new_registration
    )

    db.session.commit()

    return redirect(
        url_for(
            "home",
            registration="success"
        ) + "#registration"
    )

# =========================================================
# CHECK REGISTRATION STATUS
# =========================================================

@app.route("/check-registration-status", methods=["POST"])
def check_registration_status():

    email = request.form.get("email", "").strip().lower()
    phone = request.form.get("phone", "").strip()

    # Check empty fields
    if not email or not phone:

        flash(
            "Please enter both email and phone number.",
            "error"
        )

        return redirect(
            url_for("home") + "#registration-status"
        )

    # Find registration using email + phone
    registration = Registration.query.filter_by(
        email=email,
        phone=phone
    ).order_by(
        Registration.created_at.desc()
    ).first()

    # Registration not found
    if not registration:

        return redirect(
            url_for(
                "home",
                status="not_found"
            ) + "#registration-status"
        )

    # Registration found
    return redirect(
        url_for(
            "home",
            status=registration.status
        ) + "#registration-status"
    )
# =========================================================
# ADMIN LOGIN / DASHBOARD
# =========================================================

ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "qwin123")


@app.route("/admin", methods=["GET", "POST"])
def admin():

    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        )

        password = request.form.get(
            "password",
            ""
        )

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:

            session["admin_logged_in"] = True

            return redirect(
                url_for("admin")
            )

        flash(
            "Invalid admin username or password.",
            "error"
        )

    # Check admin login
    if not session.get("admin_logged_in"):

        return render_template(
            "admin_login.html"
        )

    # =====================================================
    # SEARCH
    # =====================================================

    search = request.args.get(
        "search",
        ""
    ).strip()

    # =====================================================
    # LEVEL FILTER
    # =====================================================

    level = request.args.get(
        "level",
        ""
    ).strip()

    # =====================================================
    # STATUS FILTER
    # =====================================================

    status = request.args.get(
        "status",
        ""
    ).strip()

    # =====================================================
    # DATE SORT
    # =====================================================

    sort = request.args.get(
        "sort",
        "newest"
    ).strip()

    # Start query
    query = Registration.query

    # Search
    if search:

        query = query.filter(
            db.or_(
                Registration.student_name.ilike(
                    f"%{search}%"
                ),
                Registration.phone.ilike(
                    f"%{search}%"
                ),
                Registration.email.ilike(
                    f"%{search}%"
                )
            )
        )

    # Level filter
    if level:

        query = query.filter(
            Registration.chess_level == level
        )

    # Status filter
    if status:

        query = query.filter(
            Registration.status == status
        )

    # Sorting
    if sort == "oldest":

        query = query.order_by(
            Registration.created_at.asc()
        )

    else:

        query = query.order_by(
            Registration.created_at.desc()
        )

    registrations = query.all()

    # =====================================================
    # STATISTICS
    # =====================================================

    total_registrations = Registration.query.count()

    beginner_count = Registration.query.filter_by(
        chess_level="Beginner"
    ).count()

    intermediate_count = Registration.query.filter_by(
        chess_level="Intermediate"
    ).count()

    advanced_count = Registration.query.filter_by(
        chess_level="Advanced"
    ).count()

    # ⭐ ENQUIRY COUNT
    enquiry_count = Enquiry.query.count()

    # =====================================================
    # SHOW DASHBOARD
    # =====================================================

    return render_template(
        "admin.html",
        registrations=registrations,
        search=search,
        level=level,
        status=status,
        sort=sort,
        total_registrations=total_registrations,
        beginner_count=beginner_count,
        intermediate_count=intermediate_count,
        advanced_count=advanced_count,
        enquiry_count=enquiry_count
    )


# =========================================================
# SUBMIT ENQUIRY FROM HOME PAGE
# =========================================================

@app.route("/enquiry", methods=["POST"])
def submit_enquiry():

    name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip().lower()

    phone = request.form.get(
        "phone",
        ""
    ).strip()

    subject = request.form.get(
        "subject",
        ""
    ).strip()

    message = request.form.get(
        "message",
        ""
    ).strip()

    # Check required fields
    if not name or not email or not phone or not subject or not message:

        flash(
            "Please fill all enquiry fields.",
            "error"
        )

        return redirect(
            url_for("home") + "#enquiry"
        )

    new_enquiry = Enquiry(
        name=name,
        email=email,
        phone=phone,
        subject=subject,
        message=message
    )

    db.session.add(
        new_enquiry
    )

    db.session.commit()

    return redirect(
        url_for(
            "home",
            enquiry="success"
        ) + "#enquiry"
    )


# =========================================================
# ADMIN ENQUIRIES
# =========================================================

@app.route("/admin/enquiries")
def admin_enquiries():

    # Only logged-in admin can access
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    # Get all enquiries - newest first
    enquiries = Enquiry.query.order_by(
        Enquiry.created_at.desc()
    ).all()

    return render_template(
        "admin_enquiries.html",
        enquiries=enquiries
    )


# =========================================================
# DELETE ENQUIRY
# =========================================================

@app.route(
    "/admin/enquiry/delete/<int:enquiry_id>",
    methods=["POST"]
)
def delete_enquiry(enquiry_id):

    # Only logged-in admin can delete
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    # Find enquiry
    enquiry = Enquiry.query.get_or_404(
        enquiry_id
    )

    # Delete enquiry
    db.session.delete(
        enquiry
    )

    db.session.commit()

    # Return to enquiry page
    return redirect(
        url_for("admin_enquiries")
    )


# =========================================================
# EXPORT REGISTRATIONS CSV
# =========================================================

@app.route("/admin/export-csv")
def export_csv():

    # Only logged-in admin can export
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    registrations = Registration.query.order_by(
        Registration.id.desc()
    ).all()

    csv_data = (
        "ID,Student Name,Age,Parent / Guardian,"
        "Phone,Email,Chess Level,Message,Registered On\n"
    )

    for registration in registrations:

        csv_data += (
            f'"{registration.id}",'
            f'"{registration.student_name}",'
            f'"{registration.age}",'
            f'"{registration.parent_name}",'
            f'"{registration.phone}",'
            f'"{registration.email}",'
            f'"{registration.chess_level}",'
            f'"{registration.message or ""}",'
            f'"{registration.created_at}"\n'
        )

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=qwin_chess_registrations.csv"
        }
    )


# =========================================================
# CONTACT PAGE
# =========================================================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form.get(
            "name",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip().lower()

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        # Check required fields
        if not name or not phone or not email or not subject or not message:

            flash(
                "Please fill all enquiry fields.",
                "error"
            )

            return redirect(
                url_for("contact")
            )

        new_enquiry = Enquiry(
            name=name,
            phone=phone,
            email=email,
            subject=subject,
            message=message
        )

        db.session.add(
            new_enquiry
        )

        db.session.commit()

        flash(
            "Your enquiry has been sent successfully!",
            "success"
        )

        return redirect(
            url_for("contact")
        )

    return render_template(
        "contact.html"
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@app.route("/admin/logout")
def admin_logout():

    session.pop(
        "admin_logged_in",
        None
    )

    return redirect(
        url_for("admin")
    )


# =========================================================
# DELETE REGISTRATION
# =========================================================

@app.route(
    "/admin/delete-registration/<int:registration_id>",
    methods=["POST"]
)
def delete_registration(registration_id):

    # Only logged-in admin can delete
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    registration = Registration.query.get_or_404(
        registration_id
    )

    db.session.delete(
        registration
    )

    db.session.commit()

    return redirect(
        url_for("admin")
    )


# =========================================================
# UPDATE REGISTRATION STATUS
# =========================================================

@app.route(
    "/admin/update-status/<int:registration_id>",
    methods=["POST"]
)
def update_status(registration_id):

    # Only logged-in admin can update status
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    registration = Registration.query.get_or_404(
        registration_id
    )

    new_status = request.form.get(
        "status"
    )

    # Allow only these statuses
    if new_status not in [
        "Pending",
        "Approved",
        "Rejected"
    ]:

        flash(
            "Invalid status.",
            "error"
        )

        return redirect(
            url_for("admin")
        )

    registration.status = new_status

    db.session.commit()

    return redirect(
        url_for("admin")
    )


# =========================================================
# VIEW STUDENT DETAILS
# =========================================================

@app.route(
    "/admin/student/<int:registration_id>"
)
def view_student(registration_id):

    # Only logged-in admin can view
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    registration = Registration.query.get_or_404(
        registration_id
    )

    return render_template(
        "student_details.html",
        registration=registration
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@app.route(
    "/admin/student/edit/<int:registration_id>",
    methods=["GET", "POST"]
)
def edit_student(registration_id):

    # Only logged-in admin can edit
    if not session.get("admin_logged_in"):

        return redirect(
            url_for("admin")
        )

    registration = Registration.query.get_or_404(
        registration_id
    )

    # Update
    if request.method == "POST":

        registration.student_name = request.form.get(
            "student_name",
            ""
        ).strip()

        registration.age = request.form.get(
            "age",
            ""
        ).strip()

        registration.parent_name = request.form.get(
            "parent_name",
            ""
        ).strip()

        registration.phone = request.form.get(
            "phone",
            ""
        ).strip()

        registration.email = request.form.get(
            "email",
            ""
        ).strip().lower()

        registration.chess_level = request.form.get(
            "chess_level",
            ""
        ).strip()

        registration.status = request.form.get(
            "status",
            "Pending"
        ).strip()

        registration.message = request.form.get(
            "message",
            ""
        ).strip()

        db.session.commit()

        return redirect(
            url_for("admin")
        )

    return render_template(
        "edit_student.html",
        registration=registration
    )


# =========================================================
# DATABASE
# =========================================================

with app.app_context():

    db.create_all()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )