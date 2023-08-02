from utilities import get_data
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_all_users():
    return jsonify(get_data()),200

@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    data = get_data()
    user = next((user for user in data if user['id'] == user_id), None)
    if not user:
        return jsonify({'message':'User not found'}),404
    return jsonify(user),200

@app.route('/trust/<string:trust>', methods=['GET'])
def get_users_by_trust(trust):
    data = get_data()
    users = [user for user in data if user['primary_trust'] == trust]
    if not users:
        return jsonify({'message':'Users not found for the trust'}),404
    return jsonify(users),200

if __name__ == '__main__':
    app.run()
