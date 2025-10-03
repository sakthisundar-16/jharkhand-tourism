from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from mysql.connector import Error
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime, timedelta
from config import Config

from functools import wraps
def require_user_type(user_type):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.')
                return redirect(url_for('login'))
            
            if session.get('user_type') != user_type:
                flash(f'Access denied. This page is only for {user_type}s.')
                return redirect(url_for('login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

app = Flask(__name__)
app.config.from_object(Config)

# File upload configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            charset=app.config['MYSQL_CHARSET'],
            auth_plugin=app.config['MYSQL_AUTH_PLUGIN']
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    """Homepage - Jharkhand Tourism Platform"""
    # Get published content from guides
    connection = get_db_connection()
    published_content = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Fetch latest published content with guide information
            cursor.execute("""
                SELECT gu.*, u.full_name as guide_name, u.username as guide_username
                FROM guide_uploads gu 
                JOIN users u ON gu.guide_id = u.id 
                WHERE u.user_type = 'guide'
                ORDER BY gu.upload_date DESC 
                LIMIT 12
            """)
            published_content = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching content: {e}")
        finally:
            cursor.close()
            connection.close()
    
    return render_template('index.html', published_content=published_content)

# Tourist Login Route
@app.route('/login/tourist', methods=['GET', 'POST'])
def login_tourist():
    """Tourist login for Jharkhand Tourism"""
    if request.method == 'POST':
        user_type = 'tourist'
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND user_type = %s",
                         (username, user_type))
            user = cursor.fetchone()

            if user and user['password'] == password:  # In production, use hashed passwords
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_type'] = user['user_type']
                session['full_name'] = user['full_name']

                cursor.close()
                connection.close()
                flash('Welcome to Jharkhand Tourism! Tourist login successful!')
                return redirect(url_for('tourist_dashboard'))
            else:
                flash('Invalid tourist credentials! Please check your username and password.')

            cursor.close()
            connection.close()

    return render_template('login_tourist.html')

# Guide Login Route
@app.route('/login/guide', methods=['GET', 'POST'])
def login_guide():
    """Guide login for Jharkhand Tourism"""
    if request.method == 'POST':
        user_type = 'guide'
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s AND user_type = %s",
                         (username, user_type))
            user = cursor.fetchone()

            if user and user['password'] == password:  # In production, use hashed passwords
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['user_type'] = user['user_type']
                session['full_name'] = user['full_name']

                cursor.close()
                connection.close()
                flash('Welcome to Jharkhand Tourism! Guide login successful!')
                return redirect(url_for('guide_dashboard'))
            else:
                flash('Invalid guide credentials! Please check your username and password.')

            cursor.close()
            connection.close()

    return render_template('login_guide.html')

# Keep the original login route for backward compatibility (redirects to tourist login)
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Default login - redirects to tourist login"""
    return redirect(url_for('login_tourist'))

@app.route('/register', methods=['POST'])
def register():
    """General registration handler for Jharkhand Tourism"""
    user_type = request.form['user_type']
    
    # Prevent admin registration
    if user_type == 'admin':
        flash('Admin registration is not allowed!')
        return redirect(url_for('login'))
    
    # Validate user type
    if user_type not in ['tourist', 'guide']:
        flash('Invalid registration type!')
        return redirect(url_for('login'))
    
    username = request.form['username']
    password = request.form['password']
    full_name = request.form['full_name']
    phone = request.form['phone']
    email = request.form['email']
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Check if username already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists! Please choose a different username.')
                return redirect(url_for('login'))
            
            # Insert new user with specific user type
            cursor.execute("""INSERT INTO users (username, password, user_type, full_name, phone, email) 
                            VALUES (%s, %s, %s, %s, %s, %s)""",
                         (username, password, user_type, full_name, phone, email))
            
            user_id = cursor.lastrowid
            
            # If registering as guide, create guide profile automatically with Jharkhand defaults
            if user_type == 'guide':
                cursor.execute("""INSERT INTO guides (user_id, specialization, experience_years, 
                                languages_spoken, location, price_per_day, availability_status) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                             (user_id, 'General Tourism', 1, 'Hindi, English', 'Ranchi District', 2000.00, 'available'))
            
            connection.commit()
            flash(f'{user_type.title()} registration successful! Welcome to Jharkhand Tourism! Please login with your credentials.')
        except Error as e:
            flash(f'Registration failed: {e}')
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('login_tourist'))

