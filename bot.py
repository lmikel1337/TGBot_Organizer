from datetime import datetime
import telebot
from telebot import types

import config
import reminder

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(message.chat.id, 'help')


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id, 'start')


@bot.message_handler(commands=['reminder'])
def reminder_command(message):
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton('Add Reminder', callback_data='reminder-add'),
               types.InlineKeyboardButton('View Reminders', callback_data='reminder-viewActive'))
    bot.send_message(message.chat.id, 'showing reminders menu', reply_markup=markup)


@bot.message_handler(commands=['reminder_show'])
def view_active_reminders(message):
    state = 'active'
    view_reminders(message, state)


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
    msg = bot.send_message(chat_id, 'Please enter the reminder\'s name')
    bot.register_next_step_handler(msg, add_reminder_header_step)


def add_reminder_header_step(message):
    chat_id = message.chat.id
    if message.text is not None:
        header = message.text
        reminder_instance = reminder.reminders_dict[chat_id]
        reminder_instance.header = header
        reminder_instance.state = 'active'
        msg = bot.send_message(chat_id, 'Please enter the description of the reminder, '
                                        'type skip to skip adding this parameter')
        bot.register_next_step_handler(msg, add_reminder_body_step)
    else:
        msg = bot.send_message(chat_id, 'Please enter the name of the reminder')
        bot.register_next_step_handler(msg, add_reminder_header_step)


def add_reminder_body_step(message):
    chat_id = message.chat.id
    body = message.text
    reminder_instance = reminder.reminders_dict[chat_id]
    if body != 'skip':
        reminder_instance.body = body
    rem = reminder_instance.add_reminder(chat_id, reminder_instance)
    if rem:
        bot.send_message(chat_id, 'Reminder saved')
    else:
        bot.send_message(chat_id, 'Error saving the reminder')


def view_reminders(query, reminder_state):
    try:
        chat_id = query.message.chat.id
    except Exception as e:
        chat_id = query.chat.id

    create_reminder_instance(chat_id)
    reminder_instance = reminder.reminders_dict[chat_id]
    reminders = reminder_instance.get_reminders(chat_id)
    if reminders['reminders'] is not None:
        bot.send_message(chat_id, 'Displaying active reminders')
        for element in reminders['reminders']:
            if element['state'] == reminder_state:
                markup = types.InlineKeyboardMarkup()
                markup.row(
                    types.InlineKeyboardButton('Done', callback_data='reminder-done-' + str(element['timestamp'])),
                    types.InlineKeyboardButton('Delete', callback_data='reminder-delete-' + str(element['timestamp']))
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
