import sqlite3
from flask import session
from db import get_connection


class UserOperation:

    def user_signup(self, name, email, mobile, password):
        db = get_connection()
        mycursor = db.cursor()
        sq = "insert into user (name,email,mobile,password) values(?,?,?,?)"
        record = [name, email, mobile, password]
        try:
            mycursor.execute(sq, record)
            db.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            mycursor.close()
            db.close()

    def user_login(self, email):
        db = get_connection()
        mycursor = db.cursor()
        sq = "select name,email,password from user where email=?"
        record = [email]
        mycursor.execute(sq, record)
        row = mycursor.fetchall()
        mycursor.close()
        db.close()
        return row

    def user_profile(self):
        db = get_connection()
        mycursor = db.cursor()
        sq = "select name,email,mobile from user where email=?"
        record = [session['email']]
        mycursor.execute(sq, record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def user_profile_update(self, name, mobile):
        db = get_connection()
        mycursor = db.cursor()
        sq = "update user set name=?,mobile=? where email=?"
        record = [name, mobile, session['email']]
        mycursor.execute(sq, record)
        db.commit()
        mycursor.close()
        db.close()
        return

    def user_delete(self):
        db = get_connection()
        mycursor = db.cursor()
        sq = "delete from user where email=?"
        record = [session['email']]
        mycursor.execute(sq, record)
        db.commit()
        mycursor.close()
        db.close()
        return

    def booking(self, name, email, contact, service, address, landmark):
        db = get_connection()
        mycursor = db.cursor()
        sq = "insert into booking (name,email,contact,service,address,landmark,status) values(?,?,?,?,?,?,'Pending')"
        record = [name, email, contact, service, address, landmark]
        mycursor.execute(sq, record)
        db.commit()
        mycursor.close()
        db.close()
        return

    def user_reset_password(self, email, mobile, new_password):
        db = get_connection()
        mycursor = db.cursor()
        # verify email+mobile match an existing account before allowing reset
        sq = "select id from user where email=? and mobile=?"
        mycursor.execute(sq, [email, mobile])
        row = mycursor.fetchall()
        if not row:
            mycursor.close()
            db.close()
            return False

        sq = "update user set password=? where email=?"
        mycursor.execute(sq, [new_password, email])
        db.commit()
        mycursor.close()
        db.close()
        return True

    def view_bookings(self):
        db = get_connection()
        mycursor = db.cursor()
        sq = "select id,name,email,contact,service,address,landmark,status,created_at from booking order by id desc"
        mycursor.execute(sq)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def user_bookings(self):
        db = get_connection()
        mycursor = db.cursor()
        sq = "select id,service,address,landmark,contact,status,created_at from booking where email=? order by id desc"
        record = [session['email']]
        mycursor.execute(sq, record)
        record = mycursor.fetchall()
        mycursor.close()
        db.close()
        return record

    def cancel_booking(self, booking_id):
        db = get_connection()
        mycursor = db.cursor()
        # ownership check baked in: only the logged-in user's own bookings can be cancelled,
        # and only while still Pending (can't cancel something already accepted/completed)
        sq = "delete from booking where id=? and email=? and status='Pending'"
        record = [booking_id, session['email']]
        mycursor.execute(sq, record)
        db.commit()
        deleted = mycursor.rowcount > 0
        mycursor.close()
        db.close()
        return deleted

    def update_booking_status(self, booking_id, status):
        db = get_connection()
        mycursor = db.cursor()
        sq = "update booking set status=? where id=?"
        mycursor.execute(sq, [status, booking_id])
        db.commit()
        mycursor.close()
        db.close()
        return
