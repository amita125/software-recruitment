import os
import re

import pandas as pd

from models import User

from datetime import datetime

# function to retrieve a list of dicts from an excel file
def get_data():
    df = pd.read_excel(os.path.expanduser("exercise_1.xlsx"),
                       engine='openpyxl')
    return df.to_dict('records')


# function to save simulate storing data. Accepts a list of users
def save_data(users):
    validated_users = []
    for user in users:
        user_to_store = User.parse_obj(user)
        validated_users.append(user_to_store)
    print(f"Successfully stored the following users:\n ")
    print(validated_users)


# Helper function to check whether the user is active or not 
def is_active(user):
    today_date = pd.Timestamp.now().date()
    start_date = pd.Timestamp(user['start_date']).date()
    end_date = pd.Timestamp(user['end_date']).date()
    return start_date <= today_date <= end_date



# Helper function to check the start and end date for use in POST and PUT requests
def convert_date_fields(data, date_format):
    try:
        if 'start_date' in data:
            data['start_date'] = datetime.strptime(data['start_date'], date_format).date()
        if 'end_date' in data:
            data['end_date'] = datetime.strptime(data['end_date'], date_format).date()
    except ValueError:
        return False
    return True

