import os

from extensions import (
    Blueprint,
    session,
    redirect,
    request,
    render_template,
    app,
    url_for,
    os
)
from app.models.query_builder import (
    insert_user,
    fetch_course,
    check_access,
    insert_video
)

from app.youtube_api import (
    youtube_video_upload
)

from flask_dance.contrib.google import make_google_blueprint, google

api = Blueprint('user', 'user')

google_login = make_google_blueprint(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    redirect_url="/google/callback",
    scope=["profile", "email"]
)
app.register_blueprint(google_login, url_prefix='/googlelogin')

from flask import jsonify


@api.route('/')
def home():
    if session.get('google_oauth_token') or session.get('user_id'):
        course_detail = fetch_course('Blockchain')
        print(course_detail)
        return render_template('dashboard.html', course_detail=course_detail)
    else:
        session.clear()
    return redirect('/login')


@api.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@app.route("/google-login")
def googlelogin():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        if resp.get('hd') == 'rapidinnovation.dev':
            session['profile_url'] = resp['picture']
            session['hd'] = resp['hd']
            session['email'] = resp['email']
            session['user_id'] = resp['id']
            session['user_name'] = resp['name']
            return redirect('/')
        else:
            session.clear()
            return redirect('/login')
    return render_template('login.html')


@app.route('/google/callback')
def google_callback():
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        if resp.get('hd') == 'rapidinnovation.dev':
            session['profile_url'] = resp['picture']
            session['user_id'] = resp['id']
            session['user_name'] = resp['name']
            session['hd'] = resp['hd']
            session['email'] = resp['email']
            user_info = {
                'user_id': resp['id'],
                'profile_url': resp['picture'],
                'user_name': resp['name'],
                'email': resp['email']
            }
            insert_user(user_info)
        else:
            session.clear()
            return redirect('/login')
    return redirect('/')


@app.route('/video_upload', methods=['GET', 'POST'])
def video_upload():
    if session.get('google_oauth_token'):
        if not check_access(session['user_id'], 'staff'):
            return redirect('/')
        else:
            if request.method == 'GET':
                return render_template('upload_video.html')
            elif request.method == 'POST':
                response_data = {
                    'status': 404,
                    'message': 'Video is Uploading in Youtube.....'
                }
                if not request.form['course'] or not request.form['title'] or not request.form['description']:
                    response_data = {
                        'status': 404,
                        'message': 'Field is missing.'
                    }
                else:

                    files = request.files.getlist('video_file')
                    if not os.path.exists('static/video'):
                        os.mkdir('static/video')
                    app.config['UPLOAD_FOLDER'] = 'static/video/'
                    file_name = None
                    for file in files:
                        if file.filename.lower().endswith(('.mp4', '.avi')):
                            print(file.filename)
                            file_name = file.filename
                        else:
                            continue
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

                    arguments = {
                        "keywords": request.form['keywords'],
                        "title": request.form['title'],
                        "description": request.form['description'],
                        'category': '27',
                        'privacyStatus': 'unlisted',
                        'file': f'static/video/{file_name}'
                    }
                    video_id = youtube_video_upload(arguments)
                    video_info = {
                        'title': request.form['title'],
                        'description': request.form['description'],
                        'keywords': request.form['keywords'],
                        'video_id': video_id

                    }
                    insert_video(request.form['course'], video_info)
                    if video_id != 'Error':
                        os.remove(f'static/video/{file_name}')
                        response_data['status'] = 200
                        response_data['message'] = 'ok'
                        response_data['video_id'] = video_id
                return jsonify(response_data)

    else:
        return redirect('/login')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')