from flask import Flask, render_template, request
import sqlite3
from datetime import date
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from flask import session, redirect, url_for
app = Flask(__name__)
app.secret_key = "secret123"

import os

def get_db():
    db_path = os.path.join(os.getcwd(), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')
@app.route('/')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = get_db()

    total_patients = conn.execute("SELECT COUNT(*) FROM patients").fetchone()[0]

    total_treatments = conn.execute("SELECT COUNT(*) FROM treatments").fetchone()[0]

    return render_template('dashboard.html',
                           total_patients=total_patients,
                           total_treatments=total_treatments)
@app.route('/report/<int:patient_id>')
def report(patient_id):
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()

    patient = conn.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    treatments = conn.execute("SELECT * FROM treatments WHERE patient_id=?", (patient_id,)).fetchall()

    from reportlab.platypus import SimpleDocTemplate, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
    from flask import send_file

    file_name = f"report_{patient_id}.pdf"

    doc = SimpleDocTemplate(file_name)
    styles = getSampleStyleSheet()

    content = []

    # Heading
    content.append(Paragraph("🦷 Dighi Dental Care", styles['Title']))
    content.append(Paragraph("Dental Treatment Invoice", styles['Heading2']))
    content.append(Paragraph(" ", styles['Normal']))

    # Patient info
    content.append(Paragraph(f"Patient: {patient['name']}", styles['Normal']))
    content.append(Paragraph(f"Mobile: {patient['mobile']}", styles['Normal']))
    content.append(Paragraph(" ", styles['Normal']))

    # 👉 THIS IS IMPORTANT
    total_cost = 0

    # Treatments loop
    for t in treatments:
        cost = t['cost'] if t['cost'] else 0
        total_cost += cost

        content.append(Paragraph(f"Treatment: {t['treatment']}", styles['Normal']))
        content.append(Paragraph(f"Date: {t['date']}", styles['Normal']))
        content.append(Paragraph(f"Cost: ₹{cost}", styles['Normal']))
        content.append(Paragraph(f"Next Visit: {t['next_visit']}", styles['Normal']))
        content.append(Paragraph(" ", styles['Normal']))

    # Total
    content.append(Paragraph(" ", styles['Normal']))
    content.append(Paragraph(f"Total Cost: ₹{total_cost}", styles['Title']))

    doc.build(content)

    return send_file(file_name, as_attachment=True)
@app.route('/reminders')
def reminders():
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()

    today = date.today().isoformat()

    patients = conn.execute("""
        SELECT patients.name, patients.mobile, treatments.next_visit
        FROM treatments
        JOIN patients ON patients.id = treatments.patient_id
        WHERE next_visit IS NOT NULL AND next_visit <= ?
    """, (today,)).fetchall()

    return render_template('reminders.html', patients=patients)
@app.route('/patients', methods=['GET', 'POST'])
def patients():
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()

    if request.method == 'POST':
        name = request.form['name']
        mobile = request.form['mobile']
        age = request.form['age']
        gender = request.form['gender']
        complaint = request.form['complaint']

        conn.execute("""
            INSERT INTO patients (name, mobile, age, gender, complaint)
            VALUES (?, ?, ?, ?, ?)
        """, (name, mobile, age, gender, complaint))
        conn.commit()

    patients = conn.execute("SELECT * FROM patients").fetchall()
    return render_template('patients.html', patients=patients)
@app.route('/treatment/<int:patient_id>', methods=['GET', 'POST'])
def treatment(patient_id):
    if 'user' not in session:
        return redirect('/login')
    conn = get_db()

    if request.method == 'POST':
        treatment = request.form['treatment']
        description = request.form['description']
        date = request.form['date']
        next_visit = request.form['next_visit']
        cost = request.form['cost']

        conn.execute("""
            INSERT INTO treatments (patient_id, treatment, description, date, next_visit, cost)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, treatment, description, date, next_visit, cost))
        conn.commit()

    treatments = conn.execute("""
        SELECT * FROM treatments WHERE patient_id=?
    """, (patient_id,)).fetchall()

    return render_template('treatment.html', treatments=treatments, patient_id=patient_id)

if __name__ == '__main__':
    app.run(debug=True)
    import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)