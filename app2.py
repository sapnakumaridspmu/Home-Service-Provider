from flask import Flask,render_template,request,redirect,url_for,flash,session
from user import UserOperation                                  # .py file,  class name  or ek object chahiye 
from encryption import Encryption 
from validation import Validation
from orgniser import OrgOperation


app=Flask(__name__)                               # object of flask class server, routing
app.secret_key="ghijklmnopqrstfghuy45lklk"    #any value you can put here                                        

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
            

@app.route('/user_logout')
def user_logout():
     session.clear()  # this is destroy all activated session
     flas("successfully logged out")
     return redirect(url_for('index'))       #index function name hota h yha    

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

@app.route('/user_delete')
def user_delete():
     if 'email' in session:
          userObj.user_delete()
          flash("Account Deleted Successfully...See you soon!!!")
          return redirect(url_for('index'))
     else:
          flash("please login to access this page..")     
          return redirect(url_for('user_login'))            

@app.route('/forget_password')
def forget_password():
     return render_template('forget_password.html')    
#_________password change_________________

@app.route('/user_change_password',methods=['GET','POST'])
def user_change_password():
    if 'email' in session:
        if request.method=='GET':
            return render_template('user_change_password.html')
        else:
            oldPassword=request.form['oldPassword']
            newPassword=request.form['newPassword']
            # -------------validation--------------------
            frmList=[oldPassword,newPassword]
            if(validObj.empty(frmList)):
                flash("field can't be empty!!")
                return redirect(url_for('user_change_password'))
            
            #-------------encryption---------------------
            oldPassword=encryptObj.convert(oldPassword)  # encryption
            newPassword=encryptObj.convert(newPassword)  # encryption
            r = userObj.user_change_password(oldPassword,newPassword)
            if(r==0):
                flash("your old password is not valid!!")
                return redirect(url_for('user_change_password'))
            else:
                session.clear()
                flash("your password is changed successfully!!")
                return redirect(url_for('user_login'))
    else:
        flash("please login to access this page..")
        return redirect(url_for('user_login'))


@app.route('/user_camp_explore',methods=['GET','POST'])
def user_camp_explore():
     if 'email' in session:
          if request.method=='GET':
               return render_template('user_camp_explore.html')
          else:
               city = request.form['city'] 
               record=userObj.user_camp_explore(city) 
               return render_template('user_camp_explore.html',record=record)       
     else:
          flash("please login to access this page..")     
          return redirect(url_for('user_login'))          

# __________________________________________________________________
# ___________________________organiser______________________________
# __________________________________________________________________  



@app.route('/org_signup',methods=['GET','POST'])
def org_signup():
    if request.method=='GET':
        return render_template('org_signup.html')
    else:
        name=request.form['name']
        email=request.form['email']
        mobile=request.form['mobile']
        address=request.form['address']
        password=request.form['password']
        # -------------validation--------------------
     #    frmList=[name,email,mobile,password]
     #    if(validObj.empty(frmList)):
     #        flash("field can't be empty!!")
     #        return redirect(url_for('user_signup'))
        
        if(validObj.checkAlpha(name)):
            flash("Name must be in alphabates!!")
            return redirect(url_for('user_signup'))
        
        if(validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('user_signup'))


        password=encryptObj.convert(password)  # encryption


        orgObj.org_signup(name,email,mobile,address,password)
        flash("Successfully Registered!! Login Now!!")   #temp session
        return redirect(url_for('org_login'))

@app.route('/org_login',methods=['GET','POST'])
def org_login():
    if request.method=='GET':
        return render_template('org_login.html')
    else:
        email=request.form['email']
        password=request.form['password']
        # -------------validation--------------------
     #    frmList=[email,password]
     #    if(validObj.empty(frmList)):
     #        flash("field can't be empty!!")
     #        return redirect(url_for('org_login'))
        
        password=encryptObj.convert(password)  # encryption

        row = orgObj.org_login(email,password)
        if (row):
            session['org_name']=row[0][0]
            session['org_email']=row[0][1]
            return redirect(url_for('org_dashboard'))
        else:
            flash("Invalid user & password!!")
            return redirect(url_for('org_login'))
            

@app.route('/org_logout')
def org_logout():
     session.clear()  # this is destroy all activated session
     flash("successfully logged out")
     return redirect(url_for('index'))       #index function name hota h yha    

@app.route('/org_dashboard')
def org_dashboard():
     if 'org_email' in session:
          return render_template('org_dashboard.html')
     else:
          flash("please login to access this page..")     
     return redirect(url_for('org_login'))  


