from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, current_user, login_required
from app.models import User
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm, UpdateProfileForm
from app.utils import generate_captcha, send_email
from app import db, mail, oauth
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer
import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/google/login')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/google/callback')
def google_callback():
    token = oauth.google.authorize_access_token()
    user_info = token.get('userinfo')
    if not user_info:
        flash('Failed to fetch user info from Google.', 'danger')
        return redirect(url_for('auth.login'))

    email = user_info.get('email')
    username = user_info.get('name') or email.split('@')[0]
    
    # Check if user exists
    user = User.get_by_email(email)
    if not user:
        # Create new user
        user_data = {
            'username': username,
            'email': email,
            'password_hash': 'OAUTH_USER', # Placeholder since they use Google
            'is_admin': False,
            'created_at': datetime.datetime.now()
        }
        db.collection('users').add(user_data)
        user = User.get_by_email(email)
        flash(f'Account created via Google: {email}', 'success')
    else:
        flash(f'Logged in via Google: {email}', 'success')

    login_user(user)
    return redirect(url_for('main.home'))

@auth_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        # Check if email is already taken by another user
        if form.email.data != current_user.email:
            existing_user = User.get_by_email(form.email.data)
            if existing_user:
                flash('That email is already in use. Please choose a different one.', 'danger')
                return render_template('edit_profile.html', form=form)

        # Update Firestore
        users_ref = db.collection('users').where('email', '==', current_user.email).limit(1).get()
        if users_ref:
            doc_id = users_ref[0].id
            db.collection('users').document(doc_id).update({
                'username': form.username.data,
                'email': form.email.data
            })
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('main.dashboard'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile', form=form)

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(form.email.data)
        if user:
            s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps(user.email, salt='reset-password')
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            
            try:
                send_email(
                    'Reset Your EShop Pro Password',
                    recipients=[user.email],
                    text_body=f"To reset your password, visit the following link: {reset_url}",
                    html_body=render_template('email/reset_password.html', reset_url=reset_url)
                )
                flash('An email has been sent with instructions to reset your password.', 'info')
            except Exception as e:
                flash('An error occurred while sending the email. Please try again later.', 'danger')
                print(f"ERROR: {e}")
        else:
            # For security reasons, don't reveal if email exists or not
            flash('If an account with that email exists, a reset link has been sent.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('forgot_password.html', title='Forgot Password', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='reset-password', max_age=3600)
    except:
        flash('The reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.get_by_email(email)
        if user:
            # Get the doc reference to update
            users_ref = db.collection('users').where('email', '==', email).limit(1).get()
            if users_ref:
                doc_id = users_ref[0].id
                hashed_password = generate_password_hash(form.password.data)
                db.collection('users').document(doc_id).update({'password_hash': hashed_password})
                flash('Your password has been updated! You can now log in.', 'success')
                return redirect(url_for('auth.login'))
        flash('An error occurred. Please try again.', 'danger')
    return render_template('reset_password.html', title='Reset Password', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = LoginForm()
    if form.validate_on_submit():
        # Check CAPTCHA
        if form.captcha.data.upper() != session.get('captcha_text'):
            flash('Invalid CAPTCHA. Please try again.', 'danger')
            # Regenerate CAPTCHA
            text, img = generate_captcha()
            session['captcha_text'] = text
            return render_template('login.html', form=form, captcha_img=img)

        user = User.get_by_email(form.email.data)
        if user and user.verify_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    # Generate/Regenerate CAPTCHA for GET or failed POST
    text, img = generate_captcha()
    session['captcha_text'] = text
    
    return render_template('login.html', title='Login', form=form, captcha_img=img)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user exists
        if User.get_by_email(form.email.data):
            flash('Email already registered.', 'warning')
            return render_template('register.html', form=form)
            
        hashed_password = generate_password_hash(form.password.data)
        user_data = {
            'username': form.username.data,
            'email': form.email.data,
            'password_hash': hashed_password,
            'is_admin': False,
            'created_at': datetime.datetime.now()
        }
        db.collection('users').add(user_data)
        
        # Send Welcome Email
        try:
            send_email(
                'Welcome to EShop Pro!',
                sender=None, # Use default
                recipients=[form.email.data],
                text_body=f"Hi {form.username.data},\n\nWelcome to EShop Pro! Your account has been successfully created. You can now start shopping for premium products.\n\nBest regards,\nThe EShop Pro Team",
                html_body=render_template('email/welcome.html', user=user_data)
            )
        except Exception as e:
            print(f"Failed to send welcome email: {e}")

        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html', title='Register', form=form)

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
