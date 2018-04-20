__author__ = "Francisco Gallardo"
# University of Michigan School of Information
# SI 364 - Building Interactive Applications

# Import statements
import os
from flask import Flask, render_template, session, redirect, request, url_for, flash
import datetime
import json
import requests
import string

#### Importing .py file containing my Search functions ####
from practice_api import search_by_name, search_by_flavor, search_by_effect, search_strain_effects, search_strain_flavors, API_KEY

from flask_script import Manager, Shell
# Imports needed for additional stuff for login
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, PasswordField, BooleanField, SelectMultipleField, ValidationError, RadioField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms.fields.html5 import EmailField

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand

# Imports for login management
from flask_login import LoginManager, login_required, logout_user, login_user, UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash
# login_required - checks if someone is logged in and if they are not logged in, it redirects user to appropiate page & if the user i logged in, then it shows them the database
# UserMixin takes the responsibility of setting up the user object to extract username, id, etcself.
# generate_password_hash & check_password_hash are used to encrypt the password and other login credentials to make sure that no one can hack into the system and whatnot
# password_hash will be different among different sites even if you use the same password across multiple sites
# Configure base directory of app
basedir = os.path.abspath(os.path.dirname(__file__))

# Application configurations
app = Flask(__name__)
app.debug = True
app.use_reloader = True
app.static_folder = 'static'
app.config['SECRET_KEY'] = 'hardtoguessstring'
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL') or "postgresql://localhost/FRGAsi364final"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['HEROKU_ON'] = os.environ.get('HEROKU')

# App addition setups
manager = Manager(app)
db = SQLAlchemy(app) # For database use
migrate = Migrate(app, db) # For database use/updating
manager.add_command('db', MigrateCommand)

# Login configurations setup
login_manager = LoginManager()
login_manager.session_protection = 'strong' # might make the password stronger, not sure yet
login_manager.login_view = 'login'
login_manager.init_app(app) # set up login manager

## Set up Shell context so it's easy to use the shell to debug
# Define function
def make_shell_context():
    return dict(app=app, db=db, User=User)

# Add function use to manager
manager.add_command("shell", Shell(make_context=make_shell_context))


# Models

# Many to Many Relationships
 # Association tables 
strains_tried = db.Table('user_saved_list',db.Column('strain_id',db.Integer, db.ForeignKey('strains.id')),
				db.Column('list_id',db.Integer, db.ForeignKey('user_lists.id'))) # Many to many, strains to users

strain_flavors = db.Table('allflavors',db.Column('strain_id',db.Integer, db.ForeignKey('strains.id')),
				db.Column('flavor_id',db.Integer, db.ForeignKey('flavors.id'))) # Many to many, strains to users

strain_effects = db.Table('alleffects', db.Column('strain_id', db.Integer, db.ForeignKey('strains.id')),
				db.Column('effect_id', db.Integer, db.ForeignKey('effects.id')))

search_strains = db.Table('search_results', db.Column('strain_id', db.Integer, db.ForeignKey('strains.id')),
				db.Column('search_term', db.Integer, db.ForeignKey('searches.id')))

## User Models
# Special model for users to log in
class User(UserMixin, db.Model): # UserMixin is what makes a user object, always need to inherit from UserMixin
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128)) # password hashes are always long so that is why we have 128 characters long 
    strain_lists = db.relationship('AlreadyTried', backref = 'collections')

    @property
    def password(self): # if you print out someone's password, you will ge this error
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password): # sets the password
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password): # verifies that user entered same password at log in and registration
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
    	return "Email: %s | ID: %d" % (self.email, self.id)

# Flavor Model
class Flavors(db.Model):
	__tablename__ = 'flavors'
	id = db.Column(db.Integer, primary_key = True)
	flavor = db.Column(db.String(128), unique = True)

	def __repr__(self):
		return "ID: %d | Flavor: %s" % (self.id, self.flavor)

# Effect Model
class Effects(db.Model):
	__tablename__ = 'effects'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(128), unique = True)
	effect_type = db.Column(db.String(128))

	def __repr__(self):
		return "%s Effect: %s" % (self.name, self.effect_type)

