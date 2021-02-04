from flask import jsonify, Flask, request
from flask_sqlalchemy import SQLAlchemy
from random import choice, shuffle
import time


app = Flask(__name__)

# Connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


SECONDS_IN_30_DAYS = 86400 * 30
START_TIME = round(time.time())
END_TIME = START_TIME + SECONDS_IN_30_DAYS


# User TABLE Configuration
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    token = db.Column(db.String(250), unique=True, nullable=False)
    start_time = db.Column(db.Integer, unique=False, nullable=False)
    end_time = db.Column(db.Integer, unique=False, nullable=False)
    app1_status = db.Column(db.Integer, unique=False, nullable=False)
    app2_status = db.Column(db.Integer, unique=False, nullable=False)
    app3_status = db.Column(db.Integer, unique=False, nullable=False)
    app4_status = db.Column(db.Integer, unique=False, nullable=False)
    app5_status = db.Column(db.Integer, unique=False, nullable=False)
    app6_status = db.Column(db.Integer, unique=False, nullable=False)
    app7_status = db.Column(db.Integer, unique=False, nullable=False)
    app8_status = db.Column(db.Integer, unique=False, nullable=False)
    app9_status = db.Column(db.Integer, unique=False, nullable=False)
    app10_status = db.Column(db.Integer, unique=False, nullable=False)
    active_status = db.Column(db.Integer, unique=False, nullable=False)

    def to_dict(self):
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary


@app.route('/')
def home():
    return '<h1>This is the home page and there is nothing to see here</h1>'


# Read Record
@app.route('/all')
def all_users():
    users = db.session.query(User).all()
    return jsonify(users=[user.to_dict() for user in users]), 200


@app.route('/token')
def get_user_from_token():
    token = request.args.get('token')
    user = db.session.query(User).filter_by(token=token).first()

    if user:
        return jsonify(user=user.to_dict()), 200
    else:
        return jsonify(error={'Not Found': 'Sorry. That token does not exist on our database'}), 404


@app.route('/check_token_validity')
def registering_users_token_validity():
    token = request.args.get('token') + '\n'

    with open('used tokens.txt', 'r') as f:
        used_tokens = f.readlines()
        f.close()

    with open('unused tokens.txt', 'r') as f:
        unused_tokens = f.readlines()
        f.close()

    if token in used_tokens:
        return jsonify(error="That token is already used"), 404

    elif token in unused_tokens:

        return jsonify(success="That token exists but hasn't been used "), 200

    else:
        return jsonify(error="That token does not exist!"), 404


@app.route('/change_token/<string:token>', methods=['PATCH'])
def change_token(token):
    new_token = request.args.get('new_token')

    user = db.session.query(User).filter_by(token=token).first()

    if user:
        user.token = new_token
        return jsonify(sucess={"Success": "Successfully changed the token"}), 200

    else:
        return jsonify(error={'error': 'That token is not registered'}), 404


@app.route('/email')
def get_user_from_email():
    email = request.args.get('email')
    user = db.session.query(User).filter_by(email=email.lower()).first()

    if user:
        return jsonify(user=user.to_dict()), 200
    else:
        return jsonify(error={'Not Found': 'Sorry. That email does not exist on our database'}), 404


# Create user
@app.route('/add', methods=['POST'])
def add_user():
    email = request.form.get('email').lower()
    new_user = User(
        email=email,
        token=request.form.get('token'),
        start_time=START_TIME,
        end_time=END_TIME,
        app1_status=0,
        app2_status=0,
        app3_status=0,
        app4_status=0,
        app5_status=0,
        app6_status=0,
        app7_status=0,
        app8_status=0,
        app9_status=0,
        app10_status=0,
        active_status=0
    )

    db.session.add(new_user)
    db.session.commit()

    with open('unused tokens.txt', 'r') as f:
        unused_tokens = f.readlines()
        f.close()

    token = request.form.get('token') + '\n'

    with open('used tokens.txt', 'a') as f:
        f.write(token + '\n')
        f.close()

    unused_tokens.remove(token)

    with open('unused tokens.txt', 'w') as f:
        for token in unused_tokens:
            f.write(token)
        f.close()

    return jsonify(response={'Success': 'Successfully added a new user'})


# Renew license
@app.route('/renew/<string:email>', methods=['PATCH'])
def renew_license(email):
    new_start_time = START_TIME
    new_end_time = END_TIME
    user = db.session.query(User).filter_by(email=email).first()

    if user:
        user.start_time = new_start_time
        user.end_time = new_end_time
        db.session.commit()
        return jsonify(response={'Success': 'Successfully renewed the license'}), 200
    else:
        return jsonify(error={'Not Found': 'Sorry. No user with that email is on our database'}), 404


