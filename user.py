import os
import psycopg2
from flask import session


class UserOperation:

    def connection(self):
        con = psycopg2.connect(os.getenv("DATABASE_URL"))
        return con

    def user_signup(self, name, email, mobile, password):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'INSERT INTO "user" (name, email, mobile, password) VALUES (%s, %s, %s, %s)'
        record = [name, email, mobile, password]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def user_login(self, email, password):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT name, email FROM "user" WHERE email=%s AND password=%s'
        record = [email, password]

        mycursor.execute(sq, record)
        row = mycursor.fetchall()

        mycursor.close()
        db.close()

        return row

    def user_profile(self):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'SELECT name, email, mobile FROM "user" WHERE email=%s'
        record = [session["email"]]

        mycursor.execute(sq, record)
        record = mycursor.fetchall()

        mycursor.close()
        db.close()

        return record

    def user_profile_update(self, name, mobile):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'UPDATE "user" SET name=%s, mobile=%s WHERE email=%s'
        record = [name, mobile, session["email"]]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def user_delete(self):
        db = self.connection()
        mycursor = db.cursor()

        sq = 'DELETE FROM "user" WHERE email=%s'
        record = [session["email"]]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()

    def booking(self, name, email, contact, service, address, landmark):
        db = self.connection()
        mycursor = db.cursor()

        sq = "INSERT INTO booking (name, email, contact, service, address, landmark) VALUES (%s, %s, %s, %s, %s, %s)"
        record = [name, email, contact, service, address, landmark]

        mycursor.execute(sq, record)
        db.commit()

        mycursor.close()
        db.close()
