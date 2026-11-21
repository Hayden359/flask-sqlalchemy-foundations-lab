# server/app.py
#!/usr/bin/env python3

from flask import Flask, make_response
from flask_migrate import Migrate

try:
    from server.models import db, Earthquake
except ModuleNotFoundError:
    from models import db, Earthquake

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)


def seed_database():
    db.create_all()
    if Earthquake.query.count() == 0:
        db.session.add_all([
            Earthquake(magnitude=9.5, location="Chile", year=1960),
            Earthquake(magnitude=9.2, location="Alaska", year=1964),
            Earthquake(magnitude=8.6, location="Alaska", year=1946),
            Earthquake(magnitude=8.5, location="Banda Sea", year=1934),
            Earthquake(magnitude=8.4, location="Chile", year=1922),
        ])
        db.session.commit()


with app.app_context():
    seed_database()


@app.route('/')
def index():
    body = {'message': 'Flask SQLAlchemy Lab 1'}
    return make_response(body, 200)

# Add views here
@app.route('/earthquakes', methods=['GET'])
def get_earthquakes():
    earthquakes = Earthquake.query.all()
    earthquakes_list = [eq.to_dict() for eq in earthquakes]
    return make_response({'earthquakes': earthquakes_list}, 200)

@app.route('/earthquakes/<int:id>', methods=['GET'])
def get_earthquake(id):
    earthquake = db.session.get(Earthquake, id)
    if not earthquake:
        return make_response({'message': f'Earthquake {id} not found.'}, 404)
    return make_response(earthquake.to_dict(), 200)

@app.route('/earthquakes/magnitude/<float:magnitude>', methods=['GET'])
def get_earthquakes_by_magnitude(magnitude):
    earthquakes = (
        Earthquake.query
        .filter(Earthquake.magnitude >= magnitude)
        .order_by(Earthquake.id.asc())
        .all()
    )
    earthquakes_list = [earthquake.to_dict() for earthquake in earthquakes]
    return make_response({
        'count': len(earthquakes_list),
        'quakes': earthquakes_list,
    }, 200)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
