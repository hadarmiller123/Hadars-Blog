""" Flask Personal Blog Website v.2 """

import os
from dotenv import load_dotenv
import datetime
import smtplib
from email.message import EmailMessage
from constants import GUEST_CLASSIFICATION, UNAUTHORIZED_ERROR_MSG, UNREACHABLE_ERROR_MSG
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, Boolean, Text, ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user
from flask_bootstrap import Bootstrap5
from forms import ContactForm, EditPostForm, CreatePostForm, RegisterForm, LoginForm, CommentForm
from flask_ckeditor import CKEditor

load_dotenv()

# Initialize Flask application
app = Flask(__name__)
Bootstrap5(app) # Enable Bootstrap for styling
ckeditor = CKEditor(app) # Enable ckeditor for much convenient text editing
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")

# Initialize Flask login manager
login_manager = LoginManager()
login_manager.init_app(app)

# Creating database
class Base(DeclarativeBase):
    """ Base model class for SQLAlchemy ORM """
    pass

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(db.Model, UserMixin):
    """ Model representing user's table in the database """
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    classification: Mapped[int] = mapped_column(Integer) # 1 - Users, 2 - Admin and above (0 will be undocumented guests)
    comments = relationship('Comment', back_populates='comment_user')

    @property
    def get_classification(self) -> int:
        return self.classification

class Post(db.Model):
    """ Model representing post's table in the database """
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    subtitle: Mapped[str] = mapped_column(String(150), nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    date: Mapped[datetime.datetime] = mapped_column(Date, default=datetime.datetime.now().date(), nullable=False)
    comments = relationship('Comment', back_populates='parent_post', cascade="all,delete")

class Comment(db.Model):
    """ Model representing comment's table in the database """
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    comment_user = relationship('User', back_populates='comments')

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey('posts.id', ondelete="CASCADE"))
    parent_post = relationship('Post', back_populates='comments')
    body: Mapped[str] = mapped_column(String, nullable=False)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False) # For admin needs

# Create the database with admin credentials
with app.app_context():
    db.create_all()
    # make admin user with top permissions
    new_user = User(email=os.environ.get('ADMIN_EMAIL'),
                    password=generate_password_hash(password=os.environ.get('ADMIN_PASSWORD'), method='pbkdf2:sha256', salt_length=8),
                    name=os.environ.get('ADMIN_NAME'),
                    classification=2)
    db.session.add(new_user)
    db.session.commit()

def get_classification_level() -> int:
    """
    Get the classification level for each user, admin or guest

    Returns:
        int: the classification level
    """
    if current_user.is_authenticated:
        return current_user.get_classification
    return GUEST_CLASSIFICATION

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

@app.route("/register", methods=['GET', 'POST'])
def register():
    """
    Handles registration functionality.

    Returns:
        str: home.html if user is already authenticated or made a successful registration
        otherwise register.html with error messages
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        form = RegisterForm()

        if form.validate_on_submit():
            # Checking if the email provided already in use
            user_found = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()

            if not user_found:
                # make a new user and log him in
                new_user = User(email=form.email.data,
                                password=generate_password_hash(password=form.password.data, method='pbkdf2:sha256', salt_length=8),
                                name=form.name.data,
                                classification=1)
                db.session.add(new_user)
                db.session.commit()

                login_user(new_user)
                return redirect(url_for('home'))
            else:
                form.email.errors.append('This email address already in use')
        return render_template('register.html', form=form, classification_level=get_classification_level())

@app.route("/login", methods=['GET', 'POST'])
def login():
    """
    Handles logging in functionality.

    Returns:
        str: home.html if user is already authenticated or made a successful login
        otherwise login.html with error messages
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    else:
        form = LoginForm()

        if form.validate_on_submit():
            # Query the database for the user based on the entered email
            user_found = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()

            if user_found:
                # Check if the password matches the hashed password
                if check_password_hash(user_found.password, form.password.data):
                    login_user(user_found)  # Log the user in
                    return redirect(url_for('home'))
                else:
                    # Add error message if the password is incorrect
                    form.password.errors.append('Incorrect password, Please try again')
            else:
                # Add error message if the email is not found in the database
                form.email.errors.append('Email not found, Please try again')
        return render_template('login.html', form=form, classification_level=get_classification_level())