# Tourist Registration Route
@app.route('/register/tourist', methods=['GET', 'POST'])
def register_tourist():
    """Tourist registration for Jharkhand Tourism"""
    if request.method == 'POST':
        user_type = 'tourist'
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Check if username already exists
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already exists! Please choose a different username.')
                    return redirect(url_for('register_tourist'))

                # Insert new tourist user
                cursor.execute("""INSERT INTO users (username, password, user_type, full_name, phone, email)
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                             (username, password, user_type, full_name, phone, email))

                connection.commit()
                flash('Tourist registration successful! Welcome to Jharkhand Tourism! Please login with your credentials.')
                return redirect(url_for('login_tourist'))
            except Error as e:
                flash(f'Registration failed: {e}')
            finally:
                cursor.close()
                connection.close()

    return render_template('register_tourist.html')

# Guide Registration Route
@app.route('/register/guide', methods=['GET', 'POST'])
def register_guide():
    """Guide registration for Jharkhand Tourism"""
    if request.method == 'POST':
        user_type = 'guide'
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        phone = request.form['phone']
        email = request.form['email']
        specialization = request.form.get('specialization', 'General Tourism')
        experience_years = request.form.get('experience_years', 1)
        languages_spoken = request.form.get('languages_spoken', 'Hindi, English, Santali')
        price_per_day = request.form.get('price_per_day', 2000)
        location = request.form.get('location', 'Ranchi District')

        connection = get_db_connection()
        if connection:
            cursor = connection.cursor()
            try:
                # Check if username already exists
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    flash('Username already exists! Please choose a different username.')
                    return redirect(url_for('register_guide'))

                # Insert new guide user
                cursor.execute("""INSERT INTO users (username, password, user_type, full_name, phone, email)
                                VALUES (%s, %s, %s, %s, %s, %s)""",
                             (username, password, user_type, full_name, phone, email))

                user_id = cursor.lastrowid

                # Create guide profile automatically with Jharkhand-specific defaults
                cursor.execute("""INSERT INTO guides (user_id, specialization, experience_years,
                                languages_spoken, location, price_per_day, availability_status)
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                             (user_id, specialization, experience_years, languages_spoken,
                              location, price_per_day, 'available'))

                connection.commit()
                flash('Guide registration successful! Welcome to Jharkhand Tourism platform! Please login with your credentials.')
                return redirect(url_for('login_guide'))
            except Error as e:
                flash(f'Registration failed: {e}')
            finally:
                cursor.close()
                connection.close()

    return render_template('register_guide.html')

@app.route('/tourist_dashboard')
@require_user_type('tourist')
def tourist_dashboard():
    """Tourist dashboard - Browse Jharkhand guides and manage bookings"""
    # Get available guides and tourist's bookings
    connection = get_db_connection()
    guides = []
    bookings = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get guides with their specializations and locations in Jharkhand
        cursor.execute("""SELECT u.id as user_id, u.full_name as guide_name, u.username, 
                         g.specialization, g.experience_years, g.languages_spoken, 
                         g.location, g.price_per_day, g.rating, g.availability_status
                         FROM users u JOIN guides g ON u.id = g.user_id 
                         WHERE g.availability_status = 'available' AND u.user_type = 'guide'""")
        guides = cursor.fetchall()
        
        # Get tourist's Jharkhand tour bookings with enhanced details
        tourist_id = session['user_id']
        cursor.execute("""SELECT b.*, u.full_name as guide_name 
                         FROM bookings b LEFT JOIN users u ON b.guide_id = u.id 
                         WHERE b.tourist_id = %s ORDER BY b.created_at DESC""", (tourist_id,))
        bookings = cursor.fetchall()
        
        cursor.close()
        connection.close()
    
    return render_template('tourist_dashboard.html', guides=guides, bookings=bookings)