# Strain Model
class Strain(db.Model):
	__tablename__ = 'strains'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(80), unique = True)
	description = db.Column(db.Text)
	race = db.Column(db.String(64))
	strain_id = db.Column(db.Integer)
	ranking = db.Column(db.Integer)

	flavors = db.relationship('Flavors', secondary = strain_flavors, backref = db.backref('strains', lazy = 'dynamic'), lazy = 'dynamic')
	effects = db.relationship('Effects', secondary = strain_effects, backref = db.backref('strains', lazy = 'dynamic'), lazy = 'dynamic')

	def __repr__(self):
		return "Strain: %s | Strain ID: %d | ID: %d" % (self.name, self.strain_id, self.id)


class PastSearches(db.Model):
	__tablename__ = 'searches'
	id = db.Column(db.Integer, primary_key = True)
	term = db.Column(db.String(64))
	q_type = db.Column(db.String(64))
	created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow())

	results = db.relationship('Strain', secondary = search_strains, backref = db.backref('searches', lazy = 'dynamic'), lazy = 'dynamic')

	def __repr__(self):
		return "ID: %d | Term: %s | Type: %s | created_at: %d" % (self.id, self.term, self.q_type, self.created_at)

class AlreadyTried(db.Model):
	__tablename__ = 'user_lists'
	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
	type_of_list = db.Column(db.String(28))

	strains = db.relationship('Strain',secondary = strains_tried, backref = db.backref('user_lists', lazy = 'dynamic'), lazy = 'dynamic')

	def __repr__(self):
		return "ID: %d | User_id: %d | Type: %s" % (self.id, self.user_id, self.type_of_list)
	



####### CUSTOM VALIDATOR #########
def search_validator(form, field):
	for symbol in string.punctuation:
		if symbol in field.data:
			raise ValidationError('Search term must not include %s' % string.punctuation)


########## FLASK FORMS ###########
class enterSearchQuery(FlaskForm):
	options = RadioField('Search for medical marijuana strain by:', choices= [('name', 'name'), ('flavor','flavor'),('effect', 'effect')], validators = [Required()])
	term = StringField('Enter the search query', validators = [Required(), search_validator])
	submit = SubmitField('Search')

