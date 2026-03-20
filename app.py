from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from datetime import timedelta
from ml_model import process_job_post, get_detector_info
from database import create_user, verify_user, save_job_detection, get_user_detections, get_user_profile, log_activity, get_user_activities, get_user_preferences, save_user_preferences, update_username, update_password, user_exists, save_csv_upload, get_user_csvs, delete_csv_upload, update_csv_filename
import os, csv, uuid
import openpyxl

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)



@app.context_processor
def inject_preferences():
    if 'username' in session:
        return {'user_preferences': get_user_preferences(session['username'])}
    return {'user_preferences': {'dark_mode': 0, 'compact_view': 0}}

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=24)

@app.route('/')
def index():
    # Redirect to dashboard if logged in, otherwise to login
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if verify_user(username, password):
            session['username'] = username
            log_activity(username, 'login', 'Logged in')
            return redirect(url_for('dashboard'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/check-username', methods=['POST'])
def check_username():
    username = request.json.get('username')
    exists = user_exists(username)
    return jsonify({'exists': exists})

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        username = request.form.get('username')
        if username and user_exists(username):
            return render_template('forgot_password.html', success='Password reset instructions would be sent to your email')
        else:
            return render_template('forgot_password.html', error='Username not found')
    return render_template('forgot_password.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        error = None
        
        if not username:
            error = 'Username is required'
        elif not password:
            error = 'Password is required'
        elif password != confirm_password:
            error = 'Passwords do not match'
        elif len(username) < 3:
            error = 'Username must be at least 3 characters long'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters long'
        
        if error:
            return render_template('register.html', error=error)
        
        if not create_user(username, password):
            error = 'Username already exists'
            return render_template('register.html', error=error)
        
        log_activity(username, 'register', 'Account created')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    recent_activities = get_user_activities(session['username'], limit=5)
    return render_template('dashboard.html', username=session['username'], recent_activities=recent_activities)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_data = get_user_profile(session['username'])
    recent_activities = get_user_activities(session['username'], limit=4)
    
    return render_template('profile.html', user=user_data, recent_activities=recent_activities, username=session['username'])

@app.route('/update-profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    new_username = request.json.get('username')
    account_status = request.json.get('accountStatus', 'Active')
    member_since = request.json.get('memberSince')
    total_detections = request.json.get('totalDetections', 0)
    
    if new_username and new_username != session['username']:
        if update_username(session['username'], new_username):
            session['username'] = new_username
            log_activity(new_username, 'profile', 'Updated account information')
            return jsonify({
                'success': True, 
                'username': new_username,
                'accountStatus': account_status,
                'memberSince': member_since,
                'totalDetections': total_detections
            })
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    log_activity(session['username'], 'profile', 'Updated account information')
    return jsonify({
        'success': True, 
        'username': session['username'],
        'accountStatus': account_status,
        'memberSince': member_since,
        'totalDetections': total_detections
    })

@app.route('/update-password', methods=['POST'])
def update_password_route():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    new_password = request.json.get('newPassword')
    if new_password:
        update_password(session['username'], new_password)
        log_activity(session['username'], 'security', 'Changed password')
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid password'})

@app.route('/update-contact', methods=['POST'])
def update_contact():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    
    log_activity(session['username'], 'profile', 'Updated contact information')
    return jsonify({'success': True, 'email': request.json.get('email'), 'phone': request.json.get('phone'), 'country': request.json.get('country')})

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        dark_mode = int(request.form.get('dark_mode', 0))
        compact_view = int(request.form.get('compact_view', 0))
        save_user_preferences(session['username'], dark_mode, compact_view)
        log_activity(session['username'], 'settings', 'Updated appearance settings')
        return redirect(url_for('settings'))
    
    preferences = get_user_preferences(session['username'])
    return render_template('settings.html', username=session['username'], preferences=preferences)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/job-post-detector', methods=['GET', 'POST'])
def job_post_detector():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    result = None
    if request.method == 'POST':
        job_title = request.form.get('job_title', '')
        company_name = request.form.get('company_name', '')
        job_description = request.form.get('job_description', '')
        salary = request.form.get('salary', '')
        location = request.form.get('location', '')
        
        # Validate inputs
        if not all([job_title, company_name, job_description]):
            error = 'Please fill in all required fields'
            return render_template('job_post_detector.html', username=session['username'], error=error)
        
        result = process_job_post(job_description, job_title, company_name, salary)
        
        if result:
            save_job_detection(
                session['username'],
                job_title,
                company_name,
                job_description,
                salary,
                location,
                result.get('prediction', 'Unknown'),
                result.get('confidence', 0.0)
            )
            log_activity(session['username'], 'detection', f'Analyzed job post: {job_title}')
    
    # Get model information
    model_info = get_detector_info()
    
    return render_template('job_post_detector.html', username=session['username'], result=result, model_info=model_info)

@app.route('/model-info')
def model_info():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    info = get_detector_info()
    return render_template('model_info.html', username=session['username'], model_info=info)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    username = session['username']
    error = None
    ALLOWED = {'.xls', '.xlsx'}
    if request.method == 'POST':
        file = request.files.get('csv_file')
        ext = os.path.splitext(file.filename)[1].lower() if file and file.filename else ''
        if not file or not file.filename or ext not in ALLOWED:
            error = 'Only Excel files (.xls, .xlsx) are allowed. PDF and other file types are not accepted.'
        else:
            from datetime import datetime
            temp_name = f"temp_{uuid.uuid4().hex}{ext}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], temp_name)
            file.save(filepath)
            new_id = save_csv_upload(username, temp_name, file.filename)
            date_str = datetime.now().strftime('%d%m%Y')
            final_name = f"{new_id}{date_str}{ext}"
            final_path = os.path.join(app.config['UPLOAD_FOLDER'], final_name)
            os.rename(filepath, final_path)
            update_csv_filename(new_id, final_name)
            log_activity(username, 'upload', f'Uploaded file: {file.filename}')
            return redirect(url_for('upload'))
    user_csvs = get_user_csvs(username)
    return render_template('upload.html', username=username, user_csvs=user_csvs, error=error)

@app.route('/csv/download/<int:csv_id>')
def csv_download(csv_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    csvs = get_user_csvs(session['username'])
    entry = next((c for c in csvs if c['id'] == csv_id), None)
    if not entry:
        return 'Not found', 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], entry['filename'], as_attachment=True, download_name=entry['original_filename'])

@app.route('/csv/view/<int:csv_id>')
def csv_view(csv_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    csvs = get_user_csvs(session['username'])
    entry = next((c for c in csvs if c['id'] == csv_id), None)
    if not entry:
        return 'Not found', 404
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], entry['filename'])
    ext = os.path.splitext(entry['original_filename'])[1].lower()
    if ext == '.csv':
        with open(filepath, newline='', encoding='utf-8-sig') as f:
            rows = list(csv.reader(f))
    else:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        ws = wb.active
        rows = [[str(c) if c is not None else '' for c in row] for row in ws.iter_rows(values_only=True)]
        wb.close()
    return jsonify({'filename': entry['original_filename'], 'rows': rows})

@app.route('/csv/update/<int:csv_id>', methods=['POST'])
def csv_update(csv_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    csvs = get_user_csvs(session['username'])
    entry = next((c for c in csvs if c['id'] == csv_id), None)
    if not entry:
        return jsonify({'success': False, 'message': 'File not found'}), 404
    rows = request.json.get('rows', [])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], entry['filename'])
    ext = os.path.splitext(entry['original_filename'])[1].lower()
    try:
        if ext == '.csv':
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                csv.writer(f).writerows(rows)
        else:
            wb = openpyxl.Workbook()
            ws = wb.active
            for row in rows:
                ws.append(row)
            wb.save(filepath)
        log_activity(session['username'], 'edit', f'Edited file: {entry["original_filename"]}')
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/csv/delete/<int:csv_id>', methods=['POST'])
def csv_delete(csv_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    filename = delete_csv_upload(csv_id, session['username'])
    if filename:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        log_activity(session['username'], 'delete', f'Deleted CSV id {csv_id}')
    return redirect(url_for('upload'))

if __name__ == '__main__':
    app.run(debug=True)
