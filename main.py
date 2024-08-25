from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
import re
from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_bcrypt import Bcrypt

# Application Setup
def create_app():
    app = Flask(__name__)
    app.secret_key = 'securekey'
    setup_extensions(app)
    setup_database(app)
    return app

def setup_extensions(app):
    global bcrypt_tool
    bcrypt_tool = Bcrypt(app)

def setup_database(app):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insurance_data.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    global database
    database = SQLAlchemy(app)

# Models
class Customer(database.Model):
    customer_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    user_name = database.Column(database.String(80), unique=True, nullable=False)
    user_password = database.Column(database.String(120), nullable=False)
    annual_income = database.Column(database.Float, nullable=False)
    user_age = database.Column(database.Integer, nullable=False)
    occupation = database.Column(database.String(80), nullable=True)
    education = database.Column(database.String(80), nullable=True)
    marital_status = database.Column(database.String(80), nullable=True)
    ssn = database.Column(database.String(11), unique=True, nullable=False)
    height_cm = database.Column(database.Float)
    weight_kg = database.Column(database.Float)
    waist_size = database.Column(database.Float)
    hip_size = database.Column(database.Float)
    systolic_bp = database.Column(database.Integer)
    diastolic_bp = database.Column(database.Integer)
    heart_rate = database.Column(database.Integer)
    cholesterol_level = database.Column(database.Float)
    blood_glucose = database.Column(database.Float)
    hdl_level = database.Column(database.Float)
    ldl_level = database.Column(database.Float)
    triglycerides_level = database.Column(database.Float)
    uric_acid_level = database.Column(database.Float)
    chronic_illness = database.Column(database.Boolean, default=False)

    def set_user_password(self, plain_password):
        """Hash and set the user's password"""
        if self.is_valid_password(plain_password):
            self.user_password = bcrypt_tool.generate_password_hash(plain_password).decode('utf-8')
        else:
            raise ValueError("Password must be between 6 and 26 characters long.")
    
    def is_valid_password(self, plain_password):
        """Check if the password is valid"""
        return 6 <= len(plain_password) <= 26
    
    def verify_password(self, plain_password):
        """Verify the user's password"""
        return bcrypt_tool.check_password_hash(self.user_password, plain_password)


class InsurancePlan(database.Model):
    plan_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    plan_name = database.Column(database.String(120), unique=True, nullable=False)
    plan_cost = database.Column(database.Float, nullable=False)

class InsuranceQuote(database.Model):
    quote_id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    customer_id = database.Column(database.Integer, database.ForeignKey('customer.customer_id'), nullable=False)
    plan_id = database.Column(database.Integer, database.ForeignKey('insurance_plan.plan_id'), nullable=False)
    quote_amount = database.Column(database.Float, nullable=False)
    customer_income = database.Column(database.Float, nullable=False)
    customer_age = database.Column(database.Integer, nullable=False)
    height_cm = database.Column(database.Float)
    weight_kg = database.Column(database.Float)
    waist_size = database.Column(database.Float)
    hip_size = database.Column(database.Float)
    systolic_bp = database.Column(database.Integer)
    diastolic_bp = database.Column(database.Integer)
    heart_rate = database.Column(database.Integer)
    cholesterol_level = database.Column(database.Float)
    blood_glucose = database.Column(database.Float)
    hdl_level = database.Column(database.Float)
    ldl_level = database.Column(database.Float)
    triglycerides_level = database.Column(database.Float)
    uric_acid_level = database.Column(database.Float)
    chronic_illness = database.Column(database.Boolean, default=False)

# Forms
class UserLoginForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

