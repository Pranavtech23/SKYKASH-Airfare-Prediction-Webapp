from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from model import predict_fare
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
app = Flask(__name__)
app.secret_key = 'super-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# User model (unchanged)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists, please login.', 'error')
            return redirect(url_for('login'))
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('predict'))
        flash('Invalid credentials, try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/predict', methods=['GET', 'POST'])
def predict():

    if 'user' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    # GET always clean page
    if request.method == 'GET':
        return render_template('predict.html')

    # POST logic
    form = request.form

    try:
        source = form['source']
        destination = form['destination']

        dep_date = form['dep_date']
        arr_date = form['arr_date']
        dep_time = form['dep_time']
        arr_time = form['arr_time']

        # ---------- VALIDATIONS ----------

        if source == destination:
            flash("Source and destination cannot be same.", "error")
            return redirect(url_for('predict'))

        dep_dt = datetime.strptime(dep_date + " " + dep_time, "%Y-%m-%d %H:%M")
        arr_dt = datetime.strptime(arr_date + " " + arr_time, "%Y-%m-%d %H:%M")

        from datetime import timedelta
        now = datetime.now() - timedelta(minutes=2)

        if dep_dt < now:
            flash("Cannot select past departure time.", "error")
            return redirect(url_for('predict'))

        if arr_dt <= dep_dt:
            flash("Arrival must be after departure.", "error")
            return redirect(url_for('predict'))


        # ---------- ML ----------
        price = predict_fare(form)

        prediction = {
            'price': float(price),
            'success': True,
            'airline': form['airline'],
            'source': form['source'],
            'destination': form['destination'],
            'stops': form['stops'],
            'dep_date': form['dep_date'],
            'dep_time': form['dep_time'],
            'arr_date': form['arr_date'],
            'arr_time': form['arr_time']
        }

        return render_template('predict.html', prediction=prediction)


    except Exception as e:
        flash(f"Prediction failed: {str(e)}", "error")
        return redirect(url_for('predict'))

@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    data = request.form

    filename = "flight_prediction.pdf"

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    content = []

    # ---------- WEBSITE HEADER ----------
    content.append(Paragraph("<b>✈ SkyKash</b>", styles["Title"]))
    content.append(Paragraph("www.skykash.com", styles["Normal"]))
    content.append(Spacer(1, 15))

    # ---------- PRICE ----------
    content.append(
        Paragraph(
            f"<font size=16><b>Predicted Flight Price: ₹{data['price']}</b></font>",
            styles["Heading2"]
        )
    )

    content.append(Spacer(1, 15))

    # ---------- TABLE DATA ----------
    table_data = [
        ["Airline", data["airline"]],
        ["Route", f"{data['source']} → {data['destination']}"],
        ["Stops", "Non-stop" if data["stops"] == "0" else data["stops"]],
        ["Departure", f"{data['dep_date']} @ {data['dep_time']}"],
        ["Arrival", f"{data['arr_date']} @ {data['arr_time']}"],
    ]

    table = Table(table_data, colWidths=[200, 300])

    table.setStyle(TableStyle([

        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),

        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),

        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),

        ("BACKGROUND", (0, 0), (-1, -1), colors.beige),

    ]))

    content.append(table)
    content.append(Spacer(1, 20))

    # ---------- FOOTER ----------
    content.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %b %Y | %H:%M')}",
            styles["Normal"]
        )
    )

    content.append(Paragraph("Thank you for using SkyKash...Visit again!!!", styles["Normal"]))

    doc.build(content)

    return send_file(filename, as_attachment=True)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    return render_template('booking.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('base.html', title='Page Not Found', content='The page you requested was not found.'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('base.html', title='Server Error', content='Something went wrong on the server.'), 500

if __name__ == '__main__':
    app.run(debug=True)  # Keep debug=True for development
