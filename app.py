from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from ml_model import process_job_post, get_detector_info
from database import create_user, verify_user, save_job_detection, get_user_detections, get_user_profile, log_activity, get_user_activities, get_user_preferences, save_user_preferences

app = Flask(__name__)
app.secret_key = 'your_secret_key_change_this'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)



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
        session['username'] = username
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', username=session['username'])

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_data = get_user_profile(session['username'])
    recent_activities = get_user_activities(session['username'], limit=4)
    
    return render_template('profile.html', user=user_data, recent_activities=recent_activities)

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
    
    # Get model information
    model_info = get_detector_info()
    
    return render_template('job_post_detector.html', username=session['username'], result=result, model_info=model_info)

@app.route('/model-info')
def model_info():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    info = get_detector_info()
    return render_template('model_info.html', username=session['username'], model_info=info)

if __name__ == '__main__':
    app.run(debug=True)
