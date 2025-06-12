from flask import Flask, request, redirect, flash, render_template
from flask_sqlalchemy import SQLAlchemy
import os


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

# Contact form model
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# Route to handle contact form
@app.route('/contact', methods=['POST'])
def contact():
    try:
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        if name and email and message:
            new_msg = ContactMessage(name=name, email=email, message=message)
            db.session.add(new_msg)
            db.session.commit()
            flash("Message saved successfully. EasyWorld will get back to you soon.")
        else:
            flash("Please fill all fields before submitting.")
    except Exception as e:
        flash("Something went wrong. Please try again.")

    return redirect(request.referrer or '/')


# Pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/overview')
def overview():
    return render_template('overview.html')

@app.route('/ventures')
def ventures():
    return render_template('ventures.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/dashboard')
def dashboard():
    messages = ContactMessage.query.order_by(ContactMessage.id.desc()).all()
    return render_template('dashboard.html', messages=messages)

# Safe way to create tables on first run
with app.app_context():
    db.create_all()



if __name__ == '__main__':
    app.run(debug=False)
