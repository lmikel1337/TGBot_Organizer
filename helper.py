import json
import os

import languages


# Writes specified data to the specified file
def write_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)


def change_language(language='En'):
    language = language.lower()
    language_dict = {}
    if language == 'en':
        language_dict = languages.language_english
    elif language == "au":
        language_dict = languages.language_australian
    edit_config('language', language)
    return language_dict


def init_bot():
    file_path = 'config.json'
    if not os.path.exists(file_path):
        print('Error initializing the bot, missing config file')
    else:
        with open(file_path) as file:
            data = json.load(file)
        token = data['token']
        language = data['language']
        return token, language


def edit_config(key, new_value):
    file_path = 'config.json'
    if not os.path.exists(file_path):
        print('Error initializing the bot, missing config file')
    else:
        with open(file_path) as file:
            data = json.load(file)
        data[key] = new_value
        write_json(data, file_path)