# Machine Learning Model Handler
class QuoteModelHandler:
    def __init__(self, quotes, model_file="insurance_model.pkl"):
        self.model_file = model_file
        self.model = self.load_or_train_model(quotes)

    def load_or_train_model(self, quotes):
        try:
            model = joblib.load(self.model_file)
            return model
        except FileNotFoundError:
            return self.train_model(quotes)

    def train_model(self, quotes):
        if not quotes:
            return None
        age_data = []
        income_data = []
        quote_amounts = []
        
        for quote in quotes:
            age_data.append(quote.customer_age)
            income_data.append(quote.customer_income)
            quote_amounts.append(quote.quote_amount)

        data_frame = pd.DataFrame({
            'age': age_data,
            'income': income_data,
            'quote_amount': quote_amounts
        })

        features = data_frame[['age', 'income']]
        target = data_frame['quote_amount']

        model = RandomForestRegressor()
        model.fit(features, target)
        joblib.dump(model, self.model_file)
        return model

    def predict_quote(self, customer_data):
        input_df = pd.DataFrame([customer_data])
        quote_prediction = self.model.predict(input_df[['age', 'income']])[0]
        return quote_prediction

# Routes for Admin Actions
def admin_dashboard():
    is_admin = True

    if is_admin:
        if request.method == 'POST':
            action_type = request.form.get('action')
            handle_admin_actions(action_type)
        all_customers = Customer.query.all()
        all_plans = InsurancePlan.query.all()
        return render_template('admin_dashboard.html', customers=all_customers, plans=all_plans)
    else:
        return redirect(url_for('login'))

def handle_admin_actions(action_type):
    if action_type == 'modify':
        modify_customer_info()
    elif action_type == 'delete':
        delete_customer()
    elif action_type == 'modify_plan':
        modify_plan_info()
    elif action_type == 'delete_plan':
        delete_plan()

def modify_customer_info():
    customer_id = request.form.get('customer_id')
    updated_age = request.form.get('new_age')
    updated_income = request.form.get('new_income')
    customer = Customer.query.get(customer_id)
    if customer:
        if updated_age:
            customer.user_age = updated_age
        if updated_income:
            customer.annual_income = updated_income
        database.session.commit()
        flash('Customer information updated successfully.')

def delete_customer():
    customer_id = request.form.get('customer_id')
    customer = Customer.query.get(customer_id)
    if customer:
        database.session.delete(customer)
        database.session.commit()
        flash('Customer information deleted successfully.')

def modify_plan_info():
    plan_id = request.form.get('plan_id')
    updated_name = request.form.get('new_name')
    updated_price = request.form.get('new_price')
    insurance_plan = InsurancePlan.query.get(plan_id)
    if insurance_plan:
        if updated_name:
            insurance_plan.plan_name = updated_name
        if updated_price:
            insurance_plan.plan_cost = updated_price
        database.session.commit()

def delete_plan():
    plan_id = request.form.get('plan_id')
    insurance_plan = InsurancePlan.query.get(plan_id)
    if insurance_plan:
        database.session.delete(insurance_plan)
        database.session.commit()
        flash('Insurance plan deleted successfully.')

# Routes for User Actions
def home_redirect():
    return redirect(url_for('login'))

def login():
    login_error = None
    if request.method == 'POST':
        username = request.form['username']
        plain_password = request.form['password']
        customer = Customer.query.filter_by(user_name=username).first()

        if customer and bcrypt_tool.check_password_hash(customer.user_password, plain_password):
            flash('Login successful', 'success')
            session['customer_id'] = customer.customer_id
            return redirect(url_for('admin_dashboard')) if username == 'admin' else redirect(url_for('user_dashboard'))
        else:
            login_error = 'Login failed. Please check your username and password.'

    return render_template('login.html', error_message=login_error)

def user_dashboard():
    return render_template('user_dashboard.html')

def user_registration_form():
    return render_template('user_registration.html')

def register_user():
    if request.method == 'POST':
        username = request.form['username']
        income = request.form['income']
        age = request.form['age']
        plain_password = request.form['password']
        create_new_user(username, income, age, plain_password)
        return redirect(url_for('user_dashboard'))

