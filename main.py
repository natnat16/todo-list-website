from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response, flash, abort
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from is_safe_url import is_safe_url
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from datetime import datetime, date, timedelta
from forms import SignUpForm, LoginForm, SettingsForm, ResetForm, ResetVerificationForm, CreateNewList, CreateNewItem, verification_questions
from numpy import unique
import os
# for local use of .env
# from dotenv import load_dotenv 
# load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('APP_SECRET_KEY')
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(weeks=1)
## change host when deploying
#host='http://127.0.0.1:5000/'
host='https://g-todo-list.herokuapp.com/'
host2='g-todo-list.herokuapp.com/'

######    Connect to Database    ######
## (DATABASE_URL online, sqlite will be used localy)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

login_manager = LoginManager(app)

######    Configure tables    ######
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))
    theme = db.Column(db.String(50), default='light')
    verifaction_question = db.Column(db.String(250))
    verifaction_answer = db.Column(db.String(50)) 
    user_lists = relationship('List', back_populates="parent_user", cascade="all, delete")     

class List(db.Model):
    __tablename__ = "lists"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_user = relationship('User', back_populates="user_lists")
    category = db.Column(db.String(50), default='General') 
    color = db.Column(db.String(50), default='orange')
    list_items = relationship('Item', back_populates="parent_list", cascade="all, delete")
    
class Item(db.Model):
    __tablename__ = "items"
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id'), nullable=False)
    task = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.Date)
    is_done = db.Column(db.Boolean)
    parent_list = relationship('List', back_populates="list_items")
      
# db.create_all()   
    
###   Themes   ###

themes = { 'dark': { 'name': 'dark',    
                      'body-th': 'body-dark',
                      'navbar-th': 'navbar-dark bg-dark',
                      'button-label': 'Light theme',
                      'button-style': 'btn-outline-light',
                      'drop-menu': 'dropdown-menu-dark',
                      'drop-button': 'btn-secondary',
                      'header-color': 'bg-dark',
                      'border': 'border-dark',
                      'modal-color': 'mod-body-dark',
                      'modal-close' : 'btn-close-white'
                    },
          'light': {  'name': 'light', 
                      'body-th': 'body-light',
                      'navbar-th': 'navbar-light bg-lite', 
                      'button-label': 'Dark theme',
                      'button-style': 'btn-outline-secondary',
                      'drop-menu': 'dropdown-menu-light',
                      'drop-button': 'dropdown-button-light',
                      'header-color': 'bg-lite',
                      'modal-color': 'body-light',
                      'border': 'border-lite',
                      'modal-close' : ''
                    }
        }

current_theme = themes['light']

###   functions   ###
def set_theme():
    global current_theme
    # case when theme change button is clicked
    theme_to_change = request.args.get('theme')
    if theme_to_change == 'dark':
      current_theme = themes['light']
    elif theme_to_change == 'light':
      current_theme = themes['dark'] 
 
    # case when user is logged in   
    if current_user.is_authenticated and theme_to_change:
      current_user.theme = current_theme['name'] 
      db.session.commit() 
    elif current_user.is_authenticated:
      current_theme = themes[current_user.theme]
      
               
def get_lists():
    # get all user lists if logged in
    if current_user.is_authenticated:
      lists = current_user.user_lists
      categories = unique([lst.category for lst in lists] + ['General'])
      # if user filterd by category get filtered lists
      category = request.args.get('category')
      if category:
        lists = List.query.filter_by(category=category).all()  
      return lists, list(categories)
    return [], ['General']

######    views    ######

@app.route('/')
def home():
    year = datetime.now().year
    set_theme()
    lists, categories = get_lists()
    list_form = CreateNewList()
    list_form.category.choices = categories + ['Add new..']
    item_form = CreateNewItem()
    login_form = LoginForm()
    return render_template("index.html", year=year, listform=list_form, itemform=item_form, loginform=login_form, theme=current_theme, lists=lists, categories=categories)
 
@app.route('/theme')
def change_theme():  
    url = request.args.get('url')
    set_theme()
    if not is_safe_url(url, {host, host2}):
      return abort(400)
    return redirect(url) 


### user management

