from flask import Flask, render_template, request, redirect, flash
from flask_login import UserMixin, login_user, logout_user, login_required, current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = '4a431f697a066c19b8614e74c97b3c6f9b4eef1666a3728f'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Create LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'register'






class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
"""
>>> from app import*
>>> app.app_context().push()
>>> db.create_all()
"""

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    todos = db.relationship('Todo', backref='user', lazy=True)
        # Flask-Login required method to check if the user is active
    def is_active(self):
        return True  # You may adjust this based on your application logic

    # Flask-Login required method to get the unique identifier for the user
    def get_id(self):
        return str(self.id)
    
    # Flask-Login required method to check if the user is authenticated
    def is_authenticated(self):
        return True 








@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            #return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
            return redirect('/login') # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        # return redirect(url_for('main.profile'))
        login_user(user)
        return redirect('/')

    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method=='POST':
        email = request.form['email']
        pass1 = request.form['password1']
        pass2 = request.form['password2']
        if(pass1==pass2):
            user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database
            if user: # if a user is found, we want to redirect back to signup page so user can try again
                # return redirect(url_for('auth.signup'))
                flash('Email address already exists')
                # return redirect('/register')

            # create a new user with the form data. Hash the password so the plaintext version isn't saved.
            new_user = User( email=email, password=generate_password_hash(pass1, method='pbkdf2:sha256'))

            # add the new user to the database
            db.session.add(new_user)
            db.session.commit()
        else: 
            flash('Password does not match')

    return render_template('register.html')


@app.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect('/login')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.route('/', methods=['GET', 'POST'])
@login_required
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        # Make sure user_id is an integer before inserting into the database
        user_id = current_user.id if current_user.is_authenticated else None

        todo = Todo(title=title, desc=desc, user_id=user_id)
        db.session.add(todo)
        db.session.commit()
    
    user_id = current_user.id if current_user.is_authenticated else None
    allTodo = Todo.query.filter_by(user_id= user_id).all()

    q=request.args.get('q')   #request.GET.get is only for django
    if(q):
        allTodo = Todo.query.filter(Todo.title.contains(q), Todo.user_id==user_id).all()
    return render_template('index.html', allTodo=allTodo)

@app.route('/show')
@login_required
def products():
    allTodo = Todo.query.all()
    print(allTodo)
    return 'this is products page'

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
@login_required
def update(sno):
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/")
        
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)

"""
@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update_something(sno):
    # The value captured from the URL as an integer is now available as 'sno'
    return f'The sno is: {sno}'
"""


#<int:sno> just denote that an integer is passed in the url, in html the url will be like /123, so 123 will be passed into this function as sno
#so just find the todo with that sno by filter_by method and continue
@app.route('/delete/<int:sno>')   
@login_required
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True, port=8000)