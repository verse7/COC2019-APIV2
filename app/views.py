import os
import jwt
from functools import wraps
from flask import render_template, request, jsonify
from app.forms import *
from app.models import *
from app.util import *
from app import app, db, csrf
from werkzeug.utils import secure_filename

###
# Utility functions
###

# jwt decorator


def form_errors(form):
    error_messages = []
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages


@app.route('/auth/register', methods=['POST'])
def register():
  form = RegistrationForm.from_json(request.json)

  if form.validate_on_submit():
    firstname = escape(form.firstname.data)
    lastname = escape(form.lastname.data)
    email = escape(form.email.data)
    password = escape(form.password.data)
    
    try:
      user = User(firstname, lastname, email, password)
      db.session.add(user)
      db.session.commit()

      data = {}
      data['id'] = user.id
      data['firstname'] = user.firstname
      data['lastname'] = user.lastname
      data['email'] = user.email

      response = generate_api_response(21, 'success', 
                  ['Successfully registered user'], data, 200)
    except:
      response = generate_api_response(41, 'error', 
                  ['A user already exists with these credentials'], {}, 200)

  else:
    response = generate_api_response(40, 'error', 
                form_errors(form), {}, 200)

  data, status = response
  return jsonify(data), status


@app.route('/auth/login', methods=['POST'])
def login():
  form = RegistrationForm.from_json(request.json)

  if form.validate_on_submit():
    email = escape(form.email.data)
    password = escape(form.password.data)
    
    # try to find a user with a matching email address
    user = User.query.filter_by(email=email).first()

    if user:
      if check_password_hash(user.password, password):
        token = jwt.encode({'id': user.id}, 
                          current_app.config['SECRET_KEY'], 
                          algorithm='HS256').decode('utf-8')
        # set the token on the response cookie with http only
        # and add the csrf token for subsequent responses
        session.clear()
        session['api_token'] = token
        response = generate_api_response(20, 'success', 
                  ['Login Successful'], {}, 200)
      else:
        response = generate_api_response(43, 'error', 
                  ['Incorrect email or password'], {}, 200)
    else:
      response = generate_api_response(43, 'error', 
                ['Incorrect email or password'], {}, 200)
  else:
    response = generate_api_response(40, 'error', 
                form_errors(form), {}, 200)

  data, status = response
  return jsonify(data), status


@app.route('/auth/logout')
def logout():
  session.clear()

  data, status = generate_api_response(20, 'success', 
                ['Successfully logged out'], {}, 200)
  return jsonify(data), status


@app.route('/events', methods=['GET', 'POST'])
def create_event():
  if request.method == 'GET':
    events = [{'title': e.title, 'location': e.location, 
                'manpower_quota': e.manpower_quota, 'attendees': e.attendees } 
              for e in Event.query.all()]
    
    response = generate_api_response(20, 'success', 
                ['Successfully fetched all events'], {'events': events}, 200)
  else:
    form = EventForm()

    if form.validate_on_submit():
      try:
        image = form.image.data
        details = json.loads(form.details.data.replace('\'', '"'))
        filename = secure_filename(image.filename)

        CDNManager().upload(image, filename)

        event = Event(CDNManager().get_file_url(filename), escape(details['title']), escape(details['location']), 
                        escape(details['manpower_quota']))
        db.session.add(event)
        db.session.commit()
        response = generate_api_response(21, 'success', 
                    ['Successfully created event'], {}, 200)
      except:
        response = generate_api_response(41, 'error', 
                    ['A cleanup event is already created for this location'], {}, 200)
    else:
      response = generate_api_response(40, 'error', 
                form_errors(form), {}, 200)

  data, status = response
  return jsonify(data), status


@app.route('/<event_id>/subscribe', methods=['POST'])
def subscribe(event_id):
  try:
    #get user_id parameters
    user_id = request.args.get('user')

    #find event with matching id
    event = Event.query.filter_by(id=event_id).first()
    
    #find user with matching id
    user = User.query.get(user_id)
  
    event.attendees.append(user)
    db.session.add(event)
    db.session.commit()
    response = generate_api_response(21, 'success', 
                    ['Successfully subscribed to an event'], {}, 200)
  except:
    response = generate_api_response(41, 'error', 
                    ['An error has occurred'], {}, 200)
  
  data, status = response
  return jsonify(data), status



@app.route('/groups', methods=["POST"]) 
@gives_user
def create_group(user):
  form = GroupForm.from_json(request.json)

  if form.validate_on_submit():
    name = form.name.data

    # try:
    group = Group(name)
    print(user)
    group.members.append(user)
    db.session.add(group)
    db.session.commit()

    data = {}
    data['id'] = group.id
    data['name'] = group.name

    response = generate_api_response(21, 'success',
                ['Successfully created group'], data, 200)

  else:
    response = generate_api_response(40, 'error', 
                form_errors(form), {}, 200)

  data, status = response
  return jsonify(data), status


@app.route('/groups', methods=["GET"])
def get_groups():
  data = [{"id": g.id, "name": g.name} for g in Group.query.all()]
  
  response = generate_api_response(21, 'success',
              ['Successfully fetched groups'], {"groups":data}, 200)

  data, status = response
  return jsonify(data), status  


@app.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
  group = Group.query.get(group_id)
  if not group:
    response = generate_api_response(40, 'error', ['This group does not exist'], {}, 200)
    data, status = response
    return jsonify(data), status

  data={}
  data["id"] = group.id
  data["name"] = group.name
  data["members"] = [{"id": m.id, "firstname": m.firstname, "lastname": m.lastname, "points": m.points} for m in group.members]

  response = generate_api_response(21, 'success',
              ['Successfully fetched groups'], {"group":data}, 200)

  data, status = response
  return jsonify(data), status



@app.route('/groups/<group_id>', methods=["PUT"])
@gives_user
def add_user(user, group_id):
  group = Group.query.get(group_id)
  if not group:
    response = generate_api_response(40, 'error', ['This group does not exist'], {}, 200)
    data, status = response
    return jsonify(data), status

  try:
    group.members.append(user)
    db.session.commit()
    response = generate_api_response(20, 'success', ['Successfully added user to the group'], {}, 200)
  except:
    response = generate_api_response(40, 'error', ['There was a problem in adding the member'], {}, 200)

  data, status = response
  return jsonify(data), status

@app.route('/points', methods=['GET'])
def points():
    try:
        #get event_id and user_id parameters
        user_id = request.args.get('user')
        
        #find user with matching id
        user = User.query.filter_by(id=user_id).first()

        points = {"points": user.points}
        response = generate_api_response(20, 'success', 
                    ['Successfully fetched user points'], points, 200)
    except:
        response = generate_api_response(41, 'error', 
                    ['An error has occurred'], {}, 200)

    data, status = response
    return jsonify(data), status


@app.after_request
def add_header(response):
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
