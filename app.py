from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory,flash
from pymongo import MongoClient
from werkzeug.utils import secure_filename
from flask_bcrypt import Bcrypt
from flask import jsonify
from bson.objectid import ObjectId
from pymongo import DESCENDING
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import pickle


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ensure you use a strong key for security
bcrypt = Bcrypt(app)


# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["user_database"]
users_collection = db["users"]
products_collection = db['products']
farmers_collection = db['farmers']
admin_collection = db['admin']
cart_collection = db['cart']
payments_collection = db['payments']
farmer_orders_collection = db["farmer_orders"]



# Upload folder configuration
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



# Routes
@app.route('/')
def home():
    return render_template('index.html')
    
@app.route('/')
def fhome():
    return render_template('home.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/upload_news')
def upload_news():
    return render_template('upload_news.html')


@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/disease')
def disease():
    return render_template('disease.html')

@app.route('/back')
def back():
    return render_template('guideline.html')

@app.route('/backfarmer')
def backfarmer():
    return render_template('home.html')

# Farmer registration page
@app.route('/registerf', methods=['GET', 'POST'])
def registerf():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Check if the email already exists
        if farmers_collection.find_one({'email': email}):
            flash('Email already exists. Please log in or use another email.')
            return redirect(url_for('registerf'))

        farmer = {
            'name': name,
            'email': email,
            'password': password
        }
        farmers_collection.insert_one(farmer)
        flash('Registration successful! Please log in.')
        return redirect(url_for('loginf'))
    return render_template('registerf.html')

# Farmer login page
# Farmer login page
@app.route('/loginf', methods=['GET', 'POST'])
def loginf():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        farmer = farmers_collection.find_one({'email': email})
        if farmer and bcrypt.check_password_hash(farmer['password'], password):
            session['farmer_id'] = str(farmer['_id'])
            session['farmer_name'] = farmer['name']
            flash('Login successful!')
            
            return redirect(url_for('homes')) 
        else:
            flash('Login failed. Please check your email and password.')
    return render_template('loginf.html')

#farmer profile page
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'farmer_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('loginf'))  # Redirect to login page if not logged in

    farmer_id = session['farmer_id']
    
    # Fetch farmer data from the database
    farmer = farmers_collection.find_one({'_id': ObjectId(farmer_id)})

    if not farmer:
        flash('Farmer not found!')
        return redirect(url_for('loginf'))

    if request.method == 'POST':
        # Update farmer profile with the form data
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        address = request.form['address']
        place = request.form['place']
        pin = request.form['pin']
        district = request.form['district']
        state = request.form['state']

        # Updating the database with new values
        farmers_collection.update_one(
            {'_id': ObjectId(farmer_id)},
            {'$set': {
                'name': name,
                'email': email,
                'contact': contact,
                'address': address,
                'place': place,
                'pin': pin,
                'district': district,
                'state': state
            }}
        )
        flash('Profile updated successfully!')

        # Redirect to home page after profile update
        return redirect(url_for('profile'))

    # Pass farmer data to the template for profile viewing and editing
    return render_template('profile.html', farmer=farmer)


# Home page route (after profile update)
@app.route('/homes')
def homes():
    if 'farmer_id' not in session:
        return redirect(url_for('loginf'))  # If not logged in, redirect to login page
    return render_template('home.html')


# Admin login page
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        if username == "admin" and password == "Admin@12" :
            flash('Login successful!')
            return render_template('admin.html')  # Redirect to admin dashboard
        else:
            flash('Login failed. Please check your username and password.')
    
    return render_template('admin_login.html')



# Route to upload product page (Requires farmer to be logged in)
@app.route('/upload_product', methods=['GET', 'POST'])
def upload_product():
    if 'farmer_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('loginf'))

    if request.method == 'POST':
        category = request.form['category']
        product_name = request.form['product_name']
        price = request.form['price']
        description = request.form['description']
        image = request.files['image']
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        product = {
            'farmer_id': session['farmer_id'],
            'category': category,
            'name': product_name,
            'price' : price,
            'description': description,
            'image': filename,
            'sold': False
        }
        products_collection.insert_one(product)
        return redirect(url_for('view_products'))
    return render_template('upload_product.html')

