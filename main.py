from flask import Flask, render_template  , request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
import json
import os 
# from werkzeug import secure_filename
import math


os.chdir("D:\Programming\AI_Frameworks\Flask\Blog")
with open("config.json","r") as c:
    para = json.load(c) ["params"]

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['Upload_Folder'] = para['uloc']
# app.config.update(
#     MAIL_SERVER = 'smtp.gmail.com',
#     MAIL_PORT = '465',
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME = para['gmail-user'],
#     MAIL_PASSWORD = para['gmail-pass']
#  )
mail = Mail(app)
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = para["local_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = para["prod_uri"]

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(12), nullable=False)
    mno = db.Column(db.Integer, nullable=True)
    message = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable = True)
    email = db.Column(db.String(20), nullable = True)

class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(12), nullable=False)
    content = db.Column(db.String(255), nullable=True)
    title = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable = True)
    imgfile = db.Column(db.String(12), nullable = True)
    

@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)/int(para['no_of_posts']))
    page= request.args.get('page')
    if not str(page).isnumeric():
        page = 1
    page = int(page)
    posts = posts[(page-1)*int(para['no_of_posts']):(page-1)*int(para['no_of_posts'])+int(para['no_of_posts'])]    
    if page == 1:
        prev = "#"
        nextp = "/?page=" +str(page+1)
    elif page == last:
        prev = "/?page=" +str(page-1)
        nextp = "#"
    else:
        prev = "/?page=" +str(page-1)
        nextp = "/?page=" +str(page+1)
    return render_template('index.html', posts = posts, prev = prev, nextp = nextp)

@app.route("/login", methods = ['GET','POST'])
def login():
    return render_template('login.html', params = para)

@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():
    if 'user' in session and session['user'] == para['uname']:
        posts = Posts.query.all()
        return render_template('dashboard.html', params = para, posts = posts)

    if request.method == "POST":
        username = request.form.get("uname")
        password = request.form.get("password")
        if username == para["uname"] and password == para["upassword"]:
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html', params = para, posts = posts )
    else:
        return render_template('login.html', params = para)

@app.route("/uploader", methods = ['GET','POST'])
def uploader():
    if 'user'in session and session['user']== para['uname']:
        if (request.method == "POST"):
            f = request.files['file1']
            f.save(os.path.join(app.config['Upload_Folder']), f)
            return "uploaded successfully"
       
@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/edit/<string:sno>", methods = ['GET', 'POST'])
def edit(sno):
    if 'user' in session and session['user'] == para['uname']:
        if request.method == "POST":
            title = request.form.get("title")
            slug =request.form.get("slug")
            content = request.form.get("content")
            imgfile = request.form.get("imgfile")
            date = datetime.now()

            if sno =='0':
                
                insert = Posts(title = title  , imgfile = imgfile , content = content, slug = slug, date = date)
                db.session.add(insert)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = title
                post.imgfile = imgfile
                post.content = content
                post.slug = slug
                post.date = date
                db.session.commit()
                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()      
        return render_template('edit.html',params = para , post = post, sno =sno)
        
@app.route("/contact", methods = ['GET','POST'])
def contact():
    # The variables in the brackets are the variable names in the form in the html page
    if request.method == 'POST':
        naam = request.form.get("name1")
        eadd = request.form.get("mail")
        phno = request.form.get("mobno")
        msg = request.form.get("feedback")
        entry = Contacts(name = naam, email = eadd, mno = phno, date = datetime.now(), message = msg)
        db.session.add(entry)
        db.session.commit() 
        # mail.send_message(f"New message from {naam}",
        #                   sender  = eadd,
        #                   recipients = [para['gmail-user']], 
        #                   body = f"{msg} + \n+ {phno}")
    
    return render_template('contact.html')

@app.route("/post/<string:post_slug>", methods = ['GET'])
def postf(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template("post.html", para = "params", post = post,)

@app.route("/logout")
def logout():
    session.pop('user')
    return render_template('login.html', params = para)

@app.route("/delete/<string:sno>",methods =['GET','POST'])
def delete(sno):
    if 'user' in session and session['user'] == para['uname']:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')



app.run(debug=True)

