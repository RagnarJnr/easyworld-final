from flask import Flask, request, redirect, flash, render_template, jsonify
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

# Blog post model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    author = db.Column(db.String(100), default="Admin")
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

# -------------------- CONTACT --------------------
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

# -------------------- BLOG API --------------------
@app.route('/api/get_blogs', methods=['GET'])
def get_blogs():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return jsonify([
        {
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "image_url": p.image_url,
            "author": p.author,
            "created_at": p.created_at.strftime("%Y-%m-%d %H:%M")
        } for p in posts
    ])

@app.route('/api/add_blog', methods=['POST'])
def add_blog():
    try:
        data = request.get_json()
        if not data.get("title") or not data.get("content"):
            return jsonify({"error": "Title and content are required"}), 400

        new_post = BlogPost(
            title=data["title"],
            content=data["content"],
            image_url=data.get("image_url"),
            author=data.get("author", "Admin")
        )
        db.session.add(new_post)
        db.session.commit()
        return jsonify({"status": "success", "id": new_post.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Edit a blog post
@app.route('/api/edit_blog/<int:post_id>', methods=['PUT'])
def edit_blog(post_id):
    try:
        data = request.get_json()
        post = BlogPost.query.get_or_404(post_id)

        post.title = data.get("title", post.title)
        post.content = data.get("content", post.content)
        post.image_url = data.get("image_url", post.image_url)
        post.author = data.get("author", post.author)

        db.session.commit()
        return jsonify({"status": "success", "message": "Blog updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✅ Delete a blog post
@app.route('/api/delete_blog/<int:post_id>', methods=['DELETE'])
def delete_blog(post_id):
    try:
        post = BlogPost.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({"status": "success", "message": "Blog deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -------------------- PAGES --------------------
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
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('dashboard.html', messages=messages, posts=posts)

# -------------------- DB INIT --------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)



