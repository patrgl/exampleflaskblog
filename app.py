from flask import render_template, url_for, request, session, redirect
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_bcrypt import Bcrypt 
from database import db, app
from models import User, Blogpost, Comment, Category
from forms import RegistrationForm, LoginForm, BlogCreationForm
from datetime import datetime
from flask_socketio import SocketIO, send
import os


############### CONFIG ###############


basedir = os.path.abspath(os.path.dirname(__file__))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
bcrypt = Bcrypt(app)
socketio = SocketIO(app, cors_allowed_origins="*")

@login_manager.user_loader
def load_user(user_id):
        return User.query.get(int(user_id))

    
############### ROUTES ###############


@app.route('/', methods=['GET', 'POST'])
def index():
    all_posts = list(Blogpost.query.all())
    all_posts.reverse() ##recent first
    return render_template('index.html', all_posts=all_posts, logged_in = session['logged_in'])


@app.route('/login/', methods=['GET', 'POST'])
def login():
    
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        input_username = form.data['username']
        input_password = form.data['password'] 
        user_query = User.query.filter_by(username=input_username).first()
        
        if not user_query:
            return render_template('login.html', form=form, message='User does not exist!')
        
        password_matches = bcrypt.check_password_hash(user_query.password_hash, input_password)
        
        if not password_matches:
            return render_template('login.html', form=form, message='Password incorrect!')
        
        session['current_user'] = user_query.username
        login_user(user_query)
        session['logged_in'] = True
        return redirect(url_for('index'))
    
    return render_template('login.html', form=form)

@app.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    session['current_user'] = ''
    session['logged_in'] = False
    return redirect(url_for('login'))

@app.route('/register/', methods=['GET','POST'])
def register():
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        input_username = form.data['username']
        input_password = form.data['password']
        
        user_query = User.query.filter_by(username=input_username).first()
        if user_query: 
            return render_template('register.html', form=form, message='User already exists!')
        
        new_hashed_password = bcrypt.generate_password_hash(input_password).decode('utf-8')
        
        register_user = User()
        register_user.username = input_username
        register_user.password_hash = new_hashed_password
        db.session.add(register_user)
        db.session.commit()
        
        return render_template('register.html', form=form, message='Registrado, presione Login arriba para ingresar.')
    
    
    return render_template('register.html', form=form, message='')


##crear post
@login_required
@app.route('/create/', methods=['GET', 'POST'])
def create():
    form = BlogCreationForm(request.form)
    form.category.choices = [(c.name, c.name) for c in Category.query.all()]
    author = session['current_user']
    
    if session['current_user'] == '' or session['current_user'] == None:
        return redirect(url_for('login'))

    
    if request.method == 'POST' and form.validate():
        new_post = Blogpost()
        new_post.title = form.data['title']
        new_post.category = form.data['category']
        new_post.author = author
        new_post.body = form.data['body']
        new_post.publish_date = datetime.now()
        
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('index'))
    
    return render_template('create.html', form=form, logged_in = session['logged_in'])

@login_required
@app.route('/posts/<int:id>/', methods=['GET', 'POST'])
def view_post(id):
    post = Blogpost.query.filter_by(id=id).first()
    comments = list(Comment.query.filter_by(parent_id=id))
    comments.reverse()
    
    return render_template('post.html', 
                           post=post,
                           comments=comments, logged_in = session['logged_in'])
    
@login_required
@app.route('/api/add_comment', methods=['GET','POST'])
def add_comment():
    comment_body = request.form['comment_body']
    parent_id = request.form['parent_id']
    if not comment_body or not parent_id:
        print('comment not placed')
        return redirect(url_for('view_post'))
    new_comment = Comment()
    new_comment.author = session['current_user']
    new_comment.parent_id = parent_id
    new_comment.publish_date = datetime.now()
    new_comment.body = comment_body
    
    db.session.add(new_comment)
    db.session.commit()
    return redirect(url_for('view_post', id=parent_id))

@login_required
@app.route('/api/add_category', methods=['GET', 'POST'])
def add_category():
    
    if session['current_user'] == '' or session['current_user'] == None:
        return redirect(url_for('login'))
    
    category_name = request.form['category_name']
    if not category_name:
        return redirect(url_for('categories'))
    new_category = Category()
    new_category.name = category_name
    db.session.add(new_category)
    db.session.commit()
    
    return redirect(url_for('categories'))

@login_required
@app.route('/categories/', methods=['GET', 'POST'])
def categories():
    categories = Category.query.all()
        
    
    return render_template('categories.html', categories=categories, logged_in = session['logged_in'])

@socketio.on('message')
def handle_message(message):
    print("Message: " + message)
    if message != "User connected":
        send(message, broadcast=True)
        
@login_required
@app.route('/chat/')
def chat():

    if session['current_user'] == '' or session['current_user'] == None:
        return redirect(url_for('login'))    

    return render_template('chat.html', username=session['current_user'], logged_in = session['logged_in'])

@app.errorhandler(KeyError) 
def handle_error(error):
    print('ERROR IS: ', error)
    return redirect(url_for('login')) 

@app.errorhandler(404)
def not_found_error(error):
    print('ERROR IS: ', error)
    return render_template('404.html'), 404

if __name__ == '__main__':
    ##remember to init DB
    '''
    with app.app_context():
        db.create_all() r
    '''
    
    socketio.run(app, host='127.0.0.1', debug=True) ## switch to current ip on network if you want chat to work on local network
##    app.run(debug=True)