# NEW ROUTE: Show booking form for selected guide
@app.route('/book_guide/<int:guide_id>')
@require_user_type('tourist')
def book_guide_form(guide_id):
    """Display booking form for selected Jharkhand guide"""
    connection = get_db_connection()
    guide = None
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            # Get guide details with user information
            cursor.execute("""
                SELECT u.id as user_id, u.full_name as guide_name, u.username, 
                       g.specialization, g.experience_years, g.languages_spoken, 
                       g.location, g.price_per_day, g.rating, g.availability_status
                FROM users u 
                JOIN guides g ON u.id = g.user_id 
                WHERE u.id = %s AND u.user_type = 'guide'
            """, (guide_id,))
            guide = cursor.fetchone()
            
            if not guide:
                flash('Guide not found!')
                return redirect(url_for('tourist_dashboard'))
                
        except Exception as e:
            print(f"Error fetching guide: {e}")
            flash('Error loading guide information!')
            return redirect(url_for('tourist_dashboard'))
        finally:
            cursor.close()
            connection.close()
    
    return render_template('tourist_booking.html', guide=guide)

# UPDATED ROUTE: Process booking with enhanced details
# TO THIS:
@app.route('/book_guide', methods=['POST'])
@require_user_type('tourist')
def book_guide(): 

    """Process Jharkhand tour booking request with enhanced details"""
    tourist_id = session['user_id']
    
    # Get form data
    guide_id = request.form['guide_id']
    tourist_name = request.form['tourist_name']
    phone = request.form['phone']
    email = request.form.get('email', '')
    native_place = request.form['native_place']
    arrival_date = request.form['arrival_date']
    days_to_stay = request.form['days_to_stay']
    group_size = request.form.get('group_size', 1)
    tour_type = request.form.get('tour_type', '')
    specific_places = request.form.get('specific_places', '')
    accommodation = request.form.get('accommodation', '')
    transport = request.form.get('transport', '')
    dietary_preference = request.form.get('dietary_preference', '')
    fitness_level = request.form.get('fitness_level', '')
    additional_requirements = request.form.get('additional_requirements', '')
    
    # Calculate departure date
    arrival = datetime.strptime(arrival_date, '%Y-%m-%d')
    departure = arrival + timedelta(days=int(days_to_stay))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Verify the guide exists and is actually a guide
            cursor.execute("SELECT id FROM users WHERE id = %s AND user_type = 'guide'", (guide_id,))
            if not cursor.fetchone():
                flash('Invalid guide selection!')
                return redirect(url_for('tourist_dashboard'))
            
            # Insert comprehensive booking details
            cursor.execute("""
                INSERT INTO bookings (
                    tourist_id, guide_id, tourist_name, phone, email, native_place, 
                    arrival_date, departure_date, days_to_stay, group_size, tour_type,
                    specific_places, accommodation, transport, dietary_preference, 
                    fitness_level, additional_requirements, booking_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                tourist_id, guide_id, tourist_name, phone, email, native_place, 
                arrival_date, departure.date(), days_to_stay, group_size, tour_type,
                specific_places, accommodation, transport, dietary_preference, 
                fitness_level, additional_requirements, 'pending'
            ))
            
            connection.commit()
            flash('Jharkhand tour booking request sent successfully! Your guide will contact you within 24 hours.')
            
        except Error as e:
            flash(f'Booking failed: {e}')
            return redirect(url_for('tourist_dashboard'))
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('tourist_dashboard'))

@app.route('/guide_dashboard')
@require_user_type('guide')
def guide_dashboard():
    """Guide dashboard - Manage Jharkhand tourism bookings and content"""
    guide_id = session['user_id']
    
    # Get comprehensive bookings for this guide
    connection = get_db_connection()
    bookings = []
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""SELECT b.*, u.username as tourist_username, u.full_name as tourist_full_name
                         FROM bookings b JOIN users u ON b.tourist_id = u.id 
                         WHERE b.guide_id = %s ORDER BY b.created_at DESC""", (guide_id,))
        bookings = cursor.fetchall()
        cursor.close()
        connection.close()
    
    return render_template('guide_dashboard.html', bookings=bookings)

