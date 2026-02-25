import random
import string
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, recipients, text_body, html_body, sender=None):
    if not sender:
        sender = current_app.config.get('MAIL_DEFAULT_SENDER')
    if not sender:
        sender = current_app.config.get('MAIL_USERNAME')
    
    if not sender:
        sender = "noreply@eshop.com"

    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, 
           args=(current_app._get_current_object(), msg)).start()

def generate_captcha(length=6, width=160, height=60):
    # Generate random text
    text = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    
    # Create image
    image = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    
    # Load font (falling back to default if necessary)
    try:
        # Try to use a system font if available, else default
        font = ImageFont.truetype("arial.ttf", 36)
    except:
        font = ImageFont.load_default()

    # Draw text
    # Calculate text layout (simple approach)
    for i, char in enumerate(text):
        draw.text((10 + i * 25, 10), char, font=font, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)))

    # Add noise/lines
    for _ in range(5):
        draw.line([(random.randint(0, width), random.randint(0, height)), 
                   (random.randint(0, width), random.randint(0, height))], 
                  fill=(150, 150, 150), width=2)

    # Blur slightly
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Save to buffer
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    return text, img_str

from functools import wraps
from flask import abort
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