def create_new_user(username, income, age, plain_password):
    occupation = request.form.get('occupation')
    education = request.form.get('education')
    marital_status = request.form.get('marital_status')
    ssn = request.form.get('ssn')
    height = float(request.form.get('height', 0))
    weight = float(request.form.get('weight', 0))
    waist_size = float(request.form.get('waist_size', 0))
    hip_size = float(request.form.get('hip_size', 0))
    systolic_bp = int(request.form.get('systolic_bp', 0))
    diastolic_bp = int(request.form.get('diastolic_bp', 0))
    heart_rate = int(request.form.get('heart_rate', 0))
    cholesterol_level = float(request.form.get('cholesterol_level', 0))
    blood_glucose = float(request.form.get('blood_glucose', 0))
    hdl_level = float(request.form.get('hdl_level', 0))
    ldl_level = float(request.form.get('ldl_level', 0))
    triglycerides_level = float(request.form.get('triglycerides_level', 0))
    uric_acid_level = float(request.form.get('uric_acid_level', 0))
    chronic_illness = request.form.get('chronic_illness') == 'on'
    
    new_user = Customer(
        user_name=username,
        annual_income=income,
        user_age=age,
        occupation=occupation,
        education=education,
        marital_status=marital_status,
        ssn=ssn,
        height_cm=height,
        weight_kg=weight,
        waist_size=waist_size,
        hip_size=hip_size,
        systolic_bp=systolic_bp,
        diastolic_bp=diastolic_bp,
        heart_rate=heart_rate,
        cholesterol_level=cholesterol_level,
        blood_glucose=blood_glucose,
        hdl_level=hdl_level,
        ldl_level=ldl_level,
        triglycerides_level=triglycerides_level,
        uric_acid_level=uric_acid_level,
        chronic_illness=chronic_illness
    )
    
    new_user.set_user_password(plain_password)
    database.session.add(new_user)
    database.session.commit()
    
    session['customer_id'] = new_user.customer_id
    flash('Registration successful!')

# Routes for Quote Generation
def generate_quote():
    user_id = request.form.get('user_id')
    plan_id = request.form.get('plan_id')

    customer = Customer.query.get(user_id)
    user_data = get_user_data(customer)

    quote_amount = quote_model.predict_quote(user_data)
    
    new_quote = InsuranceQuote(
        customer_id=user_id,
        plan_id=plan_id,
        quote_amount=quote_amount,
        customer_income=customer.annual_income,
        customer_age=customer.user_age,
        height_cm=customer.height_cm,
        weight_kg=customer.weight_kg,
        waist_size=customer.waist_size,
        hip_size=customer.hip_size,
        systolic_bp=customer.systolic_bp,
        diastolic_bp=customer.diastolic_bp,
        heart_rate=customer.heart_rate,
        cholesterol_level=customer.cholesterol_level,
        blood_glucose=customer.blood_glucose,
        hdl_level=customer.hdl_level,
        ldl_level=customer.ldl_level,
        triglycerides_level=customer.triglycerides_level,
        uric_acid_level=customer.uric_acid_level,
        chronic_illness=customer.chronic_illness
    )
    
    database.session.add(new_quote)
    database.session.commit()

    return redirect(url_for('user_dashboard'))

def get_user_data(customer):
    return {
        'age': customer.user_age,
        'income': customer.annual_income,
        'height': customer.height_cm,
        'weight': customer.weight_kg,
        'waist_circumference': customer.waist_size,
        'hip_circumference': customer.hip_size,
        'systolic_bp': customer.systolic_bp,
        'diastolic_bp': customer.diastolic_bp,
        'pulse': customer.heart_rate,
        'cholesterol': customer.cholesterol_level,
        'blood_sugar': customer.blood_glucose,
        'hdl': customer.hdl_level,
        'ldl': customer.ldl_level,
        'triglycerides': customer.triglycerides_level,
        'uric_acid': customer.uric_acid_level,
        'has_chronic_illness_history': customer.chronic_illness,
    }

# Application Initialization
application = create_app()

# Route Bindings
application.add_url_rule('/admin', view_func=admin_dashboard, methods=['GET', 'POST'])
application.add_url_rule('/', view_func=home_redirect)
application.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
application.add_url_rule('/user_dashboard', view_func=user_dashboard)
application.add_url_rule('/register_user', view_func=user_registration_form, methods=['GET'])
application.add_url_rule('/register_user', view_func=register_user, methods=['POST'])
application.add_url_rule('/generate_quote', view_func=generate_quote, methods=['POST'])

# Run the application
if __name__ == '__main__':
    with application.app_context():
        database.create_all()
        all_quotes = InsuranceQuote.query.all()
        quote_model = QuoteModelHandler(all_quotes)
        application.run(port=8000, debug=True)