class Register(FlaskForm):
	email = EmailField('Enter your email', validators = [Email('Email was not valid'), Required()])
	email2 = EmailField('Please renter your email', validators = [Email('Emails must match'), Required(), EqualTo('email',message="Emails must match")])
	password = PasswordField('Please enter your password', validators = [Required()])
	password2 = PasswordField('Please renter your password', validators = [Required(), EqualTo('password',message="Passwords must match")])
	submit = SubmitField('Register')

	#Additional checking methods for the form
	def validate_email(self,field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email already registered.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class AddToMyList(FlaskForm):
	list_to_save = RadioField('Add to wish list or already tried list', choices = [('Wishlist', 'Wishlist'), ('Tried', 'Tried')], validators = [Required()])
	options = SelectMultipleField('Add strains to your saved list', choices = [], validators = [Required()])
	submit = SubmitField('Add to list')


class RateStrain(FlaskForm):
	options = RadioField('Please rate the strain',
						choices = [("1", "1"), ("2","2"),("3","3"),("4","4"),("5","5")], validators = [Required()])
	submit = SubmitField('Submit Ranking')

class DeleteForm(FlaskForm):
	submit = SubmitField('Delete')

############# GET OR CREATE FUNCTIONS #################
def get_or_create_effect(effect_type, name):
	effect = Effects.query.filter_by(name = name, effect_type = effect_type).first()
	if effect:
		return effect
	else:
		effect = Effects(name = name, effect_type = effect_type)
		db.session.add(effect)
		db.session.commit()
		return effect

def get_or_create_flavor(flavor_name):
	flavor = Flavors.query.filter_by(flavor = flavor_name).first()
	if flavor:
		return flavor
	else:
		flavor = Flavors(flavor = flavor_name)
		db.session.add(flavor)
		db.session.commit()
		return flavor

def get_or_create_strain(name, id, race, description, flavors, pos, neg, med):
	strain = Strain.query.filter_by(name = name, strain_id = id).first()
	if strain:
		return strain
	else:
		strain = Strain(name = name, description = description, strain_id = id, race = race)

		if pos:
			ps = [get_or_create_effect("Positive", item) for item in pos]
			for item in ps:
				strain.effects.append(item)

		if med:
			md = [get_or_create_effect("Medical", item) for item in med]
			for item in md:
				strain.effects.append(item)

		if neg:
			ng = [get_or_create_effect('Negative', item) for item in neg]
			for item in ng:
				print(item)
				strain.effects.append(item)
		if flavors:
			fl = [get_or_create_flavor(item) for item in flavors]
			for item in fl:
				strain.flavors.append(item)

		db.session.add(strain)
		db.session.commit()
		return strain
def get_strain_by_id(inp):
	return Strain.query.filter_by(id = int(inp)).first()

def get_or_create_search(s_type, user_search):

	search = PastSearches.query.filter_by(term = user_search, q_type = s_type).first()
	if search:
		return search

	search = PastSearches(term = user_search, q_type = s_type)
	if s_type == 'name':
		results = search_by_name(user_search)

	elif s_type == 'flavor':
		results = search_by_flavor(user_search)

	elif s_type == 'effect':
		results = search_by_effect(user_search)

	if results:
		for key in results:
			strain = get_or_create_strain(key, 
				results[key][0], 
				results[key][1], 
				results[key][2], 
				results[key][3],
				results[key][4],
				results[key][5],
				results[key][6]
				)
			search.results.append(strain)
	else:
		strain = None
	
	db.session.add(search)
	db.session.commit()
	return search 



## DB load function
## Necessary for behind the scenes login manager that comes with flask_login capabilities! Won't run without this.
@login_manager.user_loader # ensure that use rhtat is logged in is stored in User model
def load_user(user_id):
    return User.query.get(int(user_id)) # returns User object or None



@app.route('/',methods=["GET","POST"])
@login_required
def index():
	form = enterSearchQuery()
	if form.validate_on_submit():
		user_choice = form.options.data
		query = form.term.data
		results = get_or_create_search(user_choice, query)
		return redirect(url_for('search_results', type = user_choice, search = query))
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return render_template('index.html', form = form)

	pass
	# Should display an HTML FlaskForm where the user gets to search for different marijuana strains
	# The user is able to search by the name of the strain, effects or flavors
	# Once the form is validated, it will call the get_strains helper function which will make a request to an API to find the strains that match that the user is searching for
	# If the form is not vaidated, then it will display the empty form
	

@app.route('/<type>/query/<search>', methods = ['GET', 'POST'])
@login_required
def search_results(type,search):
	form = AddToMyList()
	search = PastSearches.query.filter_by(term = search, q_type = type).first()
	strain_names = [(str(s.id),s.name) for s in search.results.all()]
	form.options.choices = strain_names
	items = search.results.all()

	strains = [s.effects.all() for s in items]
	st = {}
	for strain in items:
		st[strain.name] = {}
		pos = []
		ng = []
		md = []
		for e in strain.effects.all():
			if e.effect_type == 'Positive':
				pos.append(e.name)
			if e.effect_type == 'Negative':
				ng.append(e.name)
			if e.effect_type == 'Medical':
				md.append(e.name)
		st[strain.name]['pos'] = pos
		st[strain.name]['ng'] = ng
		st[strain.name]['md'] = md

	if form.validate_on_submit():
		type_list = form.list_to_save.data
		options = form.options.data
		
		strains = [get_strain_by_id(item) for item in options]
		
		u_list = AlreadyTried.query.filter_by(user_id = current_user.id, type_of_list = type_list).first()

		if not u_list:
			u_list = AlreadyTried(user_id = current_user.id, type_of_list = type_list)
			u_list.strains = (strains)
			db.session.add(u_list)
			db.session.commit()
		if u_list:
			
			u_list.strains.extend(strains)
			db.session.commit()
			flash('Added strain to your %s list' % type_list)
		
		return redirect(url_for('collection', type_list = type_list))
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return render_template('display_results.html', results = search.results.all(), form = form, strains = st)
	# This plage will receive two variables from the index page that the user entered through the form if it was validated.
	# Then it will call the search_strains helper function which will make a request to an API to find the strains that match that the user is searching for
	# This function will take in the two arguments that were passed from the index page
	# Once the API request is processed, the page will render an HTML template with the results of the search and the users have the ablity to save the strains to their saved strains list
	# If the form is not validated, then the page will display the results of the search query

@app.route('/collections', methods = ['GET', 'POST'])
@login_required
def see_collections():
	user = current_user
	user_collection = User.query.filter_by(id = user.id).first().strain_lists
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return render_template('collections.html', collections = user_collection)


@app.route('/collection/<type_list>', methods = ['GET', 'POST'])
@login_required
def collection(type_list):
	
	form = DeleteForm()


	user_lists = AlreadyTried.query.filter_by(user_id = current_user.id, type_of_list = type_list).first()
	lists = user_lists.strains.all()
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)

	return render_template('collection.html', list= type_list, lists = lists, form = form)
	
	# This page will display links to all of the strains that the user decided to save to their desired list of Canabis Strains


