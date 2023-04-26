from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, URL, ValidationError



class RegistrationForm(FlaskForm):
    name = StringField('Username',
                       validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8, max=20),
                                         ])
    confirm_password = PasswordField('confirm_password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    email = StringField(label='Email',
                        validators=[DataRequired(), Email(), Length(min=2, max=30)])
    password = PasswordField(label='Password',
                             validators=[DataRequired(), Length(min=2, max=30)])
    submit = SubmitField('Sign In')


# Creating the blog posting form class

class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    # Notice body's StringField changed to CKEditorField
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


# Creating a comment form

class CommentForm(FlaskForm):
    comment_text = CKEditorField("", validators=[DataRequired()])
    submit = SubmitField("Submit Comment")


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send')


# Creating a Search form
class SearchForm(FlaskForm):
    searched = StringField("Searched",
                           validators=[DataRequired(), Email(), Length(min=2, max=30)])
    submit = SubmitField('Sign In')
