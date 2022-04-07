from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField, SelectField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError, Optional
from string import punctuation
import re


verification_questions = [(1, "Your mothers' maiden name"), (2, "Your first pets' name"), (3, "The street you grew up in")]

######    Forms    ######

def validate_password(form, field):
  '''
  Validation for password complexity.
  '''
  lowcase = re.search("[a-z]", field.data)
  upcase = re.search("[A-Z]", field.data)
  number = re.search("\d", field.data)
  special = re.search(re.compile(f'[{re.escape(punctuation)}]'), field.data)
  if not lowcase or not upcase or not number or not special:
    raise ValidationError('Password must contain numbers, uppercase, lowercase & special characters')
        
class SignUpForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=12, message='Password must be between %(min)d and %(max)d characters'), validate_password])
    confirm = PasswordField('Re-enter', validators=[DataRequired(), EqualTo('password', message='Passwords must match'), Length(max=12)])
    question = SelectField('verfication', default=verification_questions[0], coerce=int, choices=verification_questions)
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('SignUp')
        
class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')    

class SettingsForm(FlaskForm):
    name = StringField('Username', validators=[DataRequired()])  
    email = EmailField('Email', render_kw={'readonly': True})
    password = PasswordField('Password', validators=[Optional(), Length(min=8, max=12, message='Password must be between %(min)d and %(max)d characters'), validate_password])
    confirm = PasswordField('Re-enter', validators=[Optional(), EqualTo('password', message='Passwords must match'), Length(max=12)])
    theme = SelectField('Theme', coerce=str, choices=['dark', 'light'])
    submit = SubmitField('Save changes')

class ResetVerificationForm(FlaskForm):
    email = EmailField('Email', render_kw={'readonly': True})
    question = StringField('Verification', render_kw={'readonly': True})
    answer = StringField('Answer', validators=[DataRequired()])
    
    submit = SubmitField('Verify') 
    
    
class ResetForm(FlaskForm):
    email = EmailField('Email', render_kw={'readonly': True})
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=12, message='Password must be between %(min)d and %(max)d characters'), validate_password])
    confirm = PasswordField('Re-enter', validators=[DataRequired(), EqualTo('password', message='Passwords must match'), Length(max=12)])
    is_verified = HiddenField()
    submit = SubmitField('Reset')    

class CreateNewList(FlaskForm):
    category = SelectField('Category', default='General', coerce=str, validate_choice=False)
    new_category = StringField('Name', default='General', validators=[DataRequired()]) 
    color = SelectField('Color', default='orange', choices=['orange', 'purple', 'green', 'pink', 'yellow'], coerce=str)
    submit = SubmitField('Create')
    
class CreateNewItem(FlaskForm):
    text = StringField('', validators=[DataRequired()], render_kw={"placeholder": "enter new task.."})
    list_id = HiddenField()
    submit = SubmitField('Add') 

