import os
import json

import helper

reminders_dict = {}


class Reminder:
    def __init__(self, timestamp, state):
        self.header = None
        self.desc = None
        self.body = None
        self.state = state
        self.timestamp = timestamp

    # Creates a formatted record from a rec class instance which is ready for writing to a json file
    def create_reminder_json(self, reminder_instance):
        rem = {
            'timestamp': str(reminder_instance.timestamp),
            'header': reminder_instance.header,
            'body': reminder_instance.body,
            'state': reminder_instance.state
        }
        return rem

    # Appends a reminder instance to the reminder-uid.json file
    def add_reminder(self, user_id, reminder_instance):
        reminders = {}
        reminders['reminders'] = []
        file_path = 'reminders/' + 'reminder-' + str(user_id) + '.json'
        try:
            while not os.path.exists(file_path):
                helper.write_json(reminders, file_path)
            rem = self.create_reminder_json(reminder_instance)
            with open(file_path) as file:
                data = json.load(file)
            tmp = data['reminders']
            tmp.append(rem)
            helper.write_json(data, file_path)
            return True
        except Exception as e:
            return False

    def get_reminders(self, user_id):
        file_path = 'reminders/' + 'reminder-' + str(user_id) + '.json'
        if os.path.exists(file_path):
            with open(file_path) as file:
                data = json.load(file)
            return data
        else:
            return None

    def delete_reminder(self, user_id, reminder_id):
        try:
            file_path = 'reminders/' + 'reminder-' + str(user_id) + '.json'
            data = self.get_reminders(user_id)
            for element in data['reminders']:
                if element['timestamp'] == reminder_id:
                    data['reminders'].remove(element)
            helper.write_json(data, file_path)
            return True
        except Exception as e:
            return False

    def change_state(self, user_id, reminder_id,  new_state):
        try:
            file_path = 'reminders/' + 'reminder-' + str(user_id) + '.json'
            data = self.get_reminders(user_id)
            for element in data['reminders']:
                if element['timestamp'] == reminder_id:
                    element['state'] = new_state
            helper.write_json(data, file_path)
        except Exception as e:
            return False
