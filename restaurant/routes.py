from restaurant import app
from flask import render_template, redirect, url_for, flash, request
from restaurant.models import Table, User, Item, Order
from restaurant.forms import RegisterForm, LoginForm, OrderIDForm, ReserveForm, AddForm, OrderForm
from restaurant import db, app
from flask_login import login_user, logout_user, login_required, current_user


@app.route('/')
#HOME PAGE
@app.route('/home')
def home_page(): 
    return render_template('index.html')

#MENU PAGE
@app.route('/menu', methods = ['GET', 'POST']) #type: ignore
@login_required
def menu_page():
    add_form = AddForm()
    if request.method == 'POST':
        selected_item = request.form.get('selected_item') #get the selected item from the menu page
        s_item_object = Item.query.filter_by(name = selected_item).first()
        if s_item_object:
            s_item_object.assign_ownership(current_user) #assign ownership of the ordered item to the user
        flash(f"Your order for { s_item_object.name } has been added to cart successfully!", category = 'success')
        return redirect(url_for('menu_page'))
    
    if request.method == 'GET':
        items = Item.query.all()
        return render_template('menu.html', items = items, add_form = add_form)

#CART PAGE
@app.route('/delete_cart_item', methods = ['POST']) #type: ignore
def delete_cart_item():
    if request.method == 'POST':
        ordered_item = request.form.get('ordered_item1')
        o_item_object = Item.query.filter_by(name = ordered_item).first()
        o_item_object.remove_ownership(current_user)
        Order.query.filter_by(name = current_user.fullname).delete() #type: ignore
        flash(f"Your order for { o_item_object.name } has been removed from cart successfully!", category = 'success')
    return redirect(url_for('cart_page'))
        
@app.route('/cart', methods = ['GET', 'POST']) #type: ignore
def cart_page():
    order_form = OrderForm()
    if request.method == 'POST':
        totalcounts = int(request.form.get('totalcounts')) #type: ignore
        for i in range(1,totalcounts+1):
            ordered_item = request.form.get('ordered_item'+str(i)) #get the ordered item(s) from the cart page
            o_item_object = Item.query.filter_by(name = ordered_item).first()
            order_info = Order(name = current_user.fullname, #type: ignore
                            address = current_user.address, #type: ignore
                            order_items = o_item_object.name,count=int(request.form.get(ordered_item+"count"))) #type: ignore
            db.session.add(order_info)
            db.session.commit()

            o_item_object.remove_ownership(current_user)    
        #return congrats page on successfull order
        return redirect(url_for('congrats_page'))
    if request.method == 'GET':
        selected_items = Item.query.filter_by(orderer = current_user.id) #type: ignore
        return render_template('cart.html', order_form = order_form, selected_items = selected_items)

#CONGRATULATIONS PAGE
@app.route('/congrats')
def congrats_page():
    return render_template('congrats.html')   

#TABLE RESERVATION PAGE
@app.route('/table', methods = ['GET', 'POST']) #type: ignore
@login_required
def table_page():
    reserve_form = ReserveForm()
    #to get rid of 'confirm form resubmission' on refresh
    if request.method == 'POST':
        reserved_table = request.form.get('reserved_table')
        r_table_object = Table.query.filter_by(table = reserved_table).first()
        if r_table_object:
            r_table_object.assign_ownership(current_user) #set the owner of the table to the current logged in user
            flash(f"Your table {{ r_table_object.table }} has been reserved successfully!", category = 'success')

        return redirect(url_for('table_page'))

    if request.method == 'GET':
        tables = Table.query.filter_by(reservee = None)
        return render_template('table.html', tables = tables, reserve_form = reserve_form)

#LOGIN PAGE
@app.route('/login', methods = ['GET', 'POST'])
def login_page():
    forml = LoginForm()
    form = RegisterForm()
    if forml.validate_on_submit():
        attempted_user = User.query.filter_by(username = forml.username.data).first() #get username data entered from sign in form
        if attempted_user and attempted_user.check_password_correction(attempted_password = forml.password.data): #to check if username & password entered is in user database
            login_user(attempted_user) #checks if user is registered 
            flash(f'Signed in successfully as: {attempted_user.username}', category = 'success')
            return redirect(url_for('home_page'))
        else:
            flash('Username or password is incorrect! Please Try Again', category = 'danger') #displayed in case user is not registered
    return render_template('login.html', forml = forml, form = form)

def return_login():
    return render_template("login.html")


#LOGOUT FUNCTIONALITY
@app.route('/logout')
def logout():
    logout_user() #used to log out
    flash('You have been logged out!', category = 'error')
    return redirect(url_for("home_page")) 

#REGISTER PAGE
@app.route('/register', methods = ['GET', 'POST'])
def register_page():
    forml = LoginForm()
    form = RegisterForm() 
    #checks if form is valid
    if form.validate_on_submit():
         user_to_create = User(username = form.username.data,
                               fullname = form.fullname.data,
                               address = form.address.data,
                               phone_number = form.phone_number.data,
                               password = form.password1.data,)
         db.session.add(user_to_create)
         db.session.commit()
         login_user(user_to_create) #login the user on registration 
         return redirect(location=url_for('home_page'))
    else:
        flash("Username already exists!",category = 'warning')

    if form.errors != {}: #if there are not errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user: {err_msg}', category = 'error')
    return render_template('login.html', form = form, forml = forml)

#ORDER ID PAGE
@app.route('/order_id', methods = ['GET', 'POST'])
def track_page():
    orderid = OrderIDForm()
    # if request.method == "POST":
    if orderid.validate_on_submit:
        #check to see if order id matches
        valid_orderid = Order.query.filter_by( order_id = orderid.orderid.data ).first()
        if valid_orderid:
            return redirect(url_for('delivery'))
        else:
            flash('Your Order-ID is invalid! Please Try Again.', category = 'danger')

    return render_template('order-id.html', orderid = orderid)

@app.route('/countupdate', methods=['POST']) #type: ignore 
def countupdate():
    name = request.form.get('dish_item')
    count = request.form.get('count')
    
    flash('Item Count Updated successfully', category='success')
    return redirect(location=url_for('cart_page'))
    