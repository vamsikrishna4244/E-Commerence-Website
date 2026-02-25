# 🛍️ EShop Pro

A full-featured, modern e-commerce web application built with **Flask** and **Firebase Firestore**. Features a premium glassmorphism UI, Google OAuth, CAPTCHA login, email notifications, and a complete admin panel.

---

## ✨ Features

- 🏠 **Homepage** — Hero section with featured products
- 🛒 **Shopping Cart** — AJAX-powered, no page reloads
- 💳 **Checkout** — Full order flow with email confirmation
- 👤 **Authentication** — Login, Register, Google OAuth, CAPTCHA, Forgot/Reset Password
- 📦 **Admin Panel** — Create, edit, delete products
- 📊 **User Dashboard** — Order history and profile management
- 📧 **Email System** — Welcome, order confirmation, password reset emails
- 🔍 **Product Search & Filter** — By category and keyword
- 🎨 **Premium UI** — Glassmorphism design with Bootstrap 5 & Font Awesome

---

## 🗂️ Project Structure

```
eshop-pro/
│
├── run.py                          # App entry point
├── config.py                       # App configuration
├── requirements.txt                # Python dependencies
├── seed_db.py                      # Seed Firestore with sample products
├── create_admin.py                 # Create admin user in Firestore
├── .env.example                    # Environment variable template
├── .gitignore
├── firebase-credentials.example.json  # Firebase config template
│
└── app/
    ├── __init__.py                 # App factory, extensions init
    ├── models.py                   # User model (Flask-Login)
    ├── forms.py                    # WTForms definitions
    ├── utils.py                    # Email sender, CAPTCHA generator, admin decorator
    │
    ├── routes/
    │   ├── __init__.py
    │   ├── main.py                 # Home, products, cart, checkout, dashboard
    │   ├── auth.py                 # Login, register, OAuth, password reset
    │   ├── admin.py                # Admin product management
    │   └── errors.py               # 404, 403, 500 error handlers
    │
    ├── static/
    │   ├── css/
    │   │   └── main.css            # Custom styles (glassmorphism, animations)
    │   └── js/
    │       └── main.js             # AJAX cart, interactions
    │
    └── templates/
        ├── base.html               # Base layout (navbar, toast, footer)
        ├── index.html              # Homepage
        ├── product_list.html       # Shop / product grid
        ├── product_detail.html     # Single product page
        ├── cart.html               # Shopping cart
        ├── checkout.html           # Checkout form
        ├── dashboard.html          # User dashboard / orders
        ├── hello.html              # Demo page
        │
        ├── auth/
        │   ├── login.html
        │   ├── register.html
        │   ├── forgot_password.html
        │   ├── reset_password.html
        │   └── edit_profile.html
        │
        ├── admin/
        │   ├── products.html       # Product inventory table
        │   └── product_form.html   # Add / edit product form
        │
        ├── email/
        │   ├── base_email.html     # Email layout template
        │   ├── welcome.html        # Welcome email
        │   ├── order_confirmation.html
        │   └── reset_password.html
        │
        └── errors/
            ├── 404.html
            ├── 403.html
            └── 500.html
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/eshop-pro.git
cd eshop-pro
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/) and create a project
2. Enable **Firestore Database** (start in test mode for development)
3. Go to **Project Settings → Service Accounts → Generate New Private Key**
4. Download the JSON file and place it in your project root
5. Rename it or note its path for the `.env` file

### 5. Set Up Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use your Firebase project)
3. Navigate to **APIs & Services → Credentials → Create OAuth 2.0 Client ID**
4. Set **Authorized redirect URIs** to: `http://localhost:5000/google/callback`
5. Copy your **Client ID** and **Client Secret**

### 6. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and fill in your real values:

```env
# Flask
SECRET_KEY=generate-a-long-random-string-here
FLASK_APP=run.py
FLASK_DEBUG=1

# Firebase
FIREBASE_SERVICE_ACCOUNT_JSON=your-firebase-credentials.json
FIREBASE_DATABASE_URL=https://your-project-id.firebaseio.com

# Email (Gmail)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_gmail_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

> **Gmail tip:** Use an [App Password](https://support.google.com/accounts/answer/185833), not your regular Gmail password.

> **Secret Key tip:** Generate one with:
> ```bash
> python -c "import secrets; print(secrets.token_hex(32))"
> ```

### 7. Seed the Database (Optional)

```bash
python seed_db.py
```

### 8. Create an Admin User

```bash
python create_admin.py
```

Default admin credentials: `admin@eshop.com` / `admin123`
> ⚠️ Change these immediately after first login in production.

### 9. Run the App

```bash
python run.py
```

Visit: [http://localhost:5000](http://localhost:5000)

---

## 🔐 Security Notes

- Never commit your `.env` file or Firebase credentials JSON
- Set `FLASK_DEBUG=0` and `SESSION_COOKIE_SECURE=True` in production
- Use HTTPS in production (required for secure cookies and OAuth)
- Rotate your `SECRET_KEY` if it's ever exposed

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, Flask 3.0 |
| Database | Firebase Firestore |
| Auth | Flask-Login, Authlib (Google OAuth) |
| Forms | Flask-WTF, WTForms |
| Email | Flask-Mail |
| Frontend | Bootstrap 5, Font Awesome 6 |
| Security | CSRF protection, CAPTCHA, bcrypt hashing |


---

## 🙌 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you'd like to change.
