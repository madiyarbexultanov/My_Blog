import smtplib
from datetime import date
from functools import wraps
from flask import Flask, render_template, request, flash, redirect, url_for
from flask import abort
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin
from flask_login import login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from forms import ContactForm, SearchForm, CommentForm

app = Flask(__name__)
ckeditor = CKEditor(app)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'cf72645db1e120cf269c96f4d74c5e4f'

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuring Flask_login
login_manager = LoginManager()
login_manager.init_app(app)

gravatar = Gravatar(app, size=50, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)


# Create admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Create the User Table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

    # This will act like a List of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    posts = relationship("BlogPost", back_populates="author")

    # "comment_author" refers to the comment_author property in the Comment class.
    comments = relationship("Comment", back_populates="comment_author")


class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)

    # *******Add child relationship*******#
    # "users.id" The users refers to the tablename of the Users class.
    # "comments" refers to the comments property in the User class.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    # ***************Child Relationship*************#
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    text = db.Column(db.Text, nullable=False)


# Creating of Database for posts
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    # Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    # ***************Parent Relationship*************#
    comments = relationship("Comment", back_populates="parent_post")


# Create all the tables in the database
with app.app_context():
    db.create_all()

# @app.context_processor
# def base():
#     form = SearchForm()
#     return dict(form=form)


# @app.route('/search', methods =["POST"])
# def search():
#     form = SearchForm()
#     posts = BlogPost.query.all()
#     if form.validate_on_submit():
#         post_searched = form.searched.data
#         posts = posts.filter(BlogPost.body.like('%' + post_searched + '%'))
#         posts = posts.order_by(BlogPost.title).all()
#         return render_template("search.html", form=form, searched = post_searched, posts = posts)

@app.route('/')
def home_page():
    posts = BlogPost.query.all()
    return render_template('index.html', title="Home", all_posts=posts, current_user=current_user)


@app.route("/about")
def about_page():
    return render_template("about.html", title="About", current_user=current_user)


@app.route("/contact", methods=["GET", "POST"])
def contact_page():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        message = form.message.data
        full_message = f'"Subject: New Form Filled\n\n"Name: {name}\nMail: {email}\n\nMessage: {message}'
        my_email = "madiyarmakanov98@gmail.com"
        password = "ygcdctzjfbvtsqyv"
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs="bexultanovmadiyar@gmail.com", msg=full_message)
            return render_template("contact.html", form=form, current_user=current_user, title="Contact me")
    return render_template("contact.html", form=form, current_user=current_user, title="Contact me")



@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    comment_form = CommentForm()
    requested_post = BlogPost.query.get(post_id)
    if comment_form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to comment.")
            return redirect(url_for("login_page"))

        new_comment = Comment(
            text=comment_form.comment_text.data,
            comment_author=current_user,
            parent_post=requested_post
        )
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("post.html", post=requested_post, title=requested_post.title, current_user=current_user,
                           form=comment_form, gravatar=gravatar)


@app.route("/delete-comment/<int:post_id>/<int:comment_id>", methods=["GET", "POST"])
@admin_only
def delete_comment(post_id, comment_id):
    comment_to_delete = Comment.query.get(comment_id)
    db.session.delete(comment_to_delete)
    db.session.commit()
    return redirect(url_for('show_post', post_id=post_id))


from forms import CreatePostForm


@app.route('/new-post', methods=["GET", "POST"])
@admin_only
def new_post():
    post_form = CreatePostForm()
    if post_form.validate_on_submit():
        new_post = BlogPost(
            title=post_form.title.data,
            subtitle=post_form.subtitle.data,
            body=post_form.body.data,
            img_url=post_form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home_page"))
    return render_template("make-post.html", form=post_form, current_user=current_user)


@app.route('/edit-post/<post_id>', methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author.name,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route('/delete/<post_id>', methods=["GET", "POST"])
def delete_post(post_id):
    post = BlogPost.query.get(post_id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for('home_page'))


# Login and authorization part
from forms import RegistrationForm


# Register new users into the User database
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():

        # If user's email already exists
        if User.query.filter_by(email=form.email.data).first():
            # Send flash messsage
            flash("You've already signed up with that email, log in instead!")
            # Redirect to /login route.
            return redirect(url_for('login_page'))
        elif User.query.filter_by(name=form.name.data).first():
            flash("That username already exists")
            return redirect(url_for('register'))

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User()
        new_user.email = request.form['email']
        new_user.name = request.form['name']
        new_user.password = hash_and_salted_password
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for("home_page"))

    return render_template("register.html", form=form, title="Registration", current_user=current_user)


from forms import LoginForm


@app.route('/login', methods=["GET", "POST"])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()

        # Email doesn't exist
        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login_page'))
        # Password incorrect
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login_page'))
        else:
            login_user(user)
            return redirect(url_for('home_page'))

    return render_template("login.html", form=form, title="Login", current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home_page'))


if __name__ == "__main__":
    app.run(debug=True)