@app.route('/collection/<saved_list>/<name>', methods = ['GET', 'POST'])
@login_required
def see_strain(saved_list,name):
	
	obj = Strain.query.filter_by(name = name).first()
	list_type = None
	f = obj.flavors.all()
	e = obj.effects.all()
	pos = list(filter(lambda x:x.effect_type == 'Positive', e))
	neg = list(filter(lambda x:x.effect_type == 'Negative', e))
	md = list(filter(lambda x:x.effect_type == 'Medical', e))

	form = RateStrain()
	
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return render_template('view_strain.html', strain = obj, pos = pos, neg = neg, md = md, form = form)
	# This page will display the details of the specific strain the user clicked on from the /savedstrains route
	# The page will also render a template that allows the user to delete the saved strain if they would like to
	# If the template is validated, the user will be redirected to the /savedstrains route
	# If the form is not validated, then the page will reload and display the Cannabis strain's information
@app.route('/strain/<name>/update/', methods = ['GET', 'POST'])
@login_required
def update_strain_rating(name):
	form = RateStrain(request.form)
	if request.method == 'GET':
		data =request.args.get('options')
		strain = Strain.query.filter_by(name = name).first()
		strain.ranking = data
		db.session.commit()
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return redirect(url_for('see_collections'))

@app.route('/delete/<name>', methods = ['GET', 'POST'])
@login_required
def delete_strain(name):
	if request.method == 'GET':
		strain = Strain.query.filter_by(name = name).first()
		if strain:

			db.session.delete(strain)
			db.session.commit()
		errors = [v for v in form.errors.values()]
		if len(errors) > 0:
			string_errors = " | ".join([str(er) for er in errors])
			flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
		return redirect(url_for('see_collections'))


@app.route('/logout')
@login_required
def logout():
	logout_user()
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return redirect(url_for('login'))
	
	# this route will logout the current user and redirect the user back to the /index route


@app.route('/login', methods = ['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(request.args.get('next') or url_for('index'))
		flash('Invalid username or password.')
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return render_template('login.html', form = form)
	# This page will render an HTML template that will allow the user to login with their email and password
	# If the form is validated and the user has already registered for an account to use this app, then they will be redirected to the /index page
	# if the form is validated but the entered credentials are not in the User model, then it page will reload with an error message and display the empty log in form
	# If the form is not validated, then the page will be refreshed and display the empty form

@app.route('/register',methods=["GET","POST"])
def register():
	form = Register()
	if form.validate_on_submit():
		email = form.email.data
		password = form.password.data
		user = User(email = email, password = password)
		db.session.add(user)
		db.session.commit()
		flash('You can now log in!')
		return redirect(url_for('login')) # redirect to log in page so that they can sign in
	errors = [v for v in form.errors.values()]
	if len(errors) > 0:
		string_errors = " | ".join([str(er) for er in errors])
		flash("!!!! ERRORS IN FORM SUBMISSION - " + string_errors)
	return render_template('register.html', form = form)
	# This page will render and HTML template that will allow the user to register for an account to use this application
	# If the template is validated, then it will call the get_or_create_user helper function that will allow the user to register for an ccount
	# Then the user will be redirected to the /login route where they will need to sign in to use the account
	# If the form is not validated, then the page will reload and display an empty form



if __name__ == '__main__':
    db.create_all()
    manager.run()