@app.route('/update_guide_profile', methods=['POST'])
@require_user_type('guide')
def update_guide_profile():
    """Update Jharkhand guide profile with specializations and service areas"""
    user_id = session['user_id']
    specialization = request.form.get('specialization', '')
    experience_years = request.form.get('experience_years', 0)
    languages_spoken = request.form.get('languages_spoken', '')
    location = request.form.get('location', '')
    price_per_day = request.form.get('price_per_day', 0)
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # First check if guide profile exists
            cursor.execute("SELECT id FROM guides WHERE user_id = %s", (user_id,))
            guide_exists = cursor.fetchone()
            
            if guide_exists:
                # Update existing profile
                cursor.execute("""UPDATE guides SET specialization = %s, experience_years = %s, 
                                languages_spoken = %s, location = %s, price_per_day = %s 
                                WHERE user_id = %s""",
                             (specialization, experience_years, languages_spoken, location, price_per_day, user_id))
                flash('Jharkhand guide profile updated successfully!')
            else:
                # Create new profile if doesn't exist
                cursor.execute("""INSERT INTO guides (user_id, specialization, experience_years, 
                                languages_spoken, location, price_per_day, availability_status) 
                                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                             (user_id, specialization, experience_years, languages_spoken, location, price_per_day, 'available'))
                flash('Jharkhand guide profile created successfully!')
            
            connection.commit()
        except Exception as e:
            flash(f'Profile update failed: {str(e)}')
            print(f"Database error: {e}")
        finally:
            cursor.close()
            connection.close()
    else:
        flash('Database connection failed!')
    
    return redirect(url_for('guide_dashboard'))

@app.route('/update_booking_status/<int:booking_id>/<status>')
@require_user_type('guide')
def update_booking_status(booking_id, status):
    """Update Jharkhand tour booking status by guide"""
    guide_id = session['user_id']
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            # Verify this booking belongs to the current guide
            cursor.execute("SELECT id FROM bookings WHERE id = %s AND guide_id = %s", 
                         (booking_id, guide_id))
            if not cursor.fetchone():
                flash('Access denied. This booking does not belong to you.')
                return redirect(url_for('guide_dashboard'))
            
            cursor.execute("UPDATE bookings SET booking_status = %s WHERE id = %s AND guide_id = %s", 
                         (status, booking_id, guide_id))
            connection.commit()
            
            # Custom flash messages for different statuses
            if status == 'confirmed':
                flash(f'Jharkhand tour booking confirmed successfully! Tourist will be notified.')
            elif status == 'completed':
                flash(f'Jharkhand tour marked as completed successfully!')
            elif status == 'cancelled':
                flash(f'Booking cancelled. Tourist will be notified.')
            else:
                flash(f'Booking {status} successfully!')
        except Error as e:
            flash(f'Update failed: {e}')
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('guide_dashboard'))

@app.route('/upload_content', methods=['POST'])
@require_user_type('guide')
def upload_content():
    """Upload Jharkhand tourism content by guides"""
    guide_id = session['user_id']
    upload_type = request.form['upload_type']
    title = request.form['title']
    description = request.form['description']
    location = request.form.get('location', '')
    
    image_path = ''
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            image_path = f'uploads/{filename}'
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("""INSERT INTO guide_uploads (guide_id, upload_type, title, description, 
                            image_path, location) VALUES (%s, %s, %s, %s, %s, %s)""",
                         (guide_id, upload_type, title, description, image_path, location))
            connection.commit()
            flash('Jharkhand content uploaded successfully! It will appear on the homepage.')
        except Error as e:
            flash(f'Upload failed: {e}')
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('guide_dashboard'))

@app.route('/admin_dashboard')
@require_user_type('admin')
def admin_dashboard():
    """Admin dashboard for Jharkhand Tourism platform management"""
    connection = get_db_connection()
    data = {}
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        
        # Get all users
        cursor.execute("SELECT * FROM users ORDER BY created_at DESC")
        data['users'] = cursor.fetchall()
        
        # Get all bookings with tourist and guide names
        cursor.execute("""SELECT b.*, u1.username as tourist_name, u2.username as guide_name 
                         FROM bookings b 
                         JOIN users u1 ON b.tourist_id = u1.id 
                         JOIN users u2 ON b.guide_id = u2.id 
                         ORDER BY b.created_at DESC""")
        data['bookings'] = cursor.fetchall()
        
        # Get all Jharkhand content uploads
        cursor.execute("""SELECT gu.*, u.username as guide_name 
                         FROM guide_uploads gu 
                         JOIN users u ON gu.guide_id = u.id 
                         ORDER BY gu.upload_date DESC""")
        data['uploads'] = cursor.fetchall()
        
        cursor.close()
        connection.close()
    
    return render_template('admin_dashboard.html', data=data)

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    """Admin function to delete users from Jharkhand Tourism platform"""
    if 'user_id' not in session or session['user_type'] != 'admin':
        return redirect(url_for('login'))
    
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor()
        try:
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            connection.commit()
            flash('User deleted successfully from Jharkhand Tourism platform!')
        except Error as e:
            flash(f'Delete failed: {e}')
        finally:
            cursor.close()
            connection.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/content/<int:content_id>')
def get_content_details(content_id):
    """Get detailed information about Jharkhand tourism content"""
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT gu.*, u.full_name as guide_name, u.username as guide_username
                FROM guide_uploads gu 
                JOIN users u ON gu.guide_id = u.id 
                WHERE gu.id = %s
            """, (content_id,))
            content = cursor.fetchone()
            
            if content:
                # Convert datetime to string for JSON serialization
                if content['upload_date']:
                    content['upload_date'] = content['upload_date'].isoformat()
                
                return jsonify({'success': True, 'content': content})
            else:
                return jsonify({'success': False, 'message': 'Content not found'})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})
        finally:
            cursor.close()
            connection.close()
    
    return jsonify({'success': False, 'message': 'Database error'})