# Route to view products page
@app.route('/products')
def view_products():
    if 'farmer_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    farmer_id = session['farmer_id']
    products = products_collection.find({'farmer_id': farmer_id})
    return render_template('products.html', products=products)

# Route to edit product details
@app.route('/edit_product/<product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    if 'farmer_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if request.method == 'POST':
        products_collection.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {
                'name': request.form['product_name'],
                'price': request.form['price'],
                'description': request.form['description'],
                'category': request.form['category']
            }}
        )
        return redirect(url_for('view_products'))
    return render_template('edit_product.html', product=product)

@app.route('/delete_product/<product_id>', methods=['POST'])
def delete_product(product_id):
    if 'farmer_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('login'))

    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if product and product['farmer_id'] == session['farmer_id']:
        # Delete the product image from the server
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product['image'])
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete the product from MongoDB
        products_collection.delete_one({'_id': ObjectId(product_id)})
        flash('Product deleted successfully.')
    else:
        flash('Unauthorized action.')

    return redirect(url_for('view_products'))

# Route to farmer profile page
@app.route('/profiles', methods=['GET', 'POST'])
def profiles():
    if 'farmer_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('loginf'))

    farmer_id = session['farmer_id']
    farmer = farmers_collection.find_one({'_id': ObjectId(farmer_id)})
    if request.method == 'POST':
        farmers_collection.update_one(
            {'_id': ObjectId(farmer_id)},
            {'$set': {
                'name': request.form['name'],
                'email': request.form['email']
            }}
        )
        return redirect(url_for('profile'))
    return render_template('profile.html', farmer=farmer)


# Route to view payments page
@app.route('/payments')
def payments():
    if 'farmer_id' not in session:
        flash('Please log in as a farmer to continue.', 'error')
        return redirect(url_for('farmer_login'))

    farmer_id = session['farmer_id']
    
    # Fetch only orders that belong to the farmer
    orders = list(payments_collection.find({"farmer_id": farmer_id}))

    for order in orders:
        order['_id'] = str(order['_id'])  # Convert ObjectId to string

    return render_template("payments.html", orders=orders)


# Route to sign out
@app.route('/signout')
def signout():
    session.pop('farmer_id', None)
    flash('You have been signed out.')
    return redirect(url_for('home'))

@app.route('/guideline', methods=['GET', 'POST'])
def guideline():
    suitable_crop_steps = []  # Initialize as empty list to avoid UnboundLocalError
    suitable_crop_names = []  # Initialize as empty list to avoid UnboundLocalError
    error_message = None
    crops = db.guideline.find()  # Retrieve all crops from MongoDB by default

    if request.method == 'POST':
        # Get the climate and soil_type from the form
        climate = request.form.get('climate')
        soil_type = request.form.get('soil_type')

        # Retrieve the matching crops based on climate and soil type
        matching_crops = db.guideline.find({
            "climate": climate,
            "soil_type": soil_type
        })

        # Check if any matching crops were found by converting cursor to list
        matching_crops_list = list(matching_crops)

        if len(matching_crops_list) > 0:  # Check if there are matching crops
            for crop in matching_crops_list:
                suitable_crop_steps.append(crop['steps'])
                suitable_crop_names.append(crop['crop_name'])
        else:
            error_message = "No matching crops found for the given climate and soil type."

    # Zip the names and steps together before passing to template
    zipped_crops = zip(suitable_crop_names, suitable_crop_steps)

    # Render the template with all crops, matching crops, and steps
    return render_template('guideline.html', crops=crops, zipped_crops=zipped_crops, error_message=error_message)

from flask import flash, redirect, render_template, request