@app.route('/check_validity/<string:token>')
def check_validity(token):
    user = db.session.query(User).filter_by(token=token).first()
    if user:
        if user.start_time < user.end_time:
            return jsonify(sucess={'Success': 'The user is still valid'}), 200
        else:
            return jsonify(failure={'Failure': 'The user has expired'}), 404
    else:
        return jsonify(error={'Not Found': 'Sorry. No user with that token is on our database'}), 404


@app.route('/check_app_status/<string:token>')
def check_app_status(token):
    user = db.session.query(User).filter_by(token=token).first()
    if user:
        app_no = int(request.args.get('app_no'))
        if app_no == 1:
            status = user.app1_status
        elif app_no == 2:
            status = user.app2_status
        elif app_no == 3:
            status = user.app3_status
        elif app_no == 4:
            status = user.app4_status
        elif app_no == 5:
            status = user.app5_status
        elif app_no == 6:
            status = user.app6_status
        elif app_no == 7:
            status = user.app7_status
        elif app_no == 8:
            status = user.app8_status
        elif app_no == 9:
            status = user.app9_status
        else:
            status = user.app10_status

        return jsonify(status={'Status': status})
    else:
        return jsonify(error={'Not Found': 'Sorry. No user with that token is on our database'}), 404


@app.route('/change_app_status/<string:token>', methods=['PATCH'])
def change_app_status(token):
    user = db.session.query(User).filter_by(token=token).first()
    if user:
        app_no = int(request.args.get('app_no'))
        if app_no == 1:
            user.app1_status = 1
        elif app_no == 2:
            user.app2_status = 1
        elif app_no == 3:
            user.app3_status = 1
        elif app_no == 4:
            user.app4_status = 1
        elif app_no == 5:
            user.app5_status = 1
        elif app_no == 6:
            user.app6_status = 1
        elif app_no == 7:
            user.app7_status = 1
        elif app_no == 8:
            user.app8_status = 1
        elif app_no == 9:
            user.app9_status = 1
        elif app_no == 10:
            user.app10_status = 1
        else:
            pass

        db.session.commit()

        return jsonify(success={'Success': f'Successfully changed the status of app number {app_no}'}), 200
    else:
        return jsonify(error={'Not Found': 'Sorry. No user with that token is on our database'}), 404


@app.route('/check_active_status/<string:token>')
def check_active_status(token):
    user = db.session.query(User).filter_by(token=token).first()

    if user:
        if user.active_status == 0:
            return jsonify(the_status_code={'Status': user.active_status},
                           Success={'Success': f"App status is {user.active_status}. App not running",
                                    'Status code': user.active_status}), 200
        else:
            return jsonify(the_status_code={'Status': user.active_status},
                           Error={'Error': f'App status is {user.active_status}. App is running',
                                  'Status code': user.active_status}), 404


@app.route('/change_active_status/<string:token>', methods=['PATCH'])
def change_active_status(token):
    user = db.session.query(User).filter_by(token=token).first()

    if user:
        user.active_status = request.args.get('new_active_status')
        db.session.commit()
        return jsonify(Success={'Success': "Successfully changed the active status"}), 200
    else:
        return jsonify(Error={'Error': 'No such user with that token'}), 404


@app.route('/generate_token/<int:number>')
def generate_token(number):
    def generate():
        letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
                   'u',
                   'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O',
                   'P',
                   'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
        numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

        token_letters = [choice(letters) for _ in range(20)]
        token_numbers = [choice(numbers) for _ in range(12)]

        token_list = token_letters + token_numbers
        shuffle(token_list)
        generated_token = ''.join(token_list)

        token = ''

        position = 0
        for j in range(len(generated_token)):
            if position == 4:
                token += '-'
                position = 0
            token += generated_token[j]
            position += 1

        return token

    with open('unused tokens.txt', 'r') as f:
        unused_tokens = f.readlines()
        f.close()

    with open('used tokens.txt', 'r') as f:
        used_tokens = f.readlines()
        f.close()

    for i in range(number):
        new_token = generate()

        if new_token not in unused_tokens and new_token not in used_tokens:
            with open('unused tokens.txt', 'a') as f:
                f.write(f'{new_token}\n')
                f.close()

    return jsonify(Success={'Success': f"Successfully generated {number} new tokens!"}), 200


@app.route('/fetch_token')
def fetch_token():
    with open('unused tokens.txt', 'r') as f:
        tokens = f.readlines()
        new_token = choice(tokens).strip('\n')
        f.close()

    return jsonify(Success={'New token': f"{new_token}"})


if __name__ == '__main__':
    app.run(debug=True)
