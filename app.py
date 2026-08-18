import os
from flask import Flask,render_template,request,redirect,url_for,flash,session
from user import UserOperation                                  # .py file,  class name  or ek object chahiye 
from encryption import Encryption 
from validation import Validation
from admin import OrgOperation


app=Flask(__name__)        
app.secret_key = os.environ.get("SECRET_KEY", "home-service-secret-key")                       # object of flask class server, routing
# app.secret_key="ghijklmnopqrstfghuy45lklk"    #any value you can put here                                        

userObj = UserOperation()                                               #object for user   --ab ese clll karna hoga
encryptObj = Encryption()                                 #object for encryption class
validObj = Validation()                                     #object for  digit validation 
orgObj = OrgOperation()         #object for orgniser

# @app.route('/')
# def index():
#      return "hello flask"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/user_signup',methods=['GET','POST'])
def user_signup():
    if request.method=='GET':
        return render_template('user_signup.html')
    else:
        name=request.form['name']
        email=request.form['email']
        mobile=request.form['mobile']
        password=request.form['password']

        # -------------validation--------------------
        frmList=[name,email,mobile,password]
        if(validObj.empty(frmList)):
            flash("field can't be empty!!")
            return redirect(url_for('user_signup'))
        
        if(validObj.checkAlpha(name)):
            flash("Name must be in alphabates!!")
            return redirect(url_for('user_signup'))
        
        if(validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('user_signup'))


        password=encryptObj.convert(password)  # encryption


        userObj.user_signup(name,email,mobile,password)
        flash("Successfully Registered!! Login Now!!")   #temp session
        return redirect(url_for('user_login'))

@app.route('/user_login',methods=['GET','POST'])
def user_login():
    if request.method=='GET':
        return render_template('user_login.html')
    else:
        email=request.form['email']
        password=request.form['password']
        # -------------validation--------------------
     #    frmList=[email,password]
     #    if(validObj.empty(frmList)):
     #        flash("field can't be empty!!")
     #        return redirect(url_for('user_login'))
        
        password=encryptObj.convert(password)  # encryption

        row = userObj.user_login(email,password)
        if (row):
            session['name']=row[0][0]
            session['email']=row[0][1]
            return redirect(url_for('user_dashboard'))
        else:
            flash("Invalid user & password!!")
            return redirect(url_for('user_login'))
    
@app.route('/user_dashboard')
def user_dashboard():
     if 'email' in session:
        return render_template('user_dashboard.html')
     else:
        flash("please login to access this page..")     
        return redirect(url_for('user_login'))  


@app.route('/user_profile',methods=['GET','POST'])
def user_profile():
     if 'email' in session:
          if request.method=='GET':
               record = userObj.user_profile()
               return render_template('user_profile.html',record=record)
          else:
               name=request.form['name']
               mobile=request.form['mobile']
          # -------------validation--------------------
          frmList=[name,mobile]
          if(validObj.empty(frmList)):
               flash("field can't be empty!!")
               return redirect(url_for('user_profile'))
        
          if(validObj.checkAlpha(name)):
               flash("Name must be in alphabates!!")
               return redirect(url_for('user_profile'))
        
          if(validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
               flash("Mobile must be a number with length of 10 digits!!")
               return redirect(url_for('user_profile'))
          #-------- end validation------------------------
          userObj.user_profile_update(name,mobile)
          flash("your profile is updated successfully!!")
          return redirect(url_for('user_profile'))         
     else:
          flash("please login to access this page..")
          return redirect(url_for('user_login'))    
   
@app.route('/ac_repair_card')
def ac_repair_card():
     if 'email' in session:
        return render_template('ac_repair_card.html')
     else:
        flash("please login to access this page..")     
        return redirect(url_for('user_login')) 
       


# ........................................................
@app.route('/card1')
def card1():
     if 'email' in session:
        return render_template('card1.html')
     else:
        flash("please login to access this page..")     
        return redirect(url_for('user_login'))   


@app.route('/card2')
def card2():
     if 'email' in session:
        if request.method=='GET':
            return render_template('card2.html')
     else:
        flash("please login to access this page..")     
        return redirect(url_for('user_login'))  

# ----------------------------------------------------------

@app.route('/booking',methods=['GET','POST']) 
def booking():
     if 'email' in session:
          if request.method=='GET':
            #    campID = request.args.get('campID')
            #    record=userObj.booking(campID)    
               return render_template('booking.html',) 
          else:
               name=request.args.get('name')
               email=request.form['email']
               contact=request.form['contact']
               service=request.form['service']
               address=request.form['address']
               landmark=request.form['landmark']


               userObj.booking(name,email,contact,service,address,landmark)  
               flash("your Booking has successfully completed!!")   #temp session
               return redirect(url_for('booking'))
     else:
          flash("Please login to access this page..") 
          return redirect(url_for('user_login')) 


@app.route('/admin_signup',methods=['GET','POST'])
def admin_signup():
    if request.method=='GET':
        return render_template('admin_signup.html')
    else:
        name=request.form['name']
        email=request.form['email']
        mobile=request.form['mobile']
        city=request.form['city']
        password=request.form['password']

        # -------------validation--------------------
        frmList=[name,email,mobile,city,password]
        if(validObj.empty(frmList)):
            flash("field can't be empty!!")
            return redirect(url_for('admin_signup'))
        
        if(validObj.checkAlpha(name)):
            flash("Name must be in alphabates!!")
            return redirect(url_for('admin_signup'))
        
        if(validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('admin_signup'))


        password=encryptObj.convert(password)  # encryption


        orgObj.admin_signup(name,email,mobile,city,password)
        flash("Successfully Registered!! Login Now!!")   #temp session
        return redirect(url_for('admin_login'))        

@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method=='GET':
        return render_template('admin_login.html')
    else:
        email=request.form['email']
        password=request.form['password']
        # -------------validation--------------------
        password=encryptObj.convert(password)  # encryption

        row = orgObj.admin_login(email,password)
        if (row):
            session['admin_name']=row[0][0]
            session['admin_email']=row[0][1]
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid user & password!!")
            return redirect(url_for('admin_login'))

@app.route('/admin_dashboard')
def admin_dashboard():
     if 'admin_email' in session:
        return render_template('admin_dashboard.html')
     else:
        flash("please login to access this page..")     
        return redirect(url_for('admin_login'))  

@app.route('/admin_profile',methods=['GET','POST'])
def admin_profile():
     if 'admin_email' in session:
          if request.method=='GET':
               record = orgObj.admin_profile()
               return render_template('admin_profile.html',record=record)
          else:
               name=request.form['name']
               mobile=request.form['mobile']
          # -------------validation--------------------
          frmList=[name,mobile]
          if(validObj.empty(frmList)):
               flash("field can't be empty!!")
               return redirect(url_for('admin_profile'))
        
          if(validObj.checkAlpha(name)):
               flash("Name must be in alphabates!!")
               return redirect(url_for('admin_profile'))
        
          if(validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
               flash("Mobile must be a number with length of 10 digits!!")
               return redirect(url_for('admin_profile'))
          #-------- end validation------------------------
          city=request.form['city']
          orgObj.admin_profile_update(name,mobile,city)
          flash("your profile is updated successfully!!")
          return redirect(url_for('admin_profile'))         
     else:
          flash("please login to access this page..")
          return redirect(url_for('admin_login'))                  

if __name__=='__main__':
    app.run(debug=True)
