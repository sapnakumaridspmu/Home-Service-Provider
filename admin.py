import sqlite3
from flask import session
from db import get_connection


class OrgOperation:

    def admin_signup(self, name, email, mobile, city, password):
        db = get_connection()
        mycursor = db.cursor()
        sq = "insert into admin(name,email,mobile,city,password) values(?,?,?,?,?)"
        record = [name, email, mobile, city, password]
        try:
            mycursor.execute(sq, record)
            db.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            mycursor.close()
            db.close()

    def admin_login(self, email):
        db = get_connection()
        mycursor = db.cursor()
        sq = "select name,email,password from admin where email=?"
        record = [email]
        mycursor.execute(sq, record)
        row = mycursor.fetchall()
        mycursor.close()
        db.close()
        return row

    def admin_profile(self):
        db = get_connection()
        mycursor = db.cursor()
        sq = "select name,email,mobile,city from admin where email=?"
        record = [session['admin_email']]
        mycursor.execute(sq, record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def admin_profile_update(self, name, mobile, city):
        db = get_connection()
        mycursor = db.cursor()
        sq = "update admin set name=?,mobile=?,city=? where email=?"
        record = [name, mobile, city, session['admin_email']]
        mycursor.execute(sq, record)
        db.commit()
        mycursor.close()
        db.close()
        return

    def admin_reset_password(self, email, mobile, new_password):
        db = get_connection()
        mycursor = db.cursor()
        # verify email+mobile match an existing account before allowing reset
        sq = "select id from admin where email=? and mobile=?"
        mycursor.execute(sq, [email, mobile])
        row = mycursor.fetchall()
        if not row:
            mycursor.close()
            db.close()
            return False

        sq = "update admin set password=? where email=?"
        mycursor.execute(sq, [new_password, email])
        db.commit()
        mycursor.close()
        db.close()
        return True

    def admin_delete(self):
        db = get_connection()
        mycursor = db.cursor()
        sq = "delete from admin where email=?"
        record = [session['admin_email']]
        mycursor.execute(sq, record)
        db.commit()
        mycursor.close()
        db.close()
        return
