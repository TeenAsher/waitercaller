from flask import Flask
from flask import render_template, request, redirect
from flask import url_for
from flask_login import LoginManager
from flask_login import login_required
from flask_login import login_user, logout_user, current_user
from dbhelper import DBHelper
from forms import RegistrationForm, LoginForm, TableCreateForm
from passwordhelper import PasswordHelper
from user import User
import config
import datetime

app = Flask(__name__)
app.secret_key = 'jcSYB98hc+aKSP7UmH5SW9+uwkB8DCU3WIO+QE5WI3kan+UWI2Z'
login_manager = LoginManager(app)
DB = DBHelper()
PH = PasswordHelper()

@app.route('/')
def home():
    return render_template('home.html', loginform=LoginForm(), registrationform=RegistrationForm())

@app.route('/dashboard')
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = '{}.{}'.format((deltaseconds/60), str(deltaseconds % 60).zfill(2))
    return render_template('dashboard.html', requests=requests)

@app.route('/account')
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    return render_template('account.html', createtableform=TableCreateForm(), tables=tables)

@app.route('/login', methods=['POST'])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(stored_user['password'], form.loginpassword.data):
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append('Email or password invalid')
    return render_template('home.html', loginform=form, registrationform=RegistrationForm())

@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Email address already registered")
            return render_template('home.html', loginform=LoginForm(), registrationform=form)
        password = PH.get_hash(form.password2.data)
        DB.add_user(form.email.data, password)
        return render_template("home.html", loginform=LoginForm(), registrationform=form, onloadmessage="Registration successful. Please log in.")
    return render_template('home.html', loginform=LoginForm(), registrationform=form)

@app.route('/account/createtable', methods=['POST'])
@login_required
def account_createtable():
    form = TableCreateForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        new_url = config.base_url + 'newrequest/' + str(tableid)
        DB.update_table(tableid, new_url)
        return redirect(url_for('account'))
    return render_template('account.html', createtableform=form, tables=DB.get_tables(current_user.get_id()))

@app.route('/account/deletetable')
@login_required
def account_deletetable():
    tableid = request.args.get('tableid')
    DB.delete_table(tableid)
    return redirect(url_for('account'))

@app.route('/newrequest/<tid>')
def new_request(tid):
    DB.add_request(tid, datetime.datetime.now())
    return 'Your request has been logged. The waiter will be with you shortly'

@app.route('/dashboard/resolve')
@login_required
def dashboard_resolve():
    request_id = request.args.get('request_id')
    DB.delete_request(request_id)
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(port=5000, debug=True)