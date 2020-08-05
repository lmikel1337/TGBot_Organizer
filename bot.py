from datetime import datetime
import telebot
from telebot import types

import reminder
import helper
import language_keyboard_convertions

token, language = helper.init_bot()

bot = telebot.TeleBot(token)

language_dict = helper.change_language(language)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, 'help')


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'start')


@bot.message_handler(commands=['translate_scuffed_text'])
def translate_scuffed_text_first_step(message):
    msg = bot.send_message(message.chat.id, language_dict['translate_scuffed_text-message'])
    bot.register_next_step_handler(msg, translate_scuffed_text)


def translate_scuffed_text(message):
    text = message.text
    new_text = []
    if text is not None:
        for letter in text:
                if 65 <= ord(letter) <= 90:
                    letter = chr(ord(letter) + 32)
                    new_text.append(chr(ord(language_keyboard_convertions.en_to_ua[letter]) - 32))
                elif letter in language_keyboard_convertions.en_to_ua:
                    new_text.append(language_keyboard_convertions.en_to_ua[letter])
                else:
                    new_text.append(letter)
        bot.send_message(message.chat.id, "".join(new_text))
    else:
        msg = bot.send_message(message.chat.id, language_dict['translate_scuffed_text-message'])
        bot.register_next_step_handler(msg, translate_scuffed_text)


@bot.message_handler(commands=['reminder'])
def reminder_command(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(language_dict['reminder_command-button-add_reminder'],
                                          callback_data='reminder-add'),
               types.InlineKeyboardButton(language_dict['reminder_command-button-view_reminders'],
                                          callback_data='reminder-viewActive'))
    bot.send_message(message.chat.id, language_dict['reminder_command-message-showing_reminders_menu'],
                     reply_markup=markup)


@bot.message_handler(commands=['reminder_show'])
def view_active_reminders(message):
    state = 'active'
    view_reminders(message, state)


@bot.message_handler(commands=['set_language'])
def change_language(message):
    global language_dict
    input = message.text.split()
    if len(input) == 2:
        language_dict = helper.change_language(input[1])
    bot.send_message(message.chat.id, language_dict['change_language-language_changed'])


@bot.callback_query_handler(func=lambda f: True)
def callback_handler(query):
    data = query.data
    if data.startswith('reminder'):
        reminder_handler(query)


def create_reminder_instance(chat_id):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state = 'active'
    reminder_instance = reminder.Reminder(timestamp, state)
    reminder.reminders_dict[chat_id] = reminder_instance


def reminder_handler(query):
    data = query.data
    if data[9:] == 'add':
        add_reminder_first_step(query)
        bot.answer_callback_query(query.id)
    elif data[9:] == 'viewActive':
        state = 'active'
        view_reminders(query, state)
        bot.answer_callback_query(query.id)
    elif 'done-' in data:
        chat_id = query.message.chat.id
        create_reminder_instance(chat_id)
        reminder_instance = reminder.reminders_dict[chat_id]
        state = 'inactive'
        reminder_instance.change_state(chat_id, data[14:], state)
        bot.send_message(chat_id, 'Reminder marked as completed')
    elif 'delete-' in data:
        chat_id = query.message.chat.id
        create_reminder_instance(chat_id)
        reminder_instance = reminder.reminders_dict[chat_id]
        res = reminder_instance.delete_reminder(chat_id, data[16:])
        if res:
            bot.send_message(chat_id, 'Reminder deleted')


@bot.message_handler(commands=['reminder_add'])
def add_reminder_first_step(query):
    try:
        chat_id = query.message.chat.id
    except Exception as e:
        chat_id = query.chat.id
    create_reminder_instance(chat_id)
    msg = bot.send_message(chat_id, language_dict['reminder_add-message-please_enter_the_reminders_name'])
    bot.register_next_step_handler(msg, add_reminder_header_step)


def add_reminder_header_step(message):
    chat_id = message.chat.id
    if message.text is not None:
        header = message.text
        reminder_instance = reminder.reminders_dict[chat_id]
        reminder_instance.header = header
        reminder_instance.state = 'active'
        msg = bot.send_message(chat_id, language_dict['add_reminder_header_step-message-please_enter_description'])
        bot.register_next_step_handler(msg, add_reminder_body_step)
    else:
        msg = bot.send_message(chat_id, language_dict['add_reminder_header_step-message-enter_the_name_of_reminder:'])
        bot.register_next_step_handler(msg, add_reminder_header_step)


def add_reminder_body_step(message):
    chat_id = message.chat.id
    body = message.text.lower()
    reminder_instance = reminder.reminders_dict[chat_id]
    if body != 'skip':
        reminder_instance.body = body
    rem = reminder_instance.add_reminder(chat_id, reminder_instance)
    if rem:
        bot.send_message(chat_id, language_dict['add_reminder_body_step-message-reminder_saved'])
    else:
        bot.send_message(chat_id, language_dict['add_reminder_body_step-message-error_saving_reminder'])


def view_reminders(query, reminder_state):
    try:
        chat_id = query.message.chat.id
    except Exception as e:
        chat_id = query.chat.id

    create_reminder_instance(chat_id)
    reminder_instance = reminder.reminders_dict[chat_id]
    reminders = reminder_instance.get_reminders(chat_id)
    if reminders['reminders'] is not None:
        bot.send_message(chat_id, language_dict['view_reminders-message-displaying_active_reminders'])
        for element in reminders['reminders']:
            if element['state'] == reminder_state:
                markup = types.InlineKeyboardMarkup()
                markup.row(
                    types.InlineKeyboardButton(language_dict['view_reminders-button-done'],
                                               callback_data='reminder-done-' + str(element['timestamp'])),
                    types.InlineKeyboardButton(language_dict['view_reminders-button-delete'],
                                               callback_data='reminder-delete-' + str(element['timestamp']))
                )
                if element['body'] is not None:
                    bot.send_message(chat_id, element['header'] + '\n' + element['body'], reply_markup=markup)
                else:
                    bot.send_message(chat_id, element['header'], reply_markup=markup)
    else:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('Add category', callback_data='reminder-add'))
        bot.send_message(chat_id, 'No active reminders')


bot.polling()
