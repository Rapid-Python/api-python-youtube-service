from extensions import (
    Blueprint,
    session,
    redirect,
    request,
    render_template,
    app,
    url_for,
    os,
    jsonify
)
from app.models.query_builder import (
    insert_user,
    fetch_course,
    check_access,
    insert_video,
    fetch_courses,
    fetch_users,
    insert_course,
    update_course,
    delete_course,
    course_video,
    course_video_user,
    user_active,
    fetch_user,
    fetch_active_courses,
    video_info,
    fetch_course_by_category,
    fetch_course_by_title
)

from app.youtube_api import (
    youtube_video_upload
)

from flask_dance.contrib.google import make_google_blueprint, google
from app.upload_video import Video

api = Blueprint('user', 'user')

google_login = make_google_blueprint(
    client_id=os.getenv('client_id'),
    client_secret=os.getenv('client_secret'),
    redirect_url="/google/callback",
    scope=["profile", "email"]
)
app.register_blueprint(google_login, url_prefix='/googlelogin')


@api.route('/')
def home():
    if session.get('user_id') or user_active(session.get('user_id')):
        return render_template('dashboard.html', user_info=fetch_user(session.get('user_id')))
    else:
        session.clear()
    return redirect('/login')


@api.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id') or user_active(session.get('user_id')):
        return redirect('/')
    return render_template('login.html')


@app.route("/google-login")
def googlelogin():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        session['user_id'] = resp['id']
        return redirect('/')
    return render_template('login.html')


@app.route('/google/callback')
def google_callback():
    resp = google.get("oauth2/v2/userinfo")
    if resp.ok:
        resp = resp.json()
        session['user_id'] = resp['id']
        user_info = {
            'user_id': resp['id'],
            'profile_url': resp['picture'],
            'user_name': resp['name'],
            'email': resp['email'],
            'active': True
        }
        insert_user(user_info)
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/manage/<manage_type>/', methods=['GET', 'POST'])
@app.route('/manage/<manage_type>/<object_id>', methods=['GET'])
@app.route('/manage/<manage_type>/<object_id>/', methods=['PUT', 'DELETE'])
def admin_dashboard(manage_type='user', object_id=None):
    response_data = redirect('/')
    if not session.get('user_id') or not user_active(session.get('user_id')) or \
            not check_access(session.get('user_id'), 'admin'):
        response_data = redirect('/')
    else:
        response_json = {
            'status': 404,
            'message': 'Something went wrong.'
        }
        if request.method == 'GET':
            if manage_type.lower() == 'user':
                response_data = render_template('manage.html', manage_type=manage_type, data_list=fetch_users(),
                                                user_info=fetch_user(session.get('user_id')))
            elif manage_type.lower() == 'course':
                if object_id:
                    response_data = render_template('course_detail.html', manage_type='Course Detail', data_list=course_video(object_id),
                                                    user_info=fetch_user(session.get('user_id')))
                else:
                    response_data = render_template('manage.html', manage_type=manage_type, data_list=fetch_courses(),
                                                user_info=fetch_user(session.get('user_id')))
            else:
                response_data = redirect('/')
        elif request.method == 'POST':
            if manage_type.lower() == 'course':
                course_detail = request.form.to_dict(flat=True)
                course_detail['id'] = insert_course(course_detail)
                if course_detail.get('_id'):
                    del course_detail['_id']
                response_json = {
                    'status': 200,
                    'message': 'ok',
                    'course_detail': course_detail
                }
                response_data = jsonify(response_json)
        elif request.method == 'PUT':
            course_detail = request.form.to_dict(flat=True)
            course_detail['active'] = True if course_detail['active'].capitalize() == 'True' else False
            update_course(object_id, course_detail)
            response_json = {
                'status': 200,
                'message': 'ok',
            }
            response_data = jsonify(response_json)
        elif request.method == 'DELETE':
            delete_course(object_id)
            response_json = {
                'status': 200,
                'message': 'ok',
            }
            response_data = jsonify(response_json)
    return response_data


