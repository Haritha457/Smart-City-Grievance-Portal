import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
def classify_complaint(text):

    text = text.lower()

    electrical = [
        "light",
        "street light",
        "electricity",
        "power",
        "power cut",
        "current"
    ]

    water = [
        "water",
        "pipe",
        "leakage",
        "tap"
    ]

    sanitation = [
        "drain",
        "drainage",
        "garbage",
        "waste",
        "overflow",
        "overflowing",
        "mosquito",
        "sewage"
    ]

    if any(word in text for word in electrical):
        return "Electrical", "Medium"

    elif any(word in text for word in water):
        return "Water Supply", "High"

    elif any(word in text for word in sanitation):
        return "Sanitation", "High"

    else:
        return "General", "Low"
def detect_anomaly(text):

    text = text.lower()

    if len(text) < 10:
        return 1

    if text.count("a") > len(text) * 0.5:
        return 1

    return 0  

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
@app.route('/dashboard')
def dashboard():

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
        category=category
    )
if __name__ == '__main__':
    app.run(debug=True)