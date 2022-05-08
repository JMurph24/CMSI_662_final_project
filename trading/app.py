from flask import Flask, request, make_response, redirect, render_template, g, abort
from user_service import get_user_with_credentials, logged_in
from account_service import get_balance, do_transfer
from flask_wtf.csrf import CSRFProtect

#Initializing app using Python Flask and protecting it using CSRF
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Clarissa got an award at GDC'
csrf = CSRFProtect(app)

#Sends users to the login page for authentication and authorization
@app.route("/", methods=['GET'])
def home():
    if not logged_in():
        return render_template("login.html")
    return redirect('/dashboard')

#User going through authentication process on login page
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    user = get_user_with_credentials(email, password)
    
    #Gives user error message that credentials are invalid
    if not user:
        return render_template("login.html", error="Invalid credentials")
    response = make_response(redirect("/dashboard"))
    response.set_cookie("auth_token", user["token"])
    return response, 303

#The logout page
@app.route("/logout", methods=['GET'])
def logout():
    response = make_response(redirect("/dashboard"))
    response.delete_cookie('auth_token')
    return response, 303

#Display the dashboard of authenticated user's bank account
@app.route("/dashboard", methods=['GET'])
def dashboard():
    if not logged_in():
        return render_template("login.html")
    return render_template("dashboard.html", email=g.user)

#Displays the details of the user's account such as account number, balance, and user's name
@app.route("/details", methods=['GET', 'POST'])
def details():
    if not logged_in():
        return render_template("login.html")
    account_number = request.args['account']
    return render_template(
        "details.html",
        user=g.user,
        account_number=account_number,
        balance=get_balance(account_number, g.user))

#Displays transfer page to the authenticated user
@app.route("/transfer", methods=["GET"])
def transfer_page():
    if not logged_in():
        return render_template("login.html")
    return render_template("transfer.html")

#On the transfer page the source of transfer will be diplayed along with the account the 
#transfer will be placed.
@app.route("/transfer", methods=["POST"])
def transfer():
    if not logged_in():
        return render_template("login.html")
    source = request.form.get("from")
    target = request.form.get("to")
    amount = int(request.form.get("amount"))
    
    #The range of money that can be trasnfered is $1 - $999
    if amount < 0:
        abort(400, "NO STEALING")
    if amount > 1000:
        abort(400, "WOAH THERE TAKE IT EASY")
    
    #It gets the balance of the user and checks if the user has a minimum balance to transfer the amount of money requested
    available_balance = get_balance(source, g.user)
    if available_balance is None:
        abort(404, "Account not found")
    if amount > available_balance:
        abort(400, "You don't have that much")
    
    #Redirects the user to the transfer page
    if do_transfer(source, target, amount):
        redirect("/transfer")
    else:
        abort(400, "Something bad happened")

    response = make_response(redirect("/dashboard"))
    return response, 303
