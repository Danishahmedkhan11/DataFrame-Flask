from flask import Flask,flash, send_file,render_template,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,EmailField
from wtforms.validators import DataRequired, URL,Email
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
import pandas as pd


app = Flask(__name__)
app.app_context().push()

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:nish@localhost:3306/user_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


Bootstrap(app)

app.config['SECRET_KEY'] = 'asdffasd'
login_manager=LoginManager()
login_manager.init_app(app)

#create edit form with fields
class EditFrom(FlaskForm):
    name=StringField("Name",validators=[DataRequired()])
    street=StringField("Street",validators=[DataRequired()])
    city=StringField("City",validators=[DataRequired()])
    state=StringField("State",validators=[DataRequired()])
    zip=StringField("Zip",validators=[DataRequired()])
    price=StringField("Price",validators=[DataRequired()])
    location=StringField("Location",validators=[DataRequired()])
    submit=SubmitField('Save')


#create table with columns
class User(db.Model):
    __tablename__ = "users"
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(250),nullable=False)
    street=db.Column(db.String(250),nullable=False)
    city=db.Column(db.String(250),nullable=False)
    state=db.Column(db.String(250),nullable=False)
    zip=db.Column(db.String(250),nullable=False)
    price=db.Column(db.String(250),nullable=False)
    location=db.Column(db.String(250),nullable=False)
   
class Login(UserMixin,db.Model):
    __tablename__ = "logins"
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(250),nullable=False)
    password=db.Column(db.String(250),nullable=False)
   


#create database

db.create_all()


@login_manager.user_loader
def login_user_callback(user_id):
    user=Login.query.get(user_id)
    return user

#home
@app.route('/',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)

        isLogin=Login.query.filter_by(username=username).first()

        try:
            if isLogin.username == username and isLogin.password == password:
                print('sucessfully')
                login_user(isLogin)
                return redirect(url_for('home'))
        except:
            flash('Invalid username or password')
    return render_template('login.html')



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/get-user',methods=['GET','POST'])
def home():
    user = User.query.all()
    print(user)
    if request.method =='POST': 
      
        if 'submit' in request.form:
            new_post = User(
                name=request.form.get('name'),
                email=request.form.get('email')
            )
            db.session.add(new_post)
            db.session.commit()
            user = User.query.all()

    return render_template('index.html',usernames=user)



#read file and convert it to save in mysql
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    file = request.files['file']
    if request.method == 'POST':
        # Check if a file was submitted
       
        # Read the file contents
        if file:
            print('Got it!!!')
            data=pd.read_csv(file)
            print(data)
    
            for n in range(len(data)):
                new_post = User(
                    name=data.loc[n].Name,
                    street=data.loc[n].Street,
                    city=data.loc[n].City,
                    state=data.loc[n].State,
                    zip=data.loc[n].Zip,
                    price=data.loc[n].Price,
                    location=data.loc[n].Location
                    )
                db.session.add(new_post)
                db.session.commit()
            return redirect(url_for('home'))
        
        else:
            print('hello')
            flash('Please upload file.')
            return redirect(url_for('home'))
            # Process the file 
       
   
@app.route('/download')
def download():
    # Path to the PDF file
   
    try:
        # Specify the file path
        file_path =  User.query.all()

        # Send the file for download
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return str(e)
    # Send the file as a response
   


#edit username by using id
@app.route('/edit/<int:user_id>',methods=['GET', 'POST'])
def edit(user_id):

    user = User.query.get(user_id)
    edit = EditFrom(
        name=user.name,
        street=user.street,
        city=user.city,
        state=user.state,
        zip=user.zip,
        price=user.price,
        location=user.location,
       
    )

    if edit.validate_on_submit():
        print(user.name)
        user.name = edit.name.data
        user.street = edit.street.data
        user.city = edit.city.data
        user.state = edit.state.data
        user.zip = edit.zip.data
        user.price = edit.price.data
        user.location = edit.location.data

        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html',usernames=user,form=edit)





#delete username
@app.route("/delete/<int:user_id>",methods=['DELETE','GET'])
def delete_post(user_id):
    user_to_delete = User.query.get(user_id)
    db.session.delete(user_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