# Route to get guide's own content for editing
@app.route('/guide/my_content')
@require_user_type('guide')
def guide_my_content():
    """Get guide's own Jharkhand content for editing"""
    guide_id = session['user_id']
    connection = get_db_connection()
    my_content = []
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT * FROM guide_uploads 
                WHERE guide_id = %s 
                ORDER BY upload_date DESC
            """, (guide_id,))
            my_content = cursor.fetchall()
        except Exception as e:
            print(f"Error fetching content: {e}")
        finally:
            cursor.close()
            connection.close()
    
    return jsonify({'success': True, 'content': my_content})

# Route to edit content
@app.route('/guide/edit_content/<int:content_id>', methods=['GET', 'POST'])
@require_user_type('guide')
def edit_content(content_id):
    """Edit Jharkhand tourism content (only by content owner)"""
    guide_id = session['user_id']
    connection = get_db_connection()
    
    if not connection:
        if request.method == 'GET':
            return jsonify({'success': False, 'message': 'Database connection failed'})
        flash('Database connection failed!')
        return redirect(url_for('guide_dashboard'))
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify ownership
        cursor.execute("SELECT * FROM guide_uploads WHERE id = %s AND guide_id = %s", 
                      (content_id, guide_id))
        content = cursor.fetchone()
        
        if not content:
            if request.method == 'GET':
                return jsonify({'success': False, 'message': 'Content not found or access denied'})
            flash('Content not found or you do not have permission to edit it!')
            return redirect(url_for('guide_dashboard'))
        
        if request.method == 'POST':
            # Update content
            upload_type = request.form.get('upload_type')
            title = request.form.get('title')
            description = request.form.get('description')
            location = request.form.get('location', '')
            
            # Validate required fields
            if not upload_type or not title or not description:
                if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                    return jsonify({'success': False, 'message': 'Missing required fields'})
                flash('Please fill in all required fields!')
                return redirect(url_for('guide_dashboard') + '#content-panel')
            
            # Handle image update
            image_path = content['image_path']  # Keep existing image by default
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    # Delete old image if exists
                    if image_path and os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_path))):
                        try:
                            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(image_path)))
                        except Exception as e:
                            print(f"Warning: Could not delete old image: {e}")
                    
                    # Save new image
                    filename = secure_filename(file.filename)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                    filename = timestamp + filename
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
                    try:
                        file.save(file_path)
                        image_path = f'uploads/{filename}'
                    except Exception as e:
                        print(f"Error saving new image: {e}")
                        if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                            return jsonify({'success': False, 'message': 'Failed to save image'})
                        flash('Failed to save image!')
                        return redirect(url_for('guide_dashboard') + '#content-panel')
            
            # Update database
            cursor.execute("""
                UPDATE guide_uploads 
                SET upload_type = %s, title = %s, description = %s, location = %s, image_path = %s
                WHERE id = %s AND guide_id = %s
            """, (upload_type, title, description, location, image_path, content_id, guide_id))
            
            connection.commit()
            
            # Return appropriate response based on request type
            if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': True, 'message': 'Jharkhand content updated successfully!'})
            else:
                flash('Jharkhand content updated successfully!')
                return redirect(url_for('guide_dashboard') + '#content-panel')
        
        # GET request - return content data for editing (for AJAX)
        # Convert datetime to string for JSON serialization
        if content.get('upload_date'):
            content['upload_date'] = content['upload_date'].isoformat()
        
        return jsonify({'success': True, 'content': content})
        
    except Exception as e:
        print(f"Error in edit_content: {e}")  # Server-side logging
        if request.method == 'GET':
            return jsonify({'success': False, 'message': f'Error loading content: {str(e)}'})
        else:
            if request.is_json or 'application/json' in request.headers.get('Accept', ''):
                return jsonify({'success': False, 'message': f'Error updating content: {str(e)}'})
            flash(f'Error updating content: {str(e)}')
            return redirect(url_for('guide_dashboard'))
    finally:
        cursor.close()
        connection.close()


# Route to delete content
@app.route('/guide/delete_content/<int:content_id>', methods=['DELETE'])
@require_user_type('guide')
def delete_content(content_id):
    """Delete Jharkhand tourism content (only by content owner)"""
    guide_id = session['user_id']
    connection = get_db_connection()
    
    if not connection:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Verify ownership
        cursor.execute("SELECT * FROM guide_uploads WHERE id = %s AND guide_id = %s", 
                      (content_id, guide_id))
        content = cursor.fetchone()
        
        if not content:
            return jsonify({'success': False, 'message': 'Content not found or access denied'})
        
        # Delete image file if exists
        if content.get('image_path'):
            image_file_path = os.path.join(app.config['UPLOAD_FOLDER'], os.path.basename(content['image_path']))
            if os.path.exists(image_file_path):
                try:
                    os.remove(image_file_path)
                    print(f"Deleted image file: {image_file_path}")
                except Exception as e:
                    print(f"Warning: Could not delete image file: {e}")
                    # Continue even if file deletion fails
        
        # Delete from database
        cursor.execute("DELETE FROM guide_uploads WHERE id = %s AND guide_id = %s", 
                      (content_id, guide_id))
        connection.commit()
        
        print(f"Deleted content ID {content_id} for guide {guide_id}")  # Server-side logging
        return jsonify({'success': True, 'message': 'Jharkhand content deleted successfully'})
        
    except Exception as e:
        print(f"Error in delete_content: {e}")  # Server-side logging
        return jsonify({'success': False, 'message': f'Error deleting content: {str(e)}'})
    finally:
        cursor.close()
        connection.close()


@app.route('/all_content')
def all_content():
    """Show all published Jharkhand tourism content"""
    # Route to show all published content (you can implement this later)
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    """Logout from Jharkhand Tourism platform"""
    session.clear()
    flash('You have been logged out successfully from Jharkhand Tourism platform.')
    return redirect(url_for('index'))

@app.route('/access_denied')
def access_denied():
    """Access denied page for Jharkhand Tourism platform"""
    return render_template('access_denied.html'), 403

@app.route('/debug_guide_profile')
@require_user_type('guide')
def debug_guide_profile():
    """Debug guide profile information for Jharkhand Tourism"""
    user_id = session['user_id']
    connection = get_db_connection()
    
    if connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM guides WHERE user_id = %s", (user_id,))
        guide_data = cursor.fetchone()
        cursor.close()
        connection.close()
        
        return f"User ID: {user_id}<br>Guide Data: {guide_data}"
    
    return "Database connection failed"

# Additional convenience routes for Jharkhand Tourism
@app.route('/login_tourist')
def old_login_tourist():
    """Backward compatibility route"""
    return redirect(url_for('login_tourist'))

@app.route('/login_guide')
def old_login_guide():
    """Backward compatibility route"""
    return redirect(url_for('login_guide'))

if __name__ == '__main__':
    app.run(debug=True)