# Admin route to insert crop guidelines, news, and disease solutions
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        # Get form data for crop steps
        climate = request.form.get('climate')
        soil_type = request.form.get('soil_type')
        crop_name = request.form.get('crop_name')
        steps = request.form.getlist('steps[]')
        

        # Store crop data in MongoDB if provided
        if climate and soil_type and steps and crop_name:
            db.guideline.insert_one({
                "climate": climate,
                "soil_type": soil_type,
                "crop_name": crop_name,
                "steps": steps

                
            })
            flash("Crop guideline added successfully!", "success")
        
        # Get form data for news
        heading = request.form.get('heading')
        news = request.form.get('news')
        
        # Store news in MongoDB if provided
        if heading and news:
            db.news.insert_one({
                "heading": heading,
                "news": news
            })
            flash("News added successfully!", "success")

        # Get form data for disease solution
        disease = request.form.get('disease')
        solution = request.form.get('solution')
        
        # Store disease and solution in MongoDB if provided
        if disease and solution:
            db.disease.insert_one({
                "disease": disease,
                "solution": solution
            })
            flash("Disease solution added successfully!", "success")
        
        return redirect('/admin')

    return render_template('admin.html') 



# Load the trained ML model
with open("model.pkl", "rb") as file:
    vectorizer, model = pickle.load(file)

# Function to predict the disease solution
def get_disease_solution(disease_name):
    try:
        disease_vector = vectorizer.transform([disease_name])  # Transform input
        prediction = model.predict(disease_vector)  # Get solution
        return prediction[0]  # Return the predicted solution
    except Exception as e:
        return "Error processing request. Please try again."

@app.route('/disease', methods=['GET', 'POST'])
def diseases():
    solution = None
    if request.method == 'POST':
        disease_name = request.form.get('disease')
        if disease_name:
            solution = get_disease_solution(disease_name)
        else:
            solution = "Invalid input. Please enter a disease name."
    
    return render_template('disease.html', solution=solution)

@app.route('/clear', methods=['POST'])
def clear_solution():
    return redirect('disease')

# User Registration Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

        # Check if email already exists
        if users_collection.find_one({'email': email}):
            flash('Email already registered. Please log in.')
            return redirect(url_for('user_login'))

        user = {
            'name': name,
            'email': email,
            'password': password
        }
        users_collection.insert_one(user)
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({'email': email})
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['user_name'] = user['name']
            flash('Login successful!')

            # Handle category and search filters after login
            category = request.args.get('category')
            search = request.args.get('search')

            query = {'sold': False}
            if category:
                query['category'] = category
            if search:
                query['name'] = {'$regex': search, '$options': 'i'}  # Case-insensitive search

            # Query products based on filters
            products = products_collection.find(query)
            return render_template('user_home.html', products=products)
        else:
            flash('Invalid email or password. Please try again.')
    return render_template('login.html')

@app.route('/user_home', methods=['GET'])
def user_home():
    # Handle category and search filters from the user home page
    category = request.args.get('category')
    search = request.args.get('search')

    query = {'sold': False}
    if category:
        query['category'] = category
    if search:
        query['name'] = {'$regex': search, '$options': 'i'}  # Case-insensitive search

    products = products_collection.find(query)
    return render_template('user_home.html', products=products)

@app.route('/user_hom')
def user_hom():
    user_id = session.get("user_id")  # Assuming user is logged in
    cart_count = 0

    if user_id:
        cart_count = cart_collection.count_documents({"user_id": user_id})  # Count items in cart
    
    return render_template("user_home.html", cart_count=cart_count)

@app.route('/cart_count')
def cart_count():
    user_id = session.get("user_id")
    count = 0

    if user_id:
        count = cart_collection.count_documents({"user_id": user_id})

    return {"count": count}

from flask import request, redirect, url_for
from bson.objectid import ObjectId