@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  year = datetime.now().year
  form = SignUpForm()

  if form.validate_on_submit():
    email = form.email.data
    if  User.query.filter_by(email=email).first():
       flash('You are already registered, please login')
       return redirect(url_for('login'))  
        
    new_user = User(
                    email=email,
                    password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8),
                    theme = current_theme['name'],
                    name = form.name.data,
                    verifaction_question = form.question.data,
                    verifaction_answer =  generate_password_hash(form.answer.data.lower(), method='pbkdf2:sha256', salt_length=8) 
                    
                    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    return redirect(url_for('home')) 
  return render_template("register.html", year=year, signupform=form, theme=current_theme)       
    
    
@app.route('/login', methods=['GET', 'POST'])
def login():
  year = datetime.now().year
  form = LoginForm()
  if form.validate_on_submit():
    email = form.email.data
    user =  User.query.filter_by(email=email).first()
    if not user:
      flash('We do not have an account for this email address, please try again or register')
      return redirect(url_for('login'))     
    elif check_password_hash(user.password, form.password.data):
      login_user(user, remember=True) 
      return redirect(url_for('home'))      
    else:
      flash('Password is incorrect')
      return redirect(url_for('login'))     
  return render_template("login.html", year=year, loginform=form, theme=current_theme) 



@app.route('/settings', methods=['GET', 'POST'])
@login_required
def account_settings():
  year = datetime.now().year
  form = SettingsForm( 
                    name=current_user.name,
                    email=current_user.email,
                    theme = current_user.theme,                    
                    )
  if form.validate_on_submit():
      changes = False
      new_name = form.name.data
      new_theme = form.theme.data
      if current_user.name != new_name:
        current_user.name = new_name 
        changes = True
      if current_user.theme != new_theme:
        current_user.theme = new_theme
        changes = True
        set_theme()
      if form.password.data:
        current_user.password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        changes = True
      
      if changes:
        db.session.commit()      
                 
      return redirect(url_for('home')) 
    
  return render_template("account.html", year=year, form=form, theme=current_theme)


@app.route('/verification', methods=['GET','POST'])
def check_email():
  if request.method=='GET':
    return redirect(url_for('login'))
  year = datetime.now().year
  reset_form = ResetForm()
  entered_email = request.form['email']
  user =  User.query.filter_by(email=entered_email).first()
  if user:
      q_num = int(user.verifaction_question)
      q_text= dict(verification_questions).get(q_num)
      verify_form = ResetVerificationForm(
                                        email=entered_email,
                                        question=q_text,
                                        ) 
      
      return render_template("reset.html", year=year, theme=current_theme, verifyform=verify_form, resetform=reset_form) 
  flash('No user account was found')  
  return redirect(url_for('login'))  

@app.route('/reset', methods=['GET', 'POST'])
def check_verification_answer():
  if request.method=='GET':
    return redirect(url_for('login'))
  year = datetime.now().year
  verify_form = ResetVerificationForm()  
  reset_form = ResetForm()
  if verify_form.validate_on_submit():
    
    email = verify_form.email.data
    user =  User.query.filter_by(email=email).first()
    if check_password_hash(user.verifaction_answer, verify_form.answer.data.lower()):
      reset_form = ResetForm(
                          email=email,
                          is_verified=True
                            )
    else:
      flash('answer is wrong')
    return render_template("reset.html", year=year, theme=current_theme, verifyform=verify_form, resetform=reset_form) 

  return render_template("reset.html", year=year, theme=current_theme, verifyform=verify_form, resetform=reset_form)  

@app.route('/reset_password', methods=['GET', 'POST'])
def reset():
  if request.method=='GET':
    return redirect(url_for('login'))  
  year = datetime.now().year
  verify_form = ResetVerificationForm()  
  reset_form = ResetForm()
  if reset_form.validate_on_submit():
    email = reset_form.email.data
    user =  User.query.filter_by(email=email).first()
    user.password = generate_password_hash(reset_form.password.data, method='pbkdf2:sha256', salt_length=8)
    db.session.commit()
    return redirect(url_for('login'))
  
  return render_template("reset.html", year=year, theme=current_theme, verifyform=verify_form, resetform=reset_form) 
         

@app.route('/logout')
@login_required 
def logout():
  logout_user()
  return redirect(url_for('home'))


