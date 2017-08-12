from flask import Flask, redirect, url_for, render_template, flash, session, request
from flask_user import current_user
from flask_login import login_user, logout_user, UserMixin
from wtforms import StringField, PasswordField, validators, Form
from flask_bootstrap import Bootstrap
from db import *
from passlib.hash import sha256_crypt
import datetime

app = Flask(__name__)
Bootstrap(app)
app.secret_key = ''

class EmailForm(Form):
    email = StringField('Email', [validators.required(),
                                  validators.email(),
                                  validators.length(min=5, max=200)])

class LoginForm(Form):
    login = StringField('Login', [validators.required()])
    password = PasswordField('Password', [validators.required()])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm(request.form)
    if request.method == 'POST' and form.validate():
        emails = dbquery("SELECT * FROM emails WHERE email='{}'".format(form.email.data))
        if len(emails) > 0:
            flash('Вы уже подписаны. Спасибо за рвение.', 'warning')
        else:
            dbexecute("INSERT INTO emails(email) VALUES('{}')".format(form.email.data))
            with open('emails.log', 'a') as f:
                f.write('{}: {}'.format(datetime.datetime.now(), form.email.data))
            flash('Теперь вы подписаны. Мы уведомим вас, когда сервис запустится.', 'success')
    return render_template('index.html', form=form)


@app.route('/datamafaka', methods=['GET', 'POST'])
def data():
    if 'logged_in' in session:
        emails = dbquery("SELECT * FROM emails")
        return render_template('data.html', emails=emails)
    else:
        form = LoginForm(request.form)
        if request.method == 'POST' and form.validate():
            users = dbquery("SELECT * FROM users WHERE login='{}' LIMIT 1".format(form.login.data))
            if len(users) == 0:
                flash('Wrong login or password.', 'danger')
            elif not sha256_crypt.verify(form.password.data, users[0]['password']):
                flash('Wrong login or password.', 'danger')
            else:
                session['logged_in'] = True
                session['login'] = users[0]['login']
                return redirect(url_for('data'))
        return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.clear()
    return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
