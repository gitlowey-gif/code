from __main__ import app
from flask import Flask, render_template, url_for, session, request, redirect, flash
from hashlib import md5
from db_connector import database
from functools import wraps

db = database()

# ---------------------------
# Login required decorator
# ---------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------
# Home page
# ---------------------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------------------
# User registration
# ---------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        email = request.form.get("email")
        address = request.form.get("address")
        phone = request.form.get("phone", "")
        password = request.form.get("password")

        hashed_password = md5(password.encode()).hexdigest()

        try:
            # Insert new user
            db.updateDB(
                "INSERT INTO user (firstname, lastname, email, phone_number, address, password) VALUES (?,?,?,?,?,?)",
                (first_name, last_name, email, phone, address, hashed_password)
            )
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('register'))

        flash('Registration successful!', 'success')
        return redirect(url_for('profile'))
        
    return render_template('register.html')

# ---------------------------
# User login
# ---------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        hashed_password = md5(password.encode()).hexdigest()

        user = db.queryDB("SELECT * FROM user WHERE email = ?", [email])

        if user and user[0]['Password'] == hashed_password:
            session['email'] = user[0]['Email']
            session['first_name'] = user[0]['Firstname']
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# ---------------------------
# Logout
# ---------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

# ---------------------------
# User profile
# ---------------------------
@app.route('/profile')
@login_required
def profile():
    user_email = session['email']
    user = db.queryDB("SELECT * FROM user WHERE Email = ?", [user_email])[0]

    # Fetch bookings and separate by type
    bookings = db.queryDB("SELECT space, booking_date, hours, rate FROM booking WHERE name = ?", [user['FirstName']])
    space_bookings = [b for b in bookings if b['space'] in ["norwich", "ipswich", "wymondham"]]
    tool_bookings = [b for b in bookings if b['space'] not in ["norwich", "ipswich", "wymondham"]]

    return render_template("profile.html", user=user, space_bookings=space_bookings, tool_bookings=tool_bookings)

# ---------------------------
# Space booking page
# ---------------------------
@app.route('/space')
@login_required
def space():
    return render_template('space.html')

# ---------------------------
# Book a specific space
# ---------------------------
@app.route('/book/<space>', methods=['GET', 'POST'])
def book_space(space):
    spaces = {"norwich": 20, "ipswich": 20, "wymondham": 20}

    if space not in spaces:
        flash("Invalid booking space.", "danger")
        return redirect(url_for('home'))

    base_rate = spaces[space]

    if request.method == 'POST':
        try:
            from datetime import date

            hours = int(request.form.get('hours', 1))
            name = request.form.get('full_name')
            email = request.form.get('email')
            address = request.form.get('address')
            booking_date = request.form.get('booking_date')

            booking_date_obj = date.fromisoformat(booking_date)
            if booking_date_obj < date.today():
                flash("Booking date cannot be in the past.", "danger")
                return redirect(url_for('book_space', space=space))

            total_rate = hours * base_rate

            db.updateDB(
                """INSERT INTO booking (space, name, email, address, booking_date, hours, rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (space, name, email, address, booking_date, hours, total_rate)
            )

            flash(f"{space.title()} booking confirmed! 🎉", "success")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('book_space', space=space))

    return render_template('book_space.html', space=space, base_rate=base_rate)

# ---------------------------
# Tool booking page
# ---------------------------
@app.route('/tool')
@login_required
def tool():
    return render_template('tool.html')

# ---------------------------
# Book a specific tool
# ---------------------------
@app.route('/book-tool/<tool>', methods=['GET', 'POST'])
def book_tool(tool):
    tools = {
        "angle_grinder": 10,
        "hammer_drill": 15,
        "circular_saw": 12,
        "drill": 8,
        "vacuum": 9
    }

    if tool not in tools:
        flash("Invalid tool selected.", "danger")
        return redirect(url_for('home'))

    base_rate = tools[tool]

    if request.method == 'POST':
        try:
            from datetime import date

            hours = int(request.form.get('hours', 1))
            name = request.form.get('full_name')
            email = request.form.get('email')
            address = request.form.get('address')            
            booking_date = request.form.get('booking_date')

            booking_date_obj = date.fromisoformat(booking_date)
            if booking_date_obj < date.today():
                flash("Booking date cannot be in the past.", "danger")
                return redirect(url_for('book_tool', tool=tool))

            total_rate = hours * base_rate

            db.updateDB(
                """INSERT INTO booking (space, name, email, address, booking_date, hours, rate)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (tool, name, email, address, booking_date, hours, total_rate)
            )

            flash(f"{tool.title()} booking confirmed! 🎉", "success")
            return redirect(url_for('home'))

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return redirect(url_for('book_tool', tool=tool))

    return render_template('book_tool.html', tool=tool, base_rate=base_rate)

# ---------------------------
# Static informational pages
# ---------------------------
@app.route('/privacy-policy')
def privacy():
    return render_template('privacy-policy.html')

@app.route('/accessibility')
def accessibility():
    return render_template('accessibility.html')

@app.route('/lesson')
@login_required
def lesson():
    return render_template('lesson.html')

@app.route('/cart')
@login_required
def cart():
    return render_template('cart.html')

# ---------------------------
# Contact form
# ---------------------------
@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get("name")
        email = request.form.get("email")
        subject = request.form.get("subject")
        message = request.form.get("message")

        try:
            db.updateDB(
                "INSERT INTO contact (name, email, subject, message) VALUES (?,?,?,?)",
                (name, email, subject, message)
            )
            flash("Message sent successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('contact'))

    return render_template('contact.html')

# ---------------------------
# Feedback form
# ---------------------------
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        rating = request.form.get("rating")
        issue = request.form.get("issue")
        comment = request.form.get("comment")

        try:
            db.updateDB(
                "INSERT INTO feedback (rating, issue, comment) VALUES (?, ?, ?)",
                (rating, issue, comment)
            )
            flash("Thank you for your feedback!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('contact'))

    return render_template('contact.html')