@app.route('/org_profile',methods=['GET','POST'])
def org_profile():
     if 'org_email' in session:
          if request.method=='GET':
               record = orgObj.org_profile()
               return render_template('org_profile.html',record=record)
          else:
               name=request.form['name']
               mobile=request.form['mobile']
          # -------------validation--------------------
          frmList=[name,mobile]
          if(validObj.empty(frmList)):
               flash("field can't be empty!!")
               return redirect(url_for('org_profile'))
        
          if(validObj.checkAlpha(name)):
               flash("Name must be in alphabates!!")
               return redirect(url_for('org_profile'))
        
          if(validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
               flash("Mobile must be a number with length of 10 digits!!")
               return redirect(url_for('org_profile'))
          #-------- end validation------------------------
          orgObj.org_profile_update(name,mobile)
          flash("your profile is updated successfully!!")
          return redirect(url_for('org_profile'))         
     else:
          flash("please login to access this page..")
          return redirect(url_for('org_login'))


@app.route('/org_change_password',methods=['GET','POST'])
def org_change_password():
     if 'org_email' in session:
          if request.method=='GET':
               record=organiserObj.org_profile()
               return render_template('org_change_password.html',record=record)
          else:
               oldPassword=request.form['oldPassword']
               newPassword=request.form['newPassword']
              #___________________validation____________________
               frmList=[oldPassword,newPassword]
               if(validObj.empty(firmList)):
                    flash("field can't be empty!!")
                    return redirect(url_for('org_change_password'))

               #----------encryption-------------------
               oldPassword=encryptObj.convert('oldPassword') 
               newPassword=encryptObj.convert('newPassword')
               r=organiserObj.org_change_password(oldPassword,newPassword)
               if(r==0):
                    flash("your old password is not valid !!")
                    return redirect(url_for('org_change_password'))
               else:
                    session.clear()
                    flash("your password is change successfully!!")
                    return redirect(url_for('org_login')) 
     else:
          flash("please login to access this page..")
          return redirect(url_for('org_login'))
    

@app.route('/org_delete')
def org_delete():
     if 'org_email' in session:
          orgObj.user_delete()
          flash("Account Deleted Successfully...See you soon!!!")
          return redirect(url_for('index'))
     else:
          flash("please login to access this page..")     
          return redirect(url_for('org_login'))   



@app.route('/org_forget_password')
def org_forget_password():
     return render_template('org_forget_password.html')

@app.route('/org_new_camp',methods=['GET','POST'])
def org_new_camp():
     if 'org_email' in session:
          if request.method=='GET':
               return render_template('org_new_camp.html')   
          else:
               campName=request.form['campName']
               contact=request.form['contact']
               city=request.form['city']
               location=request.form['location']
               startDate=request.form['startDate']
               endDate=request.form['endDate']
               charges=request.form['charges']
               descp=request.form['descp']

               #_________________ validation_______________
               # frmList=[campName,contact,city,location,startDate,endDate,charges,descp]
               # if(validObj.empty(frmList)):
               #      flash("field can't be empty!!")
               #      return redirect(url_for('org_new_camp'))

               orgObj.org_new_camp(campName,contact,city,location,startDate,endDate,charges,descp)  
               flash("Your new Camp Detail submitted successfully!!")   #temp session
               return redirect(url_for('org_new_camp'))
     else:
          flash("Please login to access this page..") 
          return redirect(url_for('org_login'))         
               
@app.route('/org_view_camp')
def org_view_camp():
     if 'org_email' in session:   #verify karega
          record = orgObj.org_view_camp()  # yha call kar data ko bhejenge record me 
          return render_template('org_view_camp.html',record=record) # record pass hoga record me hai
     else:
          flash("please login to access this page..")     
     return redirect(url_for('org_login'))  

@app.route('/org_camp_delete',methods=['GET','POST'])   
def org_camp_delete():
     if 'org_email' in session:
          if request.method=="GET":
               campID = request.args.get('campID')
               orgObj.org_camp_delete(campID)
               flash("your camp is delete successfully!!")
               return redirect(url_for('org_view_camp'))
     else:
          flash("Please login to access this page..")
          return redirect(Url_for('org_login'))          


@app.route('/org_camp_detail',methods=['GET','POST']) 
def org_camp_detail():
     if 'org_email' in session:
          if request.method=='GET':
               campID = request.args.get('campID')
               record=orgObj.org_camp_detail(campID)    
               return render_template('org_camp_detail.html',record=record) 
          else:
               campID=request.args.get('campID')
               campName=request.form['campName']
               contact=request.form['contact']
               city=request.form['city']
               location=request.form['location']
               startDate=request.form['startDate']
               endDate=request.form['endDate']
               charges=request.form['charges']
               descp=request.form['descp']

               #_________________ validation_______________
               # frmList=[campName,contact,city,location,startDate,endDate,charges,descp]
               # if(ValidObj.empty(frmList)):
               #      flash("field can't be empty!!")
               #      return redirect(url_for('org_new_camp'))

               orgObj.org_camp_edit(campID,campName,contact,city,location,startDate,endDate,charges,descp)  
               flash("Camp Detail Updated successfully!!")   #temp session
               return redirect(url_for('org_camp_detail',campID=campID))
     else:
          flash("Please login to access this page..") 
          return redirect(url_for('org_login'))  


@app.route('/org_camp_photo',methods=['GET','POST'])
def org_camp_photo():
    if 'org_email' in session:
        if request.method=="GET":
            campID = request.args.get('campID')
            photo = orgObj.org_camp_photo_view(campID)
            return render_template('org_camp_photo.html',campID=campID,photo=photo)
        else:
            campID = request.args.get('campID')
            photo = request.files['photo']

            p = photo.filename  # retrive photo name with extention
            d = datetime.now() #current date time (import datetime)
            t=int(round(d.timestamp()))
            path = str(t)+'.'+p.split('.')[-1]
            photo.save("static/camp/" + path)  #create camp folder inside static folder
            orgObj.org_camp_photo(campID,path)
            flash("Photo Uploaded Successfully!!")
            return redirect(url_for('org_camp_photo',campID=campID))   
    else:
        flash("please login to access this page..")
        return redirect(url_for('org_login'))                              


if __name__=='__main__':   #secure, ye(app.py) file jab direct run karenge tabhi ye run karega 
#app.run(debug=True)
#app.run(port='5001')
  app.run(host='0.0.0.0',port='5001',debug=True) 


