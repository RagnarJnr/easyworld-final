from flask import Flask, request, redirect, flash, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///messages.db'
db = SQLAlchemy(app)

# Image upload config
UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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
    image_filename = db.Column(db.String(255), nullable=True)
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
        title = request.form.get("title")
        content = request.form.get("content")
        author = request.form.get("author", "Admin")

        if not title or not content:
            return jsonify({"error": "Title and content are required"}), 400

        # Save uploaded image if present
        image_file = request.files.get("image")
        image_filename = None
        if image_file:
            image_filename = image_file.filename
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)

        new_post = BlogPost(
            title=title,
            content=content,
            author=author,
            image_url=f"/static/uploads/{image_filename}" if image_filename else None,
            image_filename=image_filename
        )
        db.session.add(new_post)
        db.session.commit()

        return jsonify({"status": "success", "id": new_post.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/edit_blog/<int:post_id>", methods=["POST"])
def edit_blog(post_id):
    try:
        post = BlogPost.query.get_or_404(post_id)

        post.title = request.form.get("title", post.title)
        post.content = request.form.get("content", post.content)
        post.author = request.form.get("author", post.author)

        image_file = request.files.get("image")
        if image_file and image_file.filename != "":
            image_filename = image_file.filename
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], image_filename)
            image_file.save(image_path)
            post.image_filename = image_filename

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

@app.route("/manage_blogs")
def manage_blogs():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template("manage_blogs.html", posts=posts)


# -------------------- DB INIT --------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=False)










