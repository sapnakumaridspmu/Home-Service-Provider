import mysql.connector
from flask import session


class OrgOperation:
    def connection(self):
        con=mysql.connector.connect(host="localhost",port="3306",user="root",password="",database="homeservice")
        return con

    def admin_signup(self,name,email,mobile,city,password):
        db=self.connection()
        mycursor=db.cursor()
        sq="insert into admin(name,email,mobile,city,password) values(%s,%s,%s,%s,%s)"
        record=[name,email,mobile,city,password]  
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return 

    def admin_login(self,email,password):
        db=self.connection()
        mycursor=db.cursor()
        sq="select name,email from admin where email=%s and password=%s"
        record=[email,password]
        mycursor.execute(sq,record)
        row = mycursor.fetchall()
        # count = mycursor.rowcount  #number of record
        mycursor.close()
        db.close()
        return row
    
    def admin_profile(self):
        db=self.connection()
        mycursor=db.cursor()
        sq="select name,email,mobile,city from admin where email=%s"
        record=[session['admin_email']]
        mycursor.execute(sq,record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def admin_profile_update(self,name,mobile,city):
        db=self.connection()
        mycursor=db.cursor()
        sq="update admin set name=%s,mobile=%s,city=%s where email=%s"
        record=[name,mobile,session['admin_email']]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return 
 #_____________________________

    def org_delete(self):
        db=self.connection()
        mycursor=db.cursor()
        sq="delete from user where email=%s"
        record=[session['org_email']]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return 

    def org_change_password(self,oldPassword,newPassword):
        db=self.connection()
        mycursor=db.cursor()
        sq="select * from user where email=%s and password=%s"
        record=[session['org_Email'],oldPassword]
        mycursor.execute(sq,record) 
        row=mycursor.fetchall()
        rc = mycursor.rowcount
        if(rc==0):
            return 0

        sq="update organiser set password=%s where email=%s"
        record=[newPassword,session['org_email']]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return 1       

        # ___________________________
        # __________________________
    def org_new_camp(self,campName,contact,city,location,startDate,endDate,charges,descp):
        db=self.connection()
        mycursor=db.cursor()
        sq="insert into camp (orgEmail,campName,contact,city,location,startDate,endDate,charges,descp) values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        record=[session['org_email'],campName,contact,city,location,startDate,endDate,charges,descp] 
        mycursor.execute(sq,record)  
        db.commit()
        mycursor.close()
        db.close()
        return    

    def org_view_camp(self):
        db=self.connection()
        mycursor=db.cursor()
        sq="select campID,campName,city,location,charges from camp where orgEmail=%s" 
        record=[session['org_email']]  
        mycursor.execute(sq,record)
        record=mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def org_camp_delete(self,campID):
        db=self.connection()
        mycursor=db.cursor()
        sq="delete from camp where campID=%s" 
        record=[campID] 
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return         

    def org_camp_detail(self,campID):
        db=self.connection()
        mycursor=db.cursor()
        sq="select campName,contact,city,location,startDate,endDate,charges,descp,campID from camp where campID=%s"   
        record=[campID]
        mycursor.execute(sq,record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def org_camp_edit(self,campID,campName,contact,city,location,startDate,endDate,charges,descp):
        db=self.connection()
        mycursor=db.cursor()
        sq="update camp set campName=%s,contact=%s,city=%s,location=%s,startDate=%s,endDate=%s,charges=%s,descp=%s where campID=%s"   
        record=[campName,contact,city,location,startDate,endDate,charges,descp,campID]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return       


    def org_camp_photo(self,campID,path):
        db=self.connection()
        mycursor=db.cursor()
        sq="insert into camp_photo (campID,path) values(%s,%s)" 
        record=[campID,path]   
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return

    def org_camp_photo_view(self,campID):
        db=self.connection()
        mycursor=db.cursor()
        sq="select path from camp_photo where campID=%s"
        record=[campID]
        mycursor.execute(sq,record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record
   