@app.route('/update_cart/<item_id>', methods=['POST'])
def update_cart(item_id):
    try:
        new_quantity = int(request.form.get('quantity'))

        if new_quantity > 0:
            cart_collection.update_one(
                {"_id": ObjectId(item_id)},
                {"$set": {"quantity": new_quantity}}
            )
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Invalid quantity"}), 400

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Route to handle "Buy Now" action (get product details for popup)
@app.route('/buy_now/<product_id>', methods=['GET', 'POST'])
def buy_now(product_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('user_login'))

    product = products_collection.find_one({'_id': ObjectId(product_id)})
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        # Store in the session or move to the user profile for finalization
        session['product'] = product
        session['quantity'] = quantity
        return redirect(url_for('user_profile'))
    return render_template('buy_now_popup.html', product=product)


# Route for user profile (form to fill details and continue to payment)
@app.route('/user_profile', methods=['GET', 'POST'])
def user_profile():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('user_login'))

    if request.method == 'POST':
        user_details = {
            'name': request.form['name'],
            'email': request.form['email'],
            'address': request.form['address']
        }
        session['user'] = user_details  # Store user data temporarily
        return redirect(url_for('payment'))
    return render_template('user_profile.html')

# Route to add product to cart
@app.route('/add_to_cart/<product_id>', methods=['POST'])
def add_to_cart(product_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    product = products_collection.find_one({'_id': ObjectId(product_id)})

    if not product:
        flash('Product not found.')
        return redirect(url_for('user_home'))

    
    product_price = float(product.get('price', 0))  # Default to 0 if price is missing

    existing_cart_item = cart_collection.find_one({'user_id': user_id, 'product_id': product_id})

    if existing_cart_item:
        cart_collection.update_one(
            {'_id': existing_cart_item['_id']},
            {'$inc': {'quantity': 1}}
        )
    else:
        cart_item = {
            'user_id': user_id,
            'product_id': product_id,
            'product_name': product.get('name', 'Unknown Product'),  # Handle missing name
            'image': product.get('image', 'default.jpg'),  # Handle missing image
            'quantity': 1,
            'price': product_price  # Ensure price is stored properly
        }
        cart_collection.insert_one(cart_item)

    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    cart_items = list(cart_collection.find({'user_id': user_id}))

    
    for item in cart_items:
        item['_id'] = str(item['_id'])  # Convert ObjectId to string
        item['price'] = float(item.get('price', 0))  # Default to 0 if price is missing

    subtotal = sum(item['quantity'] * item['price'] for item in cart_items)
    shipping = 5 if subtotal > 0 else 0  # Example: fixed shipping fee
    total = subtotal + shipping

    return render_template('cart.html', cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)

@app.route('/remove_from_cart/<cart_item_id>', methods=['GET'])
def remove_from_cart(cart_item_id):
    if 'user_id' not in session:
        flash('Please log in to continue.')
        return redirect(url_for('user_login'))

    try:
        cart_collection.delete_one({'_id': ObjectId(cart_item_id)})  # Convert to ObjectId
        flash('Item removed from cart.')
    except Exception as e:
        flash(f'Error removing item: {str(e)}')

    return redirect(url_for('cart'))

@app.route('/payment', methods=['GET'])
def payment():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('user_login'))

    user_id = session['user_id']

    # Fetch user details
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        flash("User not found!", "error")
        return redirect(url_for('user_login'))
    
    cart_items = list(cart_collection.find({'user_id': user_id}))
    
    subtotal = sum(item['quantity'] * item['price'] for item in cart_items)
    shipping = 5 if subtotal > 0 else 0
    total = subtotal + shipping
    
    return render_template("payment.html",user=user,cart_items=cart_items, subtotal=subtotal, shipping=shipping, total=total)


