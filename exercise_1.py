from models import User
from utilities import check_email, convert_date_fields, get_data, is_active, save_data, update_data
from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the date format
date_format = "%d/%m/%Y"

# Route to get all the users from the excel file
@app.route('/users', methods=['GET'])
def get_all_users():
    data = get_data()
    return jsonify(data),200


# Route to get the user by passing user id
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    data = get_data()
    user = next((user for user in data if user['id'] == user_id and is_active(user)), None)
    if not user:
        return jsonify({'message':'User not found'}),404
    return jsonify(user),200

# Route to get the users by passing the primary trust
@app.route('/trust/<string:trust>', methods=['GET'])
def get_users_by_trust(trust):
    data = get_data()
    users = [user for user in data if user['primary_trust'] == trust and is_active(user)]
    if not users:
        return jsonify({'message':'Users not found for the trust'}),404
    return jsonify(users),200


# creating a user 
# 1. new user should have the required field from the model 
# 2. new user email should include the @nhs.
# 3. new user email should be unique 
# 4. new user should have the date formatted in '12/12/2023'
# 5. new user should follow the user model data types

@app.route('/user', methods=['POST'])
def create_employee():
    data = get_data()
    new_user = request.json

    # Check if the email is unique or not based on the excel file
    existing_emails = {user['email'] for user in data}
    if new_user['email'] in existing_emails:
        return jsonify({'message': 'Email already exists. Please use a unique email address.'}), 400

    
    # Get the required fields from the User model
    required_fields = [field for field, field_info in User.__fields__.items() if field_info.required]
    extra_fields = [field for field in new_user if field not in required_fields]

    new_id = max(data, key=lambda x: x['id'])['id'] + 1
    new_user['id'] = new_id

    missing_fields = [field for field in required_fields if field not in new_user]

    if missing_fields or extra_fields:
        error_message = ""
        if missing_fields:
            error_message += f'Missing fields: {missing_fields}. '
        if extra_fields:
            error_message += f'Extra fields: {extra_fields}.'
        return jsonify({'message': error_message}), 400
    
    # Check if the date format is valid or not
    if all(key in new_user for key in ['start_date', 'end_date']):
        if not convert_date_fields(new_user, date_format):
            return jsonify({'message': 'Invalid date format. Expected format: dd/mm/yyyy.'}), 400

    # Check the data types of the fields
    for field, value in new_user.items():
        expected_data_type = User.__fields__[field].type_

        if expected_data_type and not isinstance(value, expected_data_type):
            return jsonify({'message': f'Invalid data type for {field}. Expected {expected_data_type.__name__}.'}), 400

    # Validate email format
    if not check_email(new_user['email']):
        return jsonify({'message': 'Invalid email format. Only @nhs. addresses are allowed.'}), 400
    
    #  Validate date comparison for start and end dates
    if new_user['end_date'] < new_user['start_date']:
            return jsonify({'message': 'end_date cannot be before start_date.'}), 400
   
    data.append(new_user)
    save_data(data)
    update_data(data)
    return jsonify(new_user),201


# Updating a user details 
# 1. check the email is unique if provided 
# 2. check the update fields are valid or not 
# 3. check the date format is valid or not 
# 4. check the user is present or not


@app.route('/user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = get_data()
    existing_user = next((user for user in data if user['id'] == user_id), None)
    if not existing_user:
        return jsonify({'message':'User not found'}),404
    
    updated_record = request.json

    # Check if the new email is unique before updating the user's email
    existing_emails = {user['email'] for user in data if user['id'] != user_id}
    if 'email' in updated_record and updated_record['email'] in existing_emails and updated_record['email'] != existing_user['email']:
        return jsonify({'message': 'Email already exists. Please use a unique email address.'}), 400

    # Check the update fields are valid or not
    
    whitelist_fields = [field for field, field_info in User.__fields__.items() if field_info.required]
    unwanted_fields = [field for field in updated_record if field not in whitelist_fields]
    if unwanted_fields:
        return jsonify({'message': f'Unwanted fields in update: {", ".join(unwanted_fields)}'}), 400

    # Check the date format is valid or not
    if 'start_date' in updated_record or 'end_date' in updated_record:
        if not convert_date_fields(updated_record, date_format):
            return jsonify({'message': 'Invalid date format. Expected format: dd/mm/yyyy.'}), 400

    # Check if user wants to update start_date but not end_date
    if 'start_date' in updated_record and 'end_date' not in updated_record:
        # If 'end_date' is not present in the updated_record, retain the existing 'end_date'
        updated_record['end_date'] = existing_user['end_date']

    # Check if user wants to update end_date but not start_date
    elif 'end_date' in updated_record and 'start_date' not in updated_record:
        # If 'start_date' is not present in the updated_record, retain the existing 'start_date'
        updated_record['start_date'] = existing_user['start_date']
    

    #  Validate date comparison for start and end dates
    if updated_record['end_date'] < updated_record['start_date']:
            return jsonify({'message': 'end_date cannot be before start_date.'}), 400

    # Validate data types and date format of updated fields
    for field, value in updated_record.items():
        expected_data_type = User.__fields__[field].type_

        if expected_data_type and not isinstance(value, expected_data_type):
            return jsonify({'message': f'Invalid data type for {field}. Expected {expected_data_type.__name__}.'}), 400
    

    existing_user.update(updated_record)
    save_data(data)
    update_data(data)
    return jsonify(existing_user),200

@app.route('/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    data = get_data()
    existing_user = next((user for user in data if user['id'] == user_id), None)

    if not existing_user:
        return jsonify({'message': f'No user found with the id {user_id}.'}), 404

    data = [item for item in data if item['id'] != user_id]
    save_data(data)
    return jsonify({'message': 'User deleted successfully'}), 200


if __name__ == '__main__':
    app.run()
