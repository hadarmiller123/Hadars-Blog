from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length, Regexp, URL
from flask_ckeditor import CKEditorField

class ContactForm(FlaskForm):
    """ Form for users to send messages via the contact page """
    name = StringField(label='Name', validators=[DataRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Israel Israeli"})
    email = StringField(label='Email address', validators=[DataRequired(), Email()], render_kw={"placeholder": "Israel@israeli.com"})
    phone = StringField(label='Phone Number', validators=[DataRequired(), Regexp(regex=r'^05[0-5,8]\d{7}$', message="Phone number must be 9 or 10 digits")], render_kw={"placeholder": "05X-XXXXXXX"})
    message = TextAreaField(label='Message', validators=[DataRequired(), Length(min=5)], render_kw={"placeholder": "Write me a message :)"})
    submit = SubmitField('Send')

class BasePostForm(FlaskForm):
    """ Base form for blog posts containing post fields """
    title = StringField(label='Title', validators=[DataRequired(), Length(min=2, max=100)])
    subtitle = StringField(label='Subtitle', validators=[DataRequired(), Length(min=2, max=150)])
    img_url = StringField(label='Image URL', validators=[DataRequired(), URL()])
    author = StringField(label='Author', validators=[DataRequired(), Length(min=2, max=100),
                                                         Regexp(r'^[A-Za-z\s]+$',
                                                                    message="Author name could contain only letters and spaces")])
    body = CKEditorField(label='Body', validators=[DataRequired(), Length(min=5)])

class EditPostForm(BasePostForm):
    """ Form for editing an existing blog post """
    submit = SubmitField(label='Update Post')

class CreatePostForm(BasePostForm):
    """ Form for creating a new blog post """
    submit = SubmitField(label='Publish Post')

class RegisterForm(FlaskForm):
    """ Form for register new users """
    name = StringField(label='Name', validators=[DataRequired(), Length(min=2, max=50)], render_kw={"placeholder": "Israel Israeli"})
    email = StringField(label='Email address', validators=[DataRequired(), Email()], render_kw={"placeholder": "Israel@israeli.com"})
    password = PasswordField(label='Password', validators=[DataRequired()], render_kw={"placeholder": "Never share your password!"})
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    """ Form for login """
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label='Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class CommentForm(FlaskForm):
    """ Form for commenting """
    comment = CKEditorField(label='', validators=[DataRequired(), Length(min=5)], render_kw={'placeholder': 'Slam That Keyboard & Share Your Thoughts!'})
    submit = SubmitField('Send')
