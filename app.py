from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField, StringField, PasswordField
from wtforms.validators import NumberRange, DataRequired, Email, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class CountryStateForm(FlaskForm):
    country = SelectField('Country', choices=[('USA', 'USA'), ('Canada', 'Canada')], validators=[DataRequired()])
    state = SelectField('State', choices=[('New York', 'New York'), ('California', 'California')], validators=[DataRequired()])
    submit = SubmitField('Submit')

class MultiplicationForm(FlaskForm):
    number1 = IntegerField('Number 1', validators=[NumberRange(min=0)])
    number2 = IntegerField('Number 2', validators=[NumberRange(min=0)])
    submit = SubmitField('Multiply')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = LoginForm()
    if request.method == 'POST' and form_login.validate_on_submit():
        username = form_login.username.data
        password = form_login.password.data
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = user.username
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form_login)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form_register = RegisterForm()
    if request.method == 'POST' and form_register.validate_on_submit():
        username = form_register.username.data
        email = form_register.email.data
        password = form_register.password.data
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form_register)

@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('login'))

@app.route('/country_state_selection', methods=['GET', 'POST'])
def country_state_selection():
    form = CountryStateForm()
    if form.validate_on_submit():
        country = form.country.data
        state = form.state.data
        return redirect(url_for('country_state_result', country=country, state=state))
    return render_template('country_state_selection.html', form=form)


@app.route('/country_state_result/<country>/<state>')
def country_state_result(country, state):
    return render_template('country_state_result.html', country=country, state=state)


@app.route('/multiplication_page', methods=['GET', 'POST'])
def multiplication_page():
    form = MultiplicationForm()
    if form.validate_on_submit():
        result = form.number1.data * form.number2.data
        return redirect(url_for('multiplication_result', result=result))
    return render_template('multiplication_page.html', form=form)

@app.route('/multiplication_result/<int:result>')
def multiplication_result(result):
    return render_template('multiplication_result.html', result=result)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def create_tables():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    create_tables()
    app.run(debug=True)
