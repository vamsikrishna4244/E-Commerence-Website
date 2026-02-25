import firebase_admin
from firebase_admin import credentials, firestore
from werkzeug.security import generate_password_hash
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def create_admin():
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
    if not service_account_path:
        print("Error: FIREBASE_SERVICE_ACCOUNT_JSON not set in .env")
        return

    cred = credentials.Certificate(service_account_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    admin_email = 'admin@eshop.com'
    admin_password = 'admin123'
    
    # Check if admin already exists
    users_ref = db.collection('users').where('email', '==', admin_email).get()
    if len(users_ref) > 0:
        print(f"Admin user with email {admin_email} already exists. Updating to admin status just in case...")
        for u in users_ref:
            db.collection('users').document(u.id).update({'is_admin': True})
    else:
        user_data = {
            'username': 'AdminUser',
            'email': admin_email,
            'password_hash': generate_password_hash(admin_password),
            'is_admin': True,
            'created_at': datetime.datetime.now()
        }
        db.collection('users').add(user_data)
        print(f"Created new admin user: {admin_email}")

if __name__ == '__main__':
    create_admin()
