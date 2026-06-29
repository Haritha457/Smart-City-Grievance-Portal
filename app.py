import sqlite3
from flask import Flask, render_template, request, redirect, session
import pickle

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
with open("model/complaint_classifier.pkl", "rb") as file:
    ml_model = pickle.load(file)
def classify_complaint(text):

    category = ml_model.predict([text])[0]

    if category == "Electrical":
        priority = "Medium"

    elif category == "Water Supply":
        priority = "High"

    elif category == "Sanitation":
        priority = "High"

    else:
        priority = "Low"

    return category, priority
def detect_anomaly(text):

    text = text.lower()

    if len(text) < 10:
        return 1

    if text.count("a") > len(text) * 0.5:
        return 1

    return 0  


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('sample_database.db')
        cursor = conn.cursor()

        cursor.execute(
        "SELECT * FROM admins WHERE username=? AND password=?",
        (username, password)
        )

        admin = cursor.fetchone()

        conn.close()

        if admin:
            session['admin'] = True
            return redirect('/dashboard')

        return redirect('/login')

    return render_template('login.html')
@app.route('/', methods=['GET', 'POST'])
def home():

    if request.method == 'POST':
        complaint = request.form['complaint'].strip()
        category, priority= classify_complaint(complaint)
        is_anomaly = detect_anomaly(complaint)

        
        if not complaint:
            return render_template('index.html')

        conn = sqlite3.connect('sample_database.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO complaints (text,category,priority, is_anomaly) VALUES (?,?,?,?)",
            (complaint,category,priority,is_anomaly)
        )

        conn.commit()
        conn.close()

        print("Complaint saved to database:")
        print(complaint)

    return render_template('index.html')
@app.route('/logout')
def logout():

    session.pop('admin', None)

    return redirect('/login')
@app.route('/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect('/login')
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    priority = request.args.get('priority', '')
    status = request.args.get('status', '')

    conn = sqlite3.connect('sample_database.db')
    cursor = conn.cursor()

    
    query = "SELECT * FROM complaints WHERE 1=1"
    params = []

    if search:
      query += " AND text LIKE ?"
      params.append('%' + search + '%')

    if category:
      query += " AND category=?"
      params.append(category)

    if priority:
      query += " AND priority=?"
      params.append(priority)

    if status:
      query += " AND status=?"
      params.append(status)

    cursor.execute(query, params)

    complaints = cursor.fetchall()
        
    cursor.execute(
        "SELECT COUNT(*) FROM complaints"
    )
    total = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE category='Electrical'
        """
    )
    electrical = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE category='Water Supply'
        """
    )
    water = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE category='Sanitation'
        """
    )
    sanitation = cursor.fetchone()[0]
    cursor.execute(
    """
    SELECT COUNT(*) FROM complaints
    WHERE category='General'
    """
    )
    general = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE is_anomaly=1
        """
    )
    suspicious = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE status='Pending'
        """
    )
    pending = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE status='In Progress'
        """
    )
    in_progress = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE status='Resolved'
        """
        )
    resolved = cursor.fetchone()[0]
    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE priority='High'
        """
        )
    high_priority = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE priority='Medium'
        """
        )
    medium_priority = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*) FROM complaints
        WHERE priority='Low'
        """
        )
    low_priority = cursor.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        complaints=complaints,
        total=total,
        electrical=electrical,
        water=water,
        sanitation=sanitation,
        general=general,
        suspicious=suspicious,
        search=search,
        category=category,
        pending=pending,
        in_progress=in_progress,
        resolved=resolved,
        high_priority=high_priority,
        medium_priority=medium_priority,
        low_priority=low_priority
    )
@app.route('/update_status/<int:complaint_id>')
def update_status(complaint_id):

    conn = sqlite3.connect('sample_database.db')
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT status
        FROM complaints
        WHERE id=?
        """,
        (complaint_id,)
    )

    current_status = cursor.fetchone()[0]

    if current_status == "Pending":
        new_status = "In Progress"

    elif current_status == "In Progress":
        new_status = "Resolved"

    else:
        new_status = "Pending"

    cursor.execute(
        """
        UPDATE complaints
        SET status=?
        WHERE id=?
        """,
        (new_status, complaint_id)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')
if __name__ == '__main__':
    app.run(debug=True)