@app.route('/video_upload', methods=['GET', 'POST'])
def video_upload():
    response_data = None
    if not session.get('user_id') or not user_active(session.get('user_id')) or \
            not check_access(session.get('user_id'), 'staff'):
        response_data = redirect('/')
    else:
        if request.method == 'GET':
            return render_template('upload_video.html', user_info=fetch_user(session.get('user_id')), course_list=[{"id": i['_id'], "title": i['title']} for i in fetch_courses()])
        elif request.method == 'POST':
            response_json = {
                'status': 404,
                'message': 'Something went wrong.'
            }
            """if not request.form['course'] or not request.form['title'] or not request.form['description'] or len(request.files.getlist('video_file')) == 0:
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
                    if file.filename.lower().endswith(('.mp4',)):
                        print(file.filename)
                        file_name = file.filename
                    else:
                        continue
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
                    v = Video()
                    v.upload_video(f'static/video/{file_name}', f'{fetch_course(request.form["course"])["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{file_name.split(".")[-1]}')
                    # arguments = {
                    #                         "keywords": request.form['keywords'],
                    #                         "title": request.form['title'],
                    #                         "description": request.form['description'],
                    #                         'category': '27',
                    #                         'privacyStatus': 'unlisted',
                    #                         'file': f'static/video/{file_name}'
                    #                     }
                  #  video_id = youtube_video_upload(arguments)
                    video_info = {
                        'title': request.form['title'],
                        'description': request.form['description'],
                      #  'keywords': request.form['keywords'],
                        'video_path': f'{fetch_course(request.form["course"])["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{file_name.split(".")[-1]}',
                        'active': True
                    }
                    insert_video(request.form['course'], video_info)

                    os.remove(f'static/video/{file_name}')
                    response_data['status'] = 200
                    response_data['message'] = 'File uploaded successfully.'
                return jsonify(response_data)"""
            if not request.form['course'] or not request.form['title'] or not request.form['description'] or not request.form['file_name']:
                response_json = {
                    'status': 404,
                    'message': 'Field is missing.'
                }
            else:
                v = Video()
                response_json['presigned_object'] = v.generate_pre_signed_url(
                    f'{fetch_course(request.form["course"])["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}')
                video_info = {
                    'title': request.form['title'],
                    'description': request.form['description'],
                    #  'keywords': request.form['keywords'],
                    'video_path': f'{fetch_course(request.form["course"])["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}',
                    'active': True
                }
                insert_video(request.form['course'], video_info)
                response_json['status'] = 200
                response_json['message'] = 'ok'
            response_data = jsonify(response_json)
    return response_data


@app.route('/course/<course_id>', methods=['GET'])
def course_dashboard(course_id):
    response_data = redirect('/')
    if not session.get('user_id') or not user_active(session.get('user_id')) or \
            not check_access(session.get('user_id'), 'staff'):
        response_data = redirect('/')
    else:
        response_data = render_template('course.html',
                                        course=fetch_course(course_id),
                                        user_info=fetch_user(session.get('user_id'))
                        )
    return response_data

@app.route('/course/video/<course_id>/')
def get_video_list(course_id=None):
    response_data = {
        'status': 404,
        'message': 'Something went wrong.',
    }
    if not session.get('user_id') or not user_active(session.get('user_id')):
        response_data['message'] = 'unauthorized user'
    else:
        video_list = course_video_user(course_id)
        for i in video_list:
            i['_id'] = str(i['_id'])
        response_data['status'] = 200
        response_data['message'] = 'ok'
        response_data['items'] = video_list
    return jsonify(response_data)



@app.route('/course/<course_id>/<video_id>', methods=['GET'])
def get_video_url(course_id=None, video_id=None):
    response_data = redirect('/')
    if not session.get('user_id') or not user_active(session.get('user_id')):
        response_data = redirect('/')
    else:
        if course_id:
            if video_id:
                video_data = video_info(video_id)
                v = Video()
                response_json = {
                    'status': 200,
                    'video_url': v.generate_url(video_data['video_path'])
                }
                response_data = response_json
    return response_data


# @app.route('/video_upload', methods=['POST'])
# def get_signed_url():
#     response_data = {
#         'status': 404,
#         'message': 'Something went wrong.'
#     }
#     if not session.get('user_id') or not user_active(session.get('user_id')) or not check_access(session.get('user_id'), 'staff'):
#         response_data['message'] = 'unauthorized user.'
#     else:
#         v = Video()
#         response_data['presigned_object'] = v.generate_pre_signed_url(f'{fetch_course(request.form["course"])["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}')
#         video_info = {
#             'title': request.form['title'],
#             'description': request.form['description'],
#             #  'keywords': request.form['keywords'],
#             'video_path': f'{fetch_course(request.form["course"])["title"].replace("/", "").lower()}/{request.form["title"].replace("/", "")}.{request.form["file_name"].split(".")[-1]}',
#             'active': True
#         }
#         insert_video(request.form['course'], video_info)
#         response_data['status'] = 200
#         response_data['message'] = 'ok'
#         return jsonify(response_data)


@app.route('/category/<category_select>', methods=['GET'])
def category_search(category_select=None):
    response_data = {
        'status': 404,
        'message': 'Something went wrong.',
    }
    response_data['items'] = fetch_course_by_category(category_select)
    for i in response_data['items']:
        i['_id'] = str(i['_id'])
    response_data['status'] = 200
    response_data['message'] = 'ok'
    return jsonify(response_data)



@app.route('/search/<search_keyword>', methods=['GET'])
def title_search(search_keyword=None):
    response_data = {
        'status': 404,
        'message': 'Something went wrong.',
    }
    response_data['items'] = fetch_course_by_title(search_keyword)
    for i in response_data['items']:
        i['_id'] = str(i['_id'])
    response_data['status'] = 200
    response_data['message'] = 'ok'
    return jsonify(response_data)


@app.route('/active_course')
def active_course():
    response_data = {
        'status': 404,
        'message': 'Something went wrong.',
    }
    response_data['items'] = fetch_active_courses()
    for i in response_data['items']:
        i['_id'] = str(i['_id'])
    response_data['status'] = 200
    response_data['message'] = 'ok'
    return jsonify(response_data)
