from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error
from flask_mail import Mail, Message
from itsdangerous import URLSafeSerializer, SignatureExpired
from functools import wraps

app = Flask(__name__)
app.secret_key = 'masadepan123'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'security_notes'
}

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'rkskelminipbl@gmail.com'
app.config['MAIL_PASSWORD'] = 'bfab nzlc icpr jdrp'
app.config['MAIL_DEFAULT_SENDER'] = 'rkskelminipbl@gmail.com'

mail = Mail(app)

s = URLSafeSerializer(app.secret_key)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM accounts WHERE email=%s", (email,))
            user = cursor.fetchone()
        except mysql.connector.Error as err:
            flash(f"Database connection error: {err}", "error")
            return redirect(url_for('login'))
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session.permanent = True
            flash("Login successful!", "success")
            return redirect(url_for('bigboss'))
        else:
            flash("Invalid credentials!", "error")

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        if not username or not email or not password:
            flash("Please fill in all the fields.", "error")
            return render_template('register.html')

        hashed_password = generate_password_hash(password)

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM accounts WHERE username = %s OR email = %s", (username, email))
            accounts = cursor.fetchone()

            if accounts:
                flash("Account already exists.", "error")
            else:
                cursor.execute("INSERT INTO accounts (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
                connection.commit()
                flash("Account successfully created!", "success")
                return redirect(url_for('login'))

        except Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("You need to log in first.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/request_reset', methods=['GET', 'POST'])
def request_reset():
    if request.method == 'POST':
        email = request.form['email']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM accounts WHERE email=%s", (email,))
            user = cursor.fetchone()

            if user:
                token = s.dumps(email, salt='email-reset-salt')
                reset_url = url_for('reset_password', token=token, _external=True)
                msg = Message('Password Reset Request', recipients=[email])
                msg.body = f'Click the link to reset your password: {reset_url}'
                mail.send(msg)
                flash("A password reset link has been sent to your email.", "success")
            else:
                flash("No account found with that email address.", "error")
        except Exception as e:
            flash(f"Database error: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return redirect(url_for('login'))

    return render_template('request_reset.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = s.loads(token, salt='email-reset-salt', max_age=3600)
    except SignatureExpired:
        flash("The reset link has expired!", "error")
        return redirect(url_for('request_reset'))
    except Exception:
        flash("Invalid or expired token!", "error")
        return redirect(url_for('request_reset'))

    if request.method == 'POST':
        new_password = request.form['password']
        confirm_password = request.form['confirm_password']

        if not new_password or not confirm_password:
            flash("Password cannot be empty.", "error")
            return redirect(request.url)
        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(request.url)

        hashed_password = generate_password_hash(new_password)

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("UPDATE accounts SET password=%s WHERE email=%s", (hashed_password, email))
            connection.commit()

            if cursor.rowcount == 0:
                flash("Failed to reset password. No account found with this email.", "error")
            else:
                flash("Your password has been reset successfully!", "success")
                return redirect(url_for('login'))
        except Exception as e:
            flash(f"Database error: {str(e)}", "error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    return render_template('reset_password.html', token=token)

@app.route('/bigboss', methods=['GET', 'POST'])
@login_required
def bigboss():
    notes = []

    if request.method == 'POST':
        content = request.form.get('content', '')
        result_type = request.form.get('type', '')

        user_id = session['user_id']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO encryption_results (user_id, content, type) VALUES (%s, %s, %s)",
                (user_id, content, result_type)
            )
            connection.commit()
            flash("Result saved successfully!", "success")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, content, type, created_at FROM encryption_results WHERE user_id = %s ORDER BY created_at DESC",
            (session['user_id'],)
        )
        notes = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('bigboss.html', notes=notes)

@app.route('/view_saved_notes')
@login_required
def view_saved_notes():
    notes = []
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, content, type, created_at FROM encryption_results WHERE user_id = %s ORDER BY created_at DESC",
            (session['user_id'],)
        )
        notes = cursor.fetchall()
    except mysql.connector.Error as err:
        flash(f"Kesalahan database: {err}", "error")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('view_note.html', notes=notes)

@app.route('/view_note/<int:id>')
@login_required
def view_note(id):
    note = None
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT content, type, created_at FROM encryption_results WHERE id = %s AND user_id = %s",
            (id, session['user_id'])
        )
        note = cursor.fetchone()

        if not note:
            flash("Note not found or you don't have permission to view it.", "error")
            return redirect(url_for('view_saved_notes'))
    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return render_template('view_note.html', note=note)

@app.route('/save_note', methods=['POST'])
@login_required
def save_note():
    data = request.json
    content = data.get('content')
    note_type = data.get('type')
    user_id = session['user_id']

    if not content or not note_type:
        return jsonify(success=False, error="Content and type are required!"), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO encryption_results (user_id, content, type) VALUES (%s, %s, %s)",
            (user_id, content, note_type)
        )
        connection.commit()
        return jsonify(success=True), 200
    except mysql.connector.Error as err:
        return jsonify(success=False, error=str(err)), 500
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
