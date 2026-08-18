import os
import psycopg2
from flask import session


class OrgOperation:

    def connection(self):
        con = psycopg2.connect(os.getenv("DATABASE_URL"))
        return con

    def admin_signup(self, name, email, mobile, city, password):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'INSERT INTO admin (name, email, mobile, city, password) VALUES (%s, %s, %s, %s, %s)'
        record = [name, email, mobile, city, password]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def admin_login(self, email, password):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT name, email FROM admin WHERE email=%s AND password=%s'
        record = [email, password]

        mycursor.execute(sq, record)
        row = mycursor.fetchall()

        mycursor.close()
        db.close()

        return row

    def admin_profile(self):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT name, email, mobile, city FROM admin WHERE email=%s'
        record = [session['admin_email']]

        mycursor.execute(sq, record)
        record = mycursor.fetchall()

        mycursor.close()
        db.close()

        return record

    def admin_profile_update(self, name, mobile, city):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'UPDATE admin SET name=%s, mobile=%s, city=%s WHERE email=%s'
        record = [name, mobile, city, session['admin_email']]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def org_delete(self):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'DELETE FROM admin WHERE email=%s'
        record = [session['org_email']]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def org_change_password(self, oldPassword, newPassword):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT * FROM admin WHERE email=%s AND password=%s'
        record = [session['org_email'], oldPassword]

        mycursor.execute(sq, record)
        row = mycursor.fetchall()

        if len(row) == 0:
            mycursor.close()
            db.close()
            return 0

        sq = 'UPDATE admin SET password=%s WHERE email=%s'
        record = [newPassword, session['org_email']]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

        return 1

    def org_new_camp(self, campName, contact, city, location, startDate, endDate, charges, descp):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'INSERT INTO camp (orgEmail, campName, contact, city, location, startDate, endDate, charges, descp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'
        record = [
            session['org_email'],
            campName,
            contact,
            city,
            location,
            startDate,
            endDate,
            charges,
            descp
        ]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def org_view_camp(self):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT campID, campName, city, location, charges FROM camp WHERE orgEmail=%s'
        record = [session['org_email']]

        mycursor.execute(sq, record)
        record = mycursor.fetchall()

        mycursor.close()
        db.close()

        return record

    def org_camp_delete(self, campID):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'DELETE FROM camp WHERE campID=%s'
        mycursor.execute(sq, [campID])
        db.commit()

        mycursor.close()
        db.close()

    def org_camp_detail(self, campID):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT campName, contact, city, location, startDate, endDate, charges, descp, campID FROM camp WHERE campID=%s'
        mycursor.execute(sq, [campID])
        record = mycursor.fetchall()

        mycursor.close()
        db.close()

        return record

    def org_camp_edit(self, campID, campName, contact, city, location, startDate, endDate, charges, descp):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'UPDATE camp SET campName=%s, contact=%s, city=%s, location=%s, startDate=%s, endDate=%s, charges=%s, descp=%s WHERE campID=%s'
        record = [
            campName,
            contact,
            city,
            location,
            startDate,
            endDate,
            charges,
            descp,
            campID
        ]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def org_camp_photo(self, campID, path):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'INSERT INTO camp_photo (campID, path) VALUES (%s, %s)'
        mycursor.execute(sq, [campID, path])
        db.commit()

        mycursor.close()
        db.close()

    def org_camp_photo_view(self, campID):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT path FROM camp_photo WHERE campID=%s'
        mycursor.execute(sq, [campID])
        record = mycursor.fetchall()

        mycursor.close()
        db.close()

        return record
