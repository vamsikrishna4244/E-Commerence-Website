import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def seed_data():
    service_account_path = os.environ.get('FIREBASE_SERVICE_ACCOUNT_JSON')
    if not service_account_path:
        print("Error: FIREBASE_SERVICE_ACCOUNT_JSON not set in .env")
        return

    cred = credentials.Certificate(service_account_path)
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    products = [
        {
            'name': 'Wireless Noise Cancelling Headphones',
            'description': 'Experience world-class noise cancellation and premium sound quality with these wireless over-ear headphones.',
            'price': 299.99,
            'category': 'Electronics',
            'image_url': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80',
            'created_at': datetime.datetime.now()
        },
        {
            'name': 'Smart Watch Series 7',
            'description': 'Stay connected and track your fitness with the latest smart watch featuring a brilliant retina display.',
            'price': 399.00,
            'category': 'Electronics',
            'image_url': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80',
            'created_at': datetime.datetime.now()
        },
        {
            'name': 'Minimalist Leather Wallet',
            'description': 'A slim, hand-crafted leather wallet designed for simplicity and durability.',
            'price': 45.00,
            'category': 'Fashion',
            'image_url': 'https://images.unsplash.com/photo-1627123424574-724758594e93?w=800&q=80',
            'created_at': datetime.datetime.now()
        },
        {
            'name': 'Mechanical Keyborad (RGB)',
            'description': 'High-performance mechanical keyboard with customizable RGB lighting and tactile switches.',
            'price': 129.50,
            'category': 'Electronics',
            'image_url': 'https://images.unsplash.com/photo-1511467687858-23d96c32e4ae?w=800&q=80',
            'created_at': datetime.datetime.now()
        }
    ]
    
    print("Seeding products...")
    for p in products:
        db.collection('products').add(p)
        print(f"Added product: {p['name']}")
    
    print("Seeding complete!")

if __name__ == '__main__':
    seed_data()
