# Flask Personal Blog Website – v.2 🖍️

## Overview

An enhanced Flask-based personal blog application that offers a richer and more robust user experience. In this version, we've replaced the static API approach with a fully integrated database using SQLAlchemy, added user authentication with registration and login, enabled post commenting, and introduced a modern content editor with CKEditor. The project is modular, secure, and scalable—built with maintainability in mind.

## Features

* **Full Database Integration**: Uses [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) ORM for structured data storage, replacing the external API model.
* **User Authentication**: Register and log in securely using [Flask-Login](https://flask-login.readthedocs.io/en/latest/), with session management and access control.
* **Secure Password Hashing**: User passwords are encrypted using [Werkzeug's security module](https://werkzeug.palletsprojects.com/en/latest/utils/#module-werkzeug.security) before being stored.
* **Post Comments**: Authenticated users can comment on blog posts, enhancing engagement and interaction.
* **CKEditor Integration**: Add and format blog content using a professional WYSIWYG editor.
* **Admin Controls**: Restrict access to certain actions (e.g., post creation or deletion) to admin users only.
* **Modular Code Structure**: Organized into separate files such as `forms.py`, `constants.py`, and `models.py` for better scalability and maintenance.
* **Jinja Templating**: Uses [Jinja](https://jinja.palletsprojects.com/en/latest/) to render pages dynamically with user-specific data.
* **Contact Form**: Still includes a fully functional email contact form with input validation.
* **Environment Variables**: All sensitive data is stored securely in a `.env` file.

## How It Works

1. **Database Structure**:

   * A relational schema built with SQLAlchemy models defines Users, BlogPosts, and Comments.
   * Relationships between tables allow querying authors of posts, comments per post, and more.

2. **Authentication Flow**:

   * Users can register, log in, and securely manage sessions.
   * Passwords are hashed and salted before storage.
   * Certain routes are protected and only accessible to authenticated or admin users.

3. **Post Creation and Editing**:

   * Admins can create, edit, and delete blog posts.
   * [CKEditor](https://ckeditor.com/) allows for rich text editing when writing posts.

4. **Comments**:

   * Logged-in users can leave comments on posts.
   * Comments are associated with both the user and the post using foreign key relationships.

5. **Contact Form**:

   * Sends emails via SMTP with the user's message and contact information.

## Documentation

* [Flask](https://flask.palletsprojects.com/en/latest/)
* [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
* [Flask-WTF](https://flask-wtf.readthedocs.io/en/1.0.x/)
* [Flask-Bootstrap](https://pypi.org/project/Flask-Bootstrap/)
* [Flask-CKEditor](https://flask-ckeditor.readthedocs.io/en/latest/)
* [SQLAlchemy](https://docs.sqlalchemy.org/en/20/)
* [Werkzeug Security](https://werkzeug.palletsprojects.com/en/latest/utils/)
* [Jinja](https://jinja.palletsprojects.com/en/latest/)
* [python-dotenv](https://pypi.org/project/python-dotenv/)
* [smtplib](https://docs.python.org/3/library/smtplib.html)
* [EmailMessage](https://docs.python.org/3/library/email.message.html)
* [WTForms](https://wtforms.readthedocs.io/en/3.1.x/)
* [CKEditor](https://ckeditor.com/)
* [os](https://docs.python.org/3/library/os.html)
* [datetime](https://docs.python.org/3/library/datetime.html)
