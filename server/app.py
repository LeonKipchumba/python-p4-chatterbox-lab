from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

@app.route('/messages', methods=['GET', 'POST'])
def messages():
    if request.method == 'GET':
        messages = Message.query.order_by(Message.created_at.asc()).all()
        return jsonify([{
            'id': m.id,
            'body': m.body,
            'username': m.username,
            'created_at': m.created_at.isoformat() if m.created_at else None,
            'updated_at': m.updated_at.isoformat() if m.updated_at else None
        } for m in messages]), 200

    elif request.method == 'POST':
        data = request.get_json()
        if not data or 'body' not in data or 'username' not in data:
            return jsonify({'error': 'Missing body or username'}), 400
        message = Message(body=data['body'], username=data['username'])
        db.session.add(message)
        db.session.commit()
        return jsonify({
            'id': message.id,
            'body': message.body,
            'username': message.username,
            'created_at': message.created_at.isoformat() if message.created_at else None,
            'updated_at': message.updated_at.isoformat() if message.updated_at else None
        }), 201

@app.route('/messages/<int:id>', methods=['PATCH', 'DELETE'])
def messages_by_id(id):
    message = db.session.get(Message, id)
    if not message:
        return jsonify({'error': 'Message not found'}), 404
    if request.method == 'PATCH':
        data = request.get_json()
        if not data or 'body' not in data:
            return jsonify({'error': 'Missing body'}), 400
        message.body = data['body']
        db.session.commit()
        return jsonify({
            'id': message.id,
            'body': message.body,
            'username': message.username,
            'created_at': message.created_at.isoformat() if message.created_at else None,
            'updated_at': message.updated_at.isoformat() if message.updated_at else None
        }), 200
    elif request.method == 'DELETE':
        db.session.delete(message)
        db.session.commit()
        return '', 204

if __name__ == '__main__':
    app.run(port=5555)
