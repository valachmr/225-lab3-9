from flask import Flask, request, jsonify, render_template_string, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Needed for flash messages

# Database file path
DATABASE = os.environ.get('DATABASE', 'demo.db')

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row  # This enables name-based access to columns
    return db

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL
            );
        ''')
        db.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()

        name_valid, name_error = validate_name(name)
        phone_valid, phone_error = validate_phone(phone)

        if not name_valid:
            flash(name_error, 'error')
            return redirect(url_for('index'))
        if not phone_valid:
            flash(phone_error, 'error')
            return redirect(url_for('index'))

        db = get_db()
        db.execute('INSERT INTO contacts (name, phone) VALUES (?, ?)', (name, phone))
        db.commit()
        flash('Contact added successfully.', 'success')
        return redirect(url_for('index'))

    db = get_db()
    contacts = db.execute('SELECT * FROM contacts').fetchall()

    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Add Contact</title>
        </head>
        <body>
            <h2>Add Contact</h2>
            <form method="POST" action="/">
                <label for="name">Name:</label><br>
                <input type="text" id="name" name="name" required maxlength="100"><br>
                <label for="phone">Phone Number:</label><br>
                <input type="text" id="phone" name="phone" required maxlength="20"><br><br>
                <input type="submit" value="Submit">
            </form>

            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    <ul>
                        {% for category, msg in messages %}
                            <li style="color: {{ 'green' if category == 'success' else 'red' }};">{{ msg }}</li>
                        {% endfor %}
                    </ul>
                {% endif %}
            {% endwith %}

            {% if contacts %}
                <table border="1">
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Phone Number</th>
                    </tr>
                    {% for contact in contacts %}
                        <tr>
                            <td>{{ contact['id'] }}</td>
                            <td>{{ contact['name'] }}</td>
                            <td>{{ contact['phone'] }}</td>
                        </tr>
                    {% endfor %}
                </table>
            {% else %}
                <p>No contacts found.</p>
            {% endif %}
        </body>
        </html>
    ''', contacts=contacts)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    init_db()
    app.run(debug=debug_mode, host='0.0.0.0', port=port)