@app.route('/delete_account')
@login_required
def delete_account():
  user_to_delete = current_user
  db.session.delete(user_to_delete) 
  db.session.commit()
  return redirect(url_for('home')) 
  
### list management 

@app.route('/new_list', methods=['POST'])
def create_list(): 
    form = CreateNewList()
    # next line is to avoid 'TypeError: Choices cannot be None.' since the choices are actually set in the home view
    form.category.choices = []
    if  form.validate_on_submit():
        if form.category.data == 'Add new..':
          category = form.new_category.data.title()
        else:  
          category = form.category.data.title()
          
        new_list = List(
                        category = category,
                        color = form.color.data,
                        parent_user = current_user
                        )
        
        db.session.add(new_list)
        db.session.commit() 
        return redirect(url_for('home')) 
    flash('You must enter a category')    
    return redirect(url_for('home'))         

@app.route('/new_task', methods=['POST'])
def create_item(): 
    form = CreateNewItem()
    if  form.validate_on_submit():
        
        list_id = form.list_id.data
        requested_list = List.query.get(list_id)
        new_item = Item(
                    task = form.text.data,
                    is_done = False,
                    parent_list = requested_list
                    )

        db.session.add(new_item)
        db.session.commit() 
        
        url = url_for('home', _anchor=list_id)
    
        if not is_safe_url(url, {host, host2}):
          return abort(400)

        return redirect(url) 
    
@app.route('/delete_list')
def delete_list(): 
    list_id = request.args.get('list_id')
    list_to_delete = List.query.get(list_id)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('home')) 
  
@app.route('/delete_task')
def delete_item(): 
    item_id = request.args.get('item_id')
    item_to_delete = Item.query.get(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    
    list_id = request.args.get('list_id')
    
    url = url_for('home', _anchor=list_id)
    
    if not is_safe_url(url, {host, host2}):
      return abort(400)
    
    return redirect(url) 
    
# views getting POSTS from fetch-API
  
@app.route('/update_task_status', methods=['POST'])
def update_checkbox_status():
    
    status = request.get_json()  
    res = make_response(jsonify({'message': 'ok'}), 200)
    
    item_id = status['item_id']
    requested_item = Item.query.get(item_id)
    requested_item.is_done = status['is_checked']
    db.session.commit() 
       
    return res

@app.route('/update_task_text', methods=['POST'])
def update_task_text():
    
    status = request.get_json()  
    res = make_response(jsonify({'message': 'ok'}), 200)
    
    item_id = status['item_id']
    requested_item = Item.query.get(item_id)
    requested_item.task = status['text']
    requested_item.is_done = status['unchecked']
    db.session.commit() 
    
    return res
  
@app.route('/update_task_date', methods=['POST'])
def update_task_date():
    
    status = request.get_json()  
    res = make_response(jsonify({'message': 'ok'}), 200)
    
    item_id = status['item_id']
    requested_item = Item.query.get(item_id)
    # convert date string to datetime.date object
    if status['date'] == '':
      requested_item.due_date = None
    else:  
      year = int(status['date'].split('-')[0])
      month = int(status['date'].split('-')[1])
      day = int(status['date'].split('-')[2])
      requested_item.due_date = date(year, month, day)
    
    db.session.commit() 
    
    return res
  
@app.route('/update_category_color', methods=['POST'])
def update_category_color():
    
    status = request.get_json()  
  
    category = status['category']
    new_color = status['color']
    lists_to_update = List.query.filter_by(category=category).update({List.color: new_color})    
    db.session.commit()
    
    if status['filter_cat']:
      url = url_for('home', category=category)
    else:
      url = url_for('home')
          
    if not is_safe_url(url, {host, host2}):
      return abort(400)

    flash(f'updated: {lists_to_update}', 200)
    return redirect(url) 

  
@app.route('/update_list_color', methods=['POST'])
def update_list_color():
    
    status = request.get_json()  
  
    list_id = status['list_id']
    new_color = status['color']
    requested_list = List.query.get(list_id)
    requested_list.color = new_color
    db.session.commit() 
    
    flash('updated', 200)
    return redirect(url_for('home'))   
   

if __name__ == "__main__":
    app.run(debug=True)