import os
import psycopg2
from flask import session

class UserOperation:
    def connection(self):
    con = psycopg2.connect(os.getenv("DATABASE_URL"))
    return con

    def user_signup(self,name,email,mobile,password):
        db=self.connection()
        mycursor=db.cursor()
        sq="insert into "user" (name,email,mobile,password) values(%s,%s,%s,%s)"
        record=[name,email,mobile,password]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return  
    
    def user_login(self,email,password):
        db=self.connection()
        mycursor=db.cursor()
        sq="select name,email from "user" where email=%s and password=%s"
        record=[email,password]
        mycursor.execute(sq,record)
        row = mycursor.fetchall()
        # count = mycursor.rowcount  #number of record
        mycursor.close()
        db.close()
        return row
    
    def user_profile(self):
        db=self.connection()
        mycursor=db.cursor()
        sq="select name,email,mobile from "user" where email=%s"
        record=[session['email']]
        mycursor.execute(sq,record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def user_profile_update(self,name,mobile):
        db=self.connection()
        mycursor=db.cursor()
        sq="update "user" set name=%s,mobile=%s where email=%s"
        record=[name,mobile,session['email']]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return  

    def user_delete(self):
        db=self.connection()
        mycursor=db.cursor()
        sq="delete from "user" where email=%s"
        record=[session['email']]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return 

        #________password cahnge_________

    # def user_camp_explore(self,city):          
        # dp=self.connection()
        # mycursor=db.cursor()
        # sq="select path,campName,location,startDate,endDate,charges,c.campID from camp c,camp_photo cp where c.campID=cp.campID and city=%s"   
        # record=[campID]
        # mycursor.execute(sq,record)
        # record = mycursor.fetchall()
        # mycursor.close()
        # db.close()
        # return record    


    def booking(self,name,email,contact,service,address,landmark):
        db=self.connection()
        mycursor=db.cursor()
        sq="insert into booking (name,email,contact,service,address,landmark) values(%s,%s,%s,%s,%s,%s)"
        record=[name,email,contact,service,address,landmark]
        mycursor.execute(sq,record)
        db.commit()
        mycursor.close()
        db.close()
        return         
