from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Brutus0309!@localhost/gymmanagement'

db = SQLAlchemy(app)
ma = Marshmallow(app)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)

class WorkoutSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    session_date = db.Column(db.Date, nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    calories_burned = db.Column(db.Integer, nullable=False)
    member = db.relationship('Member', backref=db.backref('workout_sessions'))

with app.app_context():
    db.create_all()

class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member
        sqla_session = db.session

class WorkoutSessionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WorkoutSession
        sqla_session = db.session

member_schema = MemberSchema()
members_schema = MemberSchema(many=True)
workoutsession_schema = WorkoutSessionSchema()
workoutsessions_schema = WorkoutSessionSchema(many=True)


@app.route('/members', method=['POST'])
def add_member():
    try:
        name = request.json['name']
        email = request.json['email']
        phone_number = request.json['phone_number']

        new_member = Member(name=name, email=email, phone_number=phone_number)
        db.session.add(new_member)
        db.session.commit()

        return member_schema.jsonify(new_member), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members', methods=['GET'])
def get_members():
    try:
        all_members = Member.query.all()
        result = members_schema.dump(all_members)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:id>', methods=['GET'])
def get_member(id):
    try:
        member = Member.query.get_or_404(id)
        return member_schema.jsonify(member), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/members/<int:id>', methods=['PUT'])
def update_member(id):
    try:
        member = Member.query.get_or_404(id)

        name = request.json.get('name', member.name)
        email = request.json.get('email', member.email)
        phone_number = request.json.get('phone_number', member.phone_number)

        member.name = name
        member.email = email
        member.phone_number = phone_number

        db.session.commit()

        return member_schema.jsonify(member), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/members/<int:id>', methods=['DELETE'])
def delete_member(id):
    try:
        member = Member.query.get_or_404(id)
        db.session.delete(member)
        db.session.commit()
        return jsonify({'message': 'Member deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/workoutsessions', methods=['POST'])
def add_workout_session():
    try:
        member_id = request.json['member_id']
        session_date = request.json['session_date']
        duration_minutes = request.json['duration_minutes']
        calories_burned = request.json['calories_burned']

        new_session = WorkoutSession(
            member_id=member_id,
            session_date=session_date,
            duration_minutes=duration_minutes,
            calories_burned=calories_burned
        )
        db.session.add(new_session)
        db.session.commit()

        return workoutsession_schema.jsonify(new_session), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/workoutsessions', methods=['GET'])
def get_workout_sessions():
    try:
        all_sessions = WorkoutSession.query.all()
        result = workoutsessions_schema.dump(all_sessions)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/workoutsessions/<int:id>', methods=['GET'])
def get_workout_session(id):
    try:
        session = WorkoutSession.query.get_or_404(id)
        return workoutsession_schema.jsonify(session), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/workoutsessions/<int:id>', methods=['PUT'])
def update_workout_session(id):
    try:
        session = WorkoutSession.query.get_or_404(id)

        member_id = request.json.get('member_id', session.member_id)
        session_date = request.json.get('session_date', session.session_date)
        duration_minutes = request.json.get('duration_minutes', session.duration_minutes)
        calories_burned = request.json.get('calories_burned', session.calories_burned)

        session.member_id = member_id
        session.session_date = session_date
        session.duration_minutes = duration_minutes
        session.calories_burned = calories_burned

        db.session.commit()

        return workoutsession_schema.jsonify(session), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/workoutsessions/<int:id>', methods=['DELETE'])
def delete_workout_session(id):
    try:
        session = WorkoutSession.query.get_or_404(id)
        db.session.delete(session)
        db.session.commit()
        return jsonify({'message': 'Workout session deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@app.route('/members/<int:member_id>/workoutsessions', methods=['GET'])
def get_workouts_for_member(member_id):
    try:
        member = Member.query.get_or_404(member_id)
        sessions = WorkoutSession.query.filter_by(member_id=member_id).all()
        result = workoutsessions_schema.dump(sessions)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    app.run(debug=True)
