# 🌾 Farmie — Farm-to-Consumer Marketplace

Farmie is a full-stack web application built with **Flask** and **MongoDB** that bridges the gap between farmers and consumers. It enables farmers to list and sell agricultural products directly to buyers, includes an ML-powered crop disease solution finder, and provides crop cultivation guidelines based on climate and soil type.

---

## 🚀 Features

| Module | Description |
|---|---|
| **Farmer Portal** | Register, log in, manage products (add / edit / delete), view orders & payments |
| **Consumer Portal** | Browse products, add to cart, checkout with address & payment method |
| **Admin Panel** | Add crop guidelines, post news, add disease–solution pairs |
| **Disease Finder** | ML model (TF-IDF + classifier) predicts treatment for a given plant disease |
| **Crop Guidelines** | Filter crops by climate and soil type to get step-by-step cultivation advice |
| **News Feed** | Admin-posted agricultural news displayed to users |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.13, Flask 3.x
- **Database:** MongoDB (via PyMongo)
- **Authentication:** Flask-Bcrypt (password hashing)
- **ML:** scikit-learn (TF-IDF vectorizer + classifier), stored as `model.pkl`
- **Frontend:** Jinja2 templates, HTML/CSS/JS

---

## 📋 Prerequisites

- Python 3.10+ (project tested on Python 3.13)
- MongoDB running locally on `mongodb://localhost:27017`
- Git (optional)

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/your-username/farmie.git
cd farmie
```

### 2. Create a virtual environment
```bash
python -m venv venv
```

### 3. Activate the virtual environment

**Windows:**
```bash
venv\scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Start MongoDB
Make sure MongoDB is running locally:
```bash
mongod
```

### 6. Run the application
```bash
python app.py
```

The app will be available at **http://127.0.0.1:5000**

---

## 📁 Project Structure

```
farmie/
├── app.py                  # Main Flask application & all routes
├── train_model.py          # Script to train and save the ML model
├── model.pkl               # Trained ML model (vectorizer + classifier)
├── requirements.txt        # Python dependencies
├── static/
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript files
│   └── uploads/            # Farmer-uploaded product images
├── templates/              # Jinja2 HTML templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── home.html           # Farmer dashboard
│   ├── user_home.html      # Consumer product listing
│   ├── cart.html
│   ├── payment.html
│   ├── admin.html
│   ├── guideline.html
│   ├── disease.html
│   └── ...
└── fonts/                  # Custom fonts
```

---

## 🗄️ MongoDB Collections

| Collection | Purpose |
|---|---|
| `users` | Consumer accounts |
| `farmers` | Farmer accounts |
| `admin` | Admin credentials |
| `products` | Product listings by farmers |
| `cart` | Shopping cart items per user |
| `payments` | Completed orders (consumer view) |
| `farmer_orders` | Orders visible to farmers |
| `guideline` | Crop cultivation guidelines |
| `news` | Agricultural news posts |
| `disease` | Disease → solution mappings |

---

## 👤 Default Admin Credentials

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `Admin@12` |

> ⚠️ Change these credentials before deploying to production.

---

## 🤖 ML Model

The disease solution finder uses a TF-IDF vectorizer paired with a classifier trained on disease–solution pairs stored in MongoDB. To retrain the model:

```bash
python train_model.py
```

This regenerates `model.pkl`.

---

## 🔐 Security Notes

- Change `app.secret_key` in `app.py` to a strong random value before deployment.
- Never commit `model.pkl` with sensitive training data to a public repository.
- Use environment variables for MongoDB URI and secret keys in production.

---

## 📄 License

This project is for educational purposes.
