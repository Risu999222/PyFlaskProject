import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, SelectField, StringField, PasswordField, FloatField
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
    country = SelectField('Country', validators=[DataRequired()])
    state = SelectField('State', validators=[DataRequired()])
    submit = SubmitField('Submit')

class MultiplicationForm(FlaskForm):
    number1 = FloatField('Number 1', validators=[NumberRange(min=-1000000, max=1000000)])
    number2 = FloatField('Number 2', validators=[NumberRange(min=-1000000, max=1000000)])
    submit = SubmitField('Multiply')

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
    response = requests.get('https://countriesnow.space/api/v0.1/countries/states')
    if response.status_code == 200:
        data = response.json()
        countries = [(country['name'], country['name']) for country in data['data']]
        form.country.choices = countries
    if form.validate_on_submit():
        country = form.country.data
        state = form.state.data
        return redirect(url_for('country_state_result', country=country, state=state))
    return render_template('country_state_selection.html', form=form)

@app.route('/get_states', methods=['POST'])
def get_states():
    country = request.form.get('country')
    response = requests.get('https://countriesnow.space/api/v0.1/countries/states')
    if response.status_code == 200:
        data = response.json()
        states_data = {}
        for country_data in data['data']:
            if country_data['name'] == country:
                states_data['states'] = country_data['states']
                break
        else:
            return jsonify({'error': True, 'msg': 'Country not found'})
        return jsonify({'error': False, 'msg': 'States retrieved', 'data': states_data})
    else:
        return jsonify({'error': True, 'msg': 'Failed to retrieve states'})

@app.route('/country_state_result', methods=['POST'])
def country_state_result():
    country = request.form.get('country')
    state = request.form.get('state')
    return render_template('country_state_result.html', country=country, state=state)


@app.route('/multiplication_page', methods=['GET', 'POST'])
def multiplication_page():
    form = MultiplicationForm()
    if form.validate_on_submit():
        result = form.number1.data * form.number2.data
        return redirect(url_for('multiplication_result', result=result))
    return render_template('multiplication_page.html', form=form)

@app.route('/multiplication_result/<result>')
def multiplication_result(result):
    result_float = float(result)
    result_formatted = str(result_float).rstrip('0').rstrip('.') if '.' in result else result
    return render_template('multiplication_result.html', result=result_formatted)

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
