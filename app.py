import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Column
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# Database configuration (replace with your credentials)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Import your SQLAlchemy models here (defined later)
# db.init_app(app)  # Initialize with the app


# models.py
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

# User model (replace with your user data structure)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Post('{self.title}', '{self.content}')"

    def serialize(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'date_posted': self.date_posted.isoformat()  # Convert datetime to ISO format
            # 'author': self.user.username  # Assuming relationship with User model
        }


@app.route('/')
def index():
    posts = Post.query.all()  # Assuming you have a Post model
    # return render_template('index.html', posts=posts)
    return jsonify([post.serialize() for post in posts])


# ... Define other API endpoints for CRUD operations (explained later)
@app.route('/posts', methods=['GET'])
def get_all_posts():
    posts = Post.query.all()
    return jsonify([post.serialize() for post in posts])

@app.route('/posts/<int:post_id>', methods=['GET'])
def get_post(post_id):
    post = Post.query.get_or_404(post_id)
    return jsonify(post.serialize())

@app.route('/posts', methods=['POST'])
def create_post():
    # 1. Get data from request
    data = request.get_json()
    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Missing required fields'}), 400  # Bad request status code

    new_post = Post(title=data['title'], content=data['content'])
    db.session.add(new_post)
    
    try:
        db.session.commit()
    except Exception as e:
        # Handle database errors (e.g., rollback changes)
        print(f"Error creating post: {e}")
        return jsonify({'error': 'Internal server error'}), 500  # Internal server error

    return jsonify({'message': 'Post created successfully', 'post': new_post.serialize()}), 201  


@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()

    if not data or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Missing required fields'}), 400

    post = Post.query.get_or_404(post_id)
    post.title = data['title']
    post.content = data['content']

    try:
        db.session.commit()
        return jsonify(post.serialize())
    except Exception as e:
        return jsonify({'error': f'Error updating post: {str(e)}'}), 500

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    try:
        db.session.delete(post)
        db.session.commit()
        return jsonify({'message': 'Post deleted successfully'})
    except Exception as e:
        return jsonify({'error': f'Error deleting post: {str(e)}'}), 500



   # ... (rest of your Flask app code)

if __name__ == '__main__':
    # db.create_all()
    app.run(debug=True)


