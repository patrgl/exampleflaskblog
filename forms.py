from wtforms.validators import InputRequired, Length
from wtforms import Form, StringField, SelectField, PasswordField, TextAreaField, SelectField

class RegistrationForm(Form):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Password"})

class LoginForm(Form):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Username"}) 
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder" : "Password"})

class BlogCreationForm(Form):
    title = StringField('Title')
    author = StringField('Author')
    category = SelectField('Category')
    body = TextAreaField('Content')