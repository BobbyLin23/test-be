from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask.json import jsonify


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/test-db"
db = SQLAlchemy(app)


class BaseModel(object):
    def to_json(self):
        fields = self.__dict__
        if '_sa_instance_state' in fields:
            del fields['_sa_instance_state']

        return fields


class User(db.Model, BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.BigInteger, primary_key=True)
    username = db.Column(db.String(80), unique=False, nullable=False)
    gender = db.Column(db.String(16), nullable=False)


@app.route('/users', methods=['GET'])
def get_user_list():
    users = User.query.order_by(User.id)
    page_obj = users.paginate(
        page=int(request.args.get('page', 1)),
        per_page=10,
        error_out=False,
        max_per_page=10
    ).items
    total_pages = users.paginate(
        page=int(request.args.get('page', 1)),
        per_page=10,
        error_out=False,
        max_per_page=10
    ).pages
    users_output = []
    for user in page_obj:
        users_output.append(user.to_json())
    return jsonify({
        'total_pages': total_pages,
        'users': users_output
    })


@app.route('/user/<id>', methods=['GET'])
def get_user_by_id(id):
    user = User.query.get(id)
    return jsonify(user.to_json())


@app.post('/user')
def add_user():
    username = request.form['username']
    gender = request.form['gender']
    db.session.add(User(username=username, gender=gender))
    db.session.commit()
    return 'User Created!'


@app.route('/user/<id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    username = request.form['username']
    gender = request.form['gender']
    user.username = username
    user.gender = gender
    db.session.commit()
    return 'User Updated!'


if __name__ == '__main__':
    app.run()