@app.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        flash("User profile not found!", "error")
        return redirect(url_for("user_login"))
    
    # Get order details from form
    address = request.form.get("address") or user.get("address", "")
    phoneno = request.form.get("phoneno") or user.get("phoneno", "") 
    payment_method = request.form.get("payment_method") 

    if not address or not phoneno or not payment_method:
        flash("All fields are required!", "error")
        return redirect(url_for("payment"))

    cart_items = list(cart_collection.find({'user_id': user_id}))

    if not cart_items:
        flash("Your cart is empty!", "error")
        return redirect(url_for("cart"))

    subtotal = sum(item['quantity'] * item['price'] for item in cart_items)
    shipping = 5 if subtotal > 0 else 0
    total = subtotal + shipping

    order_items = []

    for item in cart_items:
        product_id = str(item["_id"])
        product_name = item["product_name"]
        quantity = item["quantity"]
        price = item["price"]

        order_item = {
            "product_id": product_id,
            "product_name": product_name,
            "quantity": quantity,
            "price": price
        }

        order_items.append(order_item)

    # Save order in the main payments collection
    order_data = {
        "user_id": user_id,
        "username": user.get("username", "Unknown"),
        "product_name" : product_name,
        "items": order_items,
        "subtotal": subtotal,
        "shipping": shipping,
        "total": total,
        "payment_method": payment_method,
        "address": address,
        "phoneno": phoneno,
        "quantity": quantity,
        "status": "Order Placed Successfully",
        "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Insert into the payments collection
    payments_collection.insert_one(order_data)

    # Insert order in farmer_orders_collection (accessible to all farmers)
    farmer_orders_collection.insert_one(order_data)
    
    # Clear the user's cart after successful order placement
    cart_collection.delete_many({'user_id': user_id})

    # Update user profile with address and phone number if missing
    if not user.get("address") or not user.get("phoneno"):
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"address": address, "phoneno": phoneno}}
        ) 

    flash("Payment processed successfully!", "success")
    return redirect(url_for("user_home"))

@app.route('/use_profile')
def use_profile():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('user_login'))
    
    user_id = session['user_id']
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        flash("User not found!", "error")
        return redirect(url_for('user_login'))

    # Ensure order_date is stored as a valid datetime in MongoDB
    orders = list(payments_collection.find({"user_id": user_id}).sort("order_date", DESCENDING))

    return render_template("use_profile.html", user=user, orders=orders)
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('user_login'))

    user_id = session['user_id']
    username = request.form.get("username")
    phoneno = request.form.get("phoneno")
    address = request.form.get("address")

    update_fields = {}
    if username:
        update_fields["username"] = username
    if phoneno:
        update_fields["phoneno"] = phoneno
    if address:
        update_fields["address"] = address

    if update_fields:
        users_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_fields}
        )

        flash("Profile updated successfully!", "success")
    else:
        flash("No changes detected.", "warning")

    return redirect(url_for("use_profile"))  # Ensure this route exists

@app.route('/farmer_orders')
def farmer_orders():
    if 'farmer_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('loginf'))

    # Fetch all orders from the farmer_orders_collection
    orders = list(farmer_orders_collection.find().sort("order_date", -1))

    return render_template("farmer_orders.html", orders=orders)



@app.route('/order_details/<order_id>')
def order_details(order_id):
    if 'farmer_id' not in session:
        flash('Please log in to continue.', 'error')
        return redirect(url_for('user_login'))

    try:
       order = farmer_orders_collection.find_one({"_id": ObjectId(order_id)})  
    except:
        flash("Invalid Order ID!", "error")
        return redirect(url_for("farmer_orders"))

    if not order:
        flash("Order not found!", "error")
        return redirect(url_for("farmer_orders"))

    return render_template("order_details.html", order=order)

@app.route('/cancel', methods=['POST'])
def cancel():
    return redirect(url_for('user_home'))

@app.route('/cancel_cart')
def cancel_cart():
    return render_template('user_home.html')


@app.route('/welcome')
def welcome():
    if 'username' in session:
        return f"Welcome, {session['username']}!"
    else:
        return redirect(url_for('login'))
    
 #check
 
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Static file serving
@app.route('/static/css/<path:filename>')
def custom_static_css(filename):
    return send_from_directory('static/css', filename, mimetype='text/css')

@app.route('/static/js/<path:filename>')
def custom_static_js(filename):
    return send_from_directory('static/js', filename, mimetype='text/javascript')

if __name__ == '__main__':
    app.run(debug=True)
