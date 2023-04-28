from flask import Flask, render_template, request , redirect , Response , send_file , session 
from PIL import Image
import numpy as np
import nltk
#import pandas as pd
import PyPDF2
import builtins
import os
from flask_mysqldb import MySQL

app = Flask(__name__, template_folder='templates')
app.secret_key = "dhrumil"

app.jinja_env.globals.pop('len', None)

app.jinja_env.globals.update(vars(builtins))

app.debug = True


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'ibm'

mysql = MySQL(app)

@app.route('/register_new', methods = ['POST','GET'])
def register_new():
    return render_template('registration.html')

@app.route('/register', methods = ['POST','GET'])
def register():
    if request.method == 'POST':
       
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if username or email already exist in the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        existing_user = cur.fetchone()

        if existing_user:
            # Username or email already exists
            return render_template('registration.html', error='Username or email already exists')

        # Add new user to the database
        cur.execute('INSERT INTO users (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
        mysql.connection.commit()

        # Save user data in session
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        session['user_id'] = user[0]
        session['username'] = user[1]
        session['email'] = user[2]

        return render_template('login.html')

    return render_template('login.html')
   
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']

        # Check if username and password match a record in the database
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cur.fetchone()

        if user:
            # Save user data in session
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]

            return render_template('home.html',name=username)

        else:
            # Invalid credentials
            return render_template('login.html', error='Invalid username or password')

    return render_template('login.html')



@app.route("/logout")
# @login_required
def logout():
    # Clear session data
    session.clear()

    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/')
def upload_file():
    return render_template('login.html')

@app.route('/complaince_chek')
def compliance_check():
    return render_template('index.html')

@app.route('/wazuh')
def wazuh():
    return redirect("https://192.168.56.101/app/login")

@app.route('/hive')
def hive():
    return redirect('http://192.168.56.101:9000/index.html#!/login')

@app.route('/manage_engine')
def manage_engine():
    return redirect('http://desktop-l5jc0u6:8020/client#/login')

global twotwo
twotwo = []
twotwo.append('200 - successfull event occur')
global four
four = []
four.append('404 - page not found')




@app.route('/upload', methods = ['POST','GET'])
def upload_pdf_file():
    if request.method == 'POST':
        f = request.files['file']
        f.save(f.filename) 
        global name
        name = f.filename
        pdfFileObj = open(name, 'rb')
        pdfReader = PyPDF2.PdfReader(pdfFileObj)
        #print(len(pdfReader.pages))
        page = pdfReader.pages[0]
        text = page.extract_text()

        sentences = nltk.sent_tokenize(text) #it is a sentence tokenizer which seperate sentences after full stop.
        words_list = []
        for sentence in sentences:
            #print(sentence)
            words = nltk.word_tokenize(sentence)
            for word in words:
                words_list.append(word)

        global sen
        sen =[]
        a=''
        for i in words_list:
            if i=='2023':
                sen.append(a)
                a=''
            else:
                a=a+i
        
        for i in sen:
            var=i.find("``200")
            if var>=0:
                twotwo.append(i)

        for i in sen:
            var=i.find("``404")
            if var>=0:
                four.append(i)

        global error
        error = []
        
        if '404' in words_list:
            #print("404 - page not found")
            error.append("404 - page not found")
        if 'https' or 'http' or 'HTTP' or 'HTTPS' in words_list:
            #print("https/http - suspicious url")
            error.append("https/http - suspicious url")
        if '200' in words_list:
            #print("200 - successfull event occur")
            error.append("200 - successfull event occur")
        if '302' in words_list:
            #print("302 - specific URL has been moved temporarily to a new location")
            error.append("302 - specific URL has been moved temporarily to a new location")
        if '5712' in words_list:
            #print("5712 - false positive - attacker try to attack but haven't success")
            error.append("5712 - false positive - attacker try to attack but haven't success")
        error = set(error)
        error = list(error)
        path = '/'.join(error)
        return render_template("output.html", name = error, length=len(error),path=path)  
    
@app.route('/more_details', methods = ['POST','GET'])
def more_details():
    global lt
    lt = []
    lt.append(twotwo)
    lt.append(four)
    return render_template("view_logs.html",lt=lt)

import fitz

@app.route('/download', methods = ['POST','GET'])
def download_pdf():
    highlight_color = (1, 1, 0) # yellow
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    doc = fitz.open(name)
    
    text_pdf = []
    for i in lt:
        for j in i:
            text_pdf.append(j)

    #print(text_pdf)
    
    for page in doc:
        page_text = page.get_text("text")
        page_text = page_text.replace('\n','')
        sentences = page_text.split("2023")
        #print(text_pdf)
       # print(type(sentences))
        for sentence in text_pdf:
            word_sentence = nltk.word_tokenize(sentence)
            #print(word_sentence)
            for i in sentences:
                i_sentence = nltk.word_tokenize(i)
                #print(i_sentence)
                if word_sentence[0]==i_sentence[0]:
                    print(i)
                    sentence_rects = page.search_for(i[8:])
                    for rect in sentence_rects:
                        highlight = page.add_highlight_annot(rect)
                        highlight.update()

     
    name_n = name[:-4]
    name_n = name_n+'_highlight.pdf'
    doc.save(name_n)
    doc.close()

   

    return send_file(name_n,as_attachment=True)



if __name__ == '__main__':
    app.run(debug=True)