@app.route("/logout", methods=['GET'])
def logout():
    """
    Logs out the currently authenticated user.

    Returns:
        str: Redirect to the home page after logging out
        or to login.html when trying to log out and hasn't logged in yet.
    """
    if current_user.is_authenticated:
        logout_user()
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def home():
    """
    Fetches blog posts from the blog database and renders the home page

    Returns:
        str: home.html with the fetched blog posts
    """
    all_posts = db.session.execute(db.select(Post).order_by(Post.id)).scalars().all()
    return render_template('home.html', posts=all_posts, classification_level=get_classification_level())

@app.route('/about', methods=['GET'])
def about():
    """
    Renders the 'About' page

    Returns:
        str: about.html
    """
    return render_template('about.html', classification_level=get_classification_level())

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Handles contact form submissions via email

    Returns:
        str: contact.html with success or error messages after validation
    """
    successful_message = None
    is_sent = False

    form = ContactForm()
    if form.validate_on_submit():
        # Extract form data
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        message = form.message.data
        subject = "New Form Submission - Hadar's Blog"

        try:
            # Generate the email using UTF-8
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = os.environ.get("EMAIL")
            msg['To'] = os.environ.get("EMAIL")
            msg.set_content(
                f"name: {name}\nemail: {email}\nphone: {phone}\nmessage: {message}",
                charset='utf-8'
            )

            # Send the email
            with smtplib.SMTP("smtp.gmail.com") as connection:
                connection.starttls()
                connection.login(
                    user=os.environ.get("EMAIL"),
                    password=os.environ.get("PASSWORD")
                )
                connection.send_message(msg)

            successful_message = 'The form was successfully sent :)'
            is_sent = True

        except Exception as e:
            successful_message = 'We could not send the form at this moment, please try again later.'

    return render_template('contact.html', form=form, isSent=is_sent, status_message=successful_message,
        classification_level=get_classification_level())


@app.route("/create", methods=['GET', 'POST'])
def create_post():
    """
    Handles the creation of a new blog post.

    Returns:
        str: Redirect to the new post or renders create form if validation fails.
    """
    # Cannot enter the creation route if not admin
    if get_classification_level() < 2:
        return render_template('error.html', error_message=UNAUTHORIZED_ERROR_MSG,
                               classification_level=get_classification_level())
    form = CreatePostForm()
    if form.validate_on_submit():
        # Check whether the title is already exist and if so generate an error page
        matching_post = db.session.execute(db.select(Post).where(Post.title == form.title.data)).scalars().all()
        if matching_post:
            form.title.errors.append('A post with that title is already exist')
        else:
            # Creating new post in database
            new_post = Post(
                title = form.title.data,
                subtitle = form.subtitle.data,
                img_url = form.img_url.data,
                author = form.author.data,
                body = form.body.data
            )
            db.session.add(new_post)
            db.session.commit()

            return redirect(url_for('show_post', post_id=new_post.id))
    return render_template('create.html', form=form, classification_level=get_classification_level())

@app.route('/post/<int:post_id>', methods=['GET'])
def show_post(post_id):
    """
    Fetches a specific blog post by its ID and renders the post page

    Args:
        post_id (int): The ID of the blog post to fetch

    Returns:
        str: post.html with the matching post data, or error.html if not found
    """
    # Search for the matching post
    post_to_show = db.session.get(Post, post_id)

    # Get all the comments related to the post id
    comments = db.session.execute(db.select(Comment).where(Comment.post_id == post_id).order_by(Comment.approved.desc())).scalars().all()

    if post_to_show:
        return render_template('post.html', post=post_to_show, comments=comments,
                               classification_level=get_classification_level())
    else:
        return render_template('error.html', error_message=UNREACHABLE_ERROR_MSG,
                               classification_level=get_classification_level())

@app.route("/edit/<int:post_id>", methods=['GET', 'POST'])
def edit_post(post_id):
    """
    Fetches a blog post by its ID and allows editing if found.

    Args:
        post_id (int): The ID of the blog post to edit.

    Returns:
        str: edit.html with the form if the post found, else error.html.
    """
    # Cannot enter the editing route if not admin
    if get_classification_level() < 2:
        return render_template('error.html', error_message=UNAUTHORIZED_ERROR_MSG,
                               classification_level=get_classification_level())
    # Getting post by id
    post_to_update = db.session.get(Post, post_id)

    if post_to_update:
        form = EditPostForm()
        if form.validate_on_submit():
            # Updating the post relevant fields and then commit the changes
            post_to_update.title = form.title.data
            post_to_update.subtitle = form.subtitle.data
            post_to_update.img_url = form.img_url.data
            post_to_update.author = form.author.data
            post_to_update.body = form.body.data
            post_to_update.date = datetime.datetime.now().date()

            db.session.commit()

            return redirect(url_for('show_post', post_id=post_id))
        return render_template('edit.html', form=form, classification_level=get_classification_level())
    else:
        return render_template('error.html', error_message=UNREACHABLE_ERROR_MSG,
                               classification_level=get_classification_level())

@app.route("/delete/<int:post_id>", methods=['GET'])
def delete_post(post_id):
    """
    Deletes a blog post by its ID if found.

    Args:
        post_id (int): The ID of the blog post to delete.

    Returns:
        str: home.html or error.html if post not found.
    """
    if get_classification_level() < 2:
        return render_template('error.html', error_message=UNAUTHORIZED_ERROR_MSG,
                               classification_level=get_classification_level())

    post_to_delete = db.session.get(Post, post_id)
    if post_to_delete:
        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        return render_template('error.html', error_message=UNREACHABLE_ERROR_MSG,
                               classification_level=get_classification_level())

@app.route("/comment/<int:post_id>", methods=['GET', 'POST'])
def comment_post(post_id):
    # Cannot enter the editing route if not user and above
    if get_classification_level() < 1:
        return render_template('error.html', error_message=UNAUTHORIZED_ERROR_MSG,
                               classification_level=get_classification_level())

    # Getting post by id
    post_to_comment = db.session.get(Post, post_id)

    if post_to_comment:
        form = CommentForm()
        if form.validate_on_submit():
            new_comment = Comment(comment_user=current_user,
                                  parent_post=post_to_comment,
                                  body=form.comment.data,
                                  approved=False)
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('show_post', post_id=post_id))
        return render_template('comment.html', form=form, classification_level=get_classification_level())
    else:
        return render_template('error.html', error_message=UNREACHABLE_ERROR_MSG,
                               classification_level=get_classification_level())

@app.route("/approve_comment/<int:comment_id>", methods=['GET'])
def approve_comment(comment_id):
    # Cannot enter the editing route if not admin
    if get_classification_level() < 2:
        return render_template('error.html', error_message=UNAUTHORIZED_ERROR_MSG,
                               classification_level=get_classification_level())

    # Getting comment by id
    comment_to_approve = db.session.get(Comment, comment_id)

    if comment_to_approve:
        comment_to_approve.approved = True
        db.session.commit()
        return redirect(url_for('show_post', post_id=comment_to_approve.post_id))
    else:
        return render_template('error.html', error_message=UNREACHABLE_ERROR_MSG,
                               classification_level=get_classification_level())

@app.route("/delete_comment/<int:comment_id>", methods=['GET'])
def delete_comment(comment_id):
    # Cannot enter the editing route if not admin
    if get_classification_level() < 2:
        return render_template('error.html', error_message=UNAUTHORIZED_ERROR_MSG,
                               classification_level=get_classification_level())

    # Getting comment by id
    comment_to_delete = db.session.get(Comment, comment_id)

    if comment_to_delete:
        # Getting post id before deleting
        temp_post_id = comment_to_delete.post_id

        db.session.delete(comment_to_delete)
        db.session.commit()
        return redirect(url_for('show_post', post_id=temp_post_id))
    else:
        return render_template('error.html', error_message=UNREACHABLE_ERROR_MSG,
                               classification_level=get_classification_level())

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask app in debug mode
