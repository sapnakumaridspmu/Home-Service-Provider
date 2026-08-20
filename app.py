import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from user import UserOperation
from encryption import Encryption
from validation import Validation
from admin import OrgOperation
from db import init_db

app = Flask(__name__)
# Fall back to a default so sessions/flash still work if SECRET_KEY isn't set
# (Render deployment should set a real SECRET_KEY env var).
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

init_db()  # create tables on startup if they don't exist yet

userObj = UserOperation()
encryptObj = Encryption()
validObj = Validation()
orgObj = OrgOperation()

SERVICE_PAGES = {
    'card1': 'card1.html',
    'card2': 'card2.html',
    'card3': 'card3.html',
    'card4': 'card4.html',
    'card5': 'card5.html',
    'card6': 'card6.html',
    'card7': 'card7.html',
    'card8': 'card8.html',
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'GET':
        return render_template('user_signup.html')
    else:
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']

        # -------------validation--------------------
        frmList = [name, email, mobile, password]
        if (validObj.empty(frmList)):
            flash("field can't be empty!!")
            return redirect(url_for('user_signup'))

        if (validObj.checkAlpha(name)):
            flash("Name must be in alphabates!!")
            return redirect(url_for('user_signup'))

        if (validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('user_signup'))

        password = encryptObj.convert(password)  # encryption

        created = userObj.user_signup(name, email, mobile, password)
        if not created:
            flash("This email is already registered. Please login instead.")
            return redirect(url_for('user_signup'))

        flash("Successfully Registered!! Login Now!!")
        return redirect(url_for('user_login'))


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    else:
        email = request.form['email']
        password = request.form['password']

        row = userObj.user_login(email)
        if (row and encryptObj.verify(password, row[0][2])):
            session['name'] = row[0][0]
            session['email'] = row[0][1]
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


@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if 'email' in session:
        if request.method == 'GET':
            record = userObj.user_profile()
            bookings = userObj.user_bookings()
            return render_template('user_profile.html', record=record, bookings=bookings)
        else:
            name = request.form['name']
            mobile = request.form['mobile']
            # -------------validation--------------------
            frmList = [name, mobile]
            if (validObj.empty(frmList)):
                flash("field can't be empty!!")
                return redirect(url_for('user_profile'))

            if (validObj.checkAlpha(name)):
                flash("Name must be in alphabates!!")
                return redirect(url_for('user_profile'))

            if (validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
                flash("Mobile must be a number with length of 10 digits!!")
                return redirect(url_for('user_profile'))
            # -------- end validation------------------------
            userObj.user_profile_update(name, mobile)
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
# Service info pages (card1..card8), one per service on the homepage.
@app.route('/<any(card1,card2,card3,card4,card5,card6,card7,card8):card_id>')
def service_card(card_id):
    if 'email' in session:
        return render_template(SERVICE_PAGES[card_id])
    else:
        flash("please login to access this page..")
        return redirect(url_for('user_login'))


# ----------------------------------------------------------

@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'email' in session:
        if request.method == 'GET':
            return render_template('booking.html')
        else:
            name = request.form['name']
            email = request.form['email']
            contact = request.form['contact']
            service = request.form['service']
            address = request.form['address']
            landmark = request.form['landmark']

            userObj.booking(name, email, contact, service, address, landmark)
            flash("your Booking has successfully completed!!")
            return redirect(url_for('booking'))
    else:
        flash("Please login to access this page..")
        return redirect(url_for('user_login'))


@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'GET':
        return render_template('forget_password.html')
    else:
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # -------------validation--------------------
        frmList = [email, mobile, password, confirm_password]
        if (validObj.empty(frmList)):
            flash("field can't be empty!!")
            return redirect(url_for('forget_password'))

        if (validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('forget_password'))

        if password != confirm_password:
            flash("Passwords do not match!!")
            return redirect(url_for('forget_password'))

        password = encryptObj.convert(password)  # encryption

        updated = userObj.user_reset_password(email, mobile, password)
        if not updated:
            flash("No account found with that email and mobile number.")
            return redirect(url_for('forget_password'))

        flash("Password reset successfully!! Login Now!!")
        return redirect(url_for('user_login'))


@app.route('/admin_forget_password', methods=['GET', 'POST'])
def admin_forget_password():
    if request.method == 'GET':
        return render_template('admin_forget_password.html')
    else:
        email = request.form['email']
        mobile = request.form['mobile']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # -------------validation--------------------
        frmList = [email, mobile, password, confirm_password]
        if (validObj.empty(frmList)):
            flash("field can't be empty!!")
            return redirect(url_for('admin_forget_password'))

        if (validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('admin_forget_password'))

        if password != confirm_password:
            flash("Passwords do not match!!")
            return redirect(url_for('admin_forget_password'))

        password = encryptObj.convert(password)  # encryption

        updated = orgObj.admin_reset_password(email, mobile, password)
        if not updated:
            flash("No account found with that email and mobile number.")
            return redirect(url_for('admin_forget_password'))

        flash("Password reset successfully!! Login Now!!")
        return redirect(url_for('admin_login'))


@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'GET':
        return render_template('admin_signup.html')
    else:
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        city = request.form['city']
        password = request.form['password']

        # -------------validation--------------------
        frmList = [name, email, mobile, city, password]
        if (validObj.empty(frmList)):
            flash("field can't be empty!!")
            return redirect(url_for('admin_signup'))

        if (validObj.checkAlpha(name)):
            flash("Name must be in alphabates!!")
            return redirect(url_for('admin_signup'))

        if (validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
            flash("Mobile must be a number with length of 10 digits!!")
            return redirect(url_for('admin_signup'))

        password = encryptObj.convert(password)  # encryption

        created = orgObj.admin_signup(name, email, mobile, city, password)
        if not created:
            flash("This email is already registered. Please login instead.")
            return redirect(url_for('admin_signup'))

        flash("Successfully Registered!! Login Now!!")
        return redirect(url_for('admin_login'))


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    else:
        email = request.form['email']
        password = request.form['password']
        # -------------validation--------------------
        row = orgObj.admin_login(email)
        if (row and encryptObj.verify(password, row[0][2])):
            session['admin_name'] = row[0][0]
            session['admin_email'] = row[0][1]
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


@app.route('/admin_profile', methods=['GET', 'POST'])
def admin_profile():
    if 'admin_email' in session:
        if request.method == 'GET':
            record = orgObj.admin_profile()
            return render_template('admin_profile.html', record=record)
        else:
            name = request.form['name']
            mobile = request.form['mobile']
            city = request.form['city']
            # -------------validation--------------------
            frmList = [name, mobile, city]
            if (validObj.empty(frmList)):
                flash("field can't be empty!!")
                return redirect(url_for('admin_profile'))

            if (validObj.checkAlpha(name)):
                flash("Name must be in alphabates!!")
                return redirect(url_for('admin_profile'))

            if (validObj.checkDigit(mobile) or validObj.checkMobileLength(mobile)):
                flash("Mobile must be a number with length of 10 digits!!")
                return redirect(url_for('admin_profile'))
            # -------- end validation------------------------
            orgObj.admin_profile_update(name, mobile, city)
            flash("your profile is updated successfully!!")
            return redirect(url_for('admin_profile'))
    else:
        flash("please login to access this page..")
        return redirect(url_for('admin_login'))


@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'email' in session:
        cancelled = userObj.cancel_booking(booking_id)
        if cancelled:
            flash("Your booking has been cancelled.")
        else:
            flash("Could not cancel this booking (it may already be accepted/completed).")
        return redirect(url_for('user_profile'))
    else:
        flash("please login to access this page..")
        return redirect(url_for('user_login'))


@app.route('/update_booking_status/<int:booking_id>', methods=['POST'])
def update_booking_status(booking_id):
    if 'admin_email' in session:
        status = request.form['status']
        if status not in ('Pending', 'Accepted', 'Completed', 'Cancelled'):
            flash("Invalid status.")
            return redirect(url_for('view_booking'))

        userObj.update_booking_status(booking_id, status)
        flash("Booking status updated.")
        return redirect(url_for('view_booking'))
    else:
        flash("please login to access this page..")
        return redirect(url_for('admin_login'))


@app.route('/view_booking')
def view_booking():
    if 'admin_email' in session:
        records = userObj.view_bookings()
        return render_template('view_booking.html', records=records)
    else:
        flash("please login to access this page..")
        return redirect(url_for('admin_login'))


@app.route('/about')
def about():
    return render_template('about_us.html')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug)
