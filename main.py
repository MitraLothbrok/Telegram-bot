import telebot
from telebot import types
import gspread
import datetime
import json


# Method to search for text in the spreadsheet
def search_spreadsheet(query, column1, column2, column3):
    try:
        # Getting all values in the specified columns
        column1_values = wks.col_values(column1)
        column2_values = wks.col_values(column2)
        column3_values = wks.col_values(column3)
        result_list = []  # Create an empty list to store results

        # Searching for the value in the columns
        for i, value in enumerate(column1_values):
            if query.lower() in value.lower():
                row_values = [column1_values[i], column2_values[i], column3_values[i]]
                result_list.append(row_values)

        return result_list  # Returning the list of matching rows
    except:
        # Value not found
        return "Значение не найдено."


empty_cell_index = None
is_number_recovered = False

# Opening the Google spreadsheet
gc = gspread.service_account(filename='telegram-bot-396912-5a5453aab539.json')
sh = gc.open_by_url('https://docs.google.com/spreadsheets/d/1WWXCy7dq2teamSL7rZDDvBYaR9ax_11cc_jqOudp8Oc/edit#gid=0')
wks = sh.get_worksheet(0)

# Connecting to the bot
token = '6379066369:AAHF1zeQ1o2bwmPFWWGwgu-0-R1eZDHAaNs'
bot = telebot.TeleBot(token)

# Bot response to the /start command
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Здравствуйте')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton("Ввести текст")
    item2 = types.KeyboardButton("Поиск по тексту")
    markup.add(item1)
    markup.add(item2)
    bot.send_message(message.chat.id, 'Выберите что вам нужно', reply_markup=markup)

# Bot response to text
@bot.message_handler(content_types = ['text'])
def answer(message):
    if message.text == "Ввести текст":
        bot.send_message(message.chat.id, 'Текст который вы введите будет сохранен в Google таблице по такому адресу - https://docs.google.com/spreadsheets/d/1WWXCy7dq2teamSL7rZDDvBYaR9ax_11cc_jqOudp8Oc/edit#gid=975183363')
        bot.register_next_step_handler(message, write_wks)


    elif message.text == "Поиск по тексту":
        bot.send_message(message.chat.id, 'Введите текст который нужно найти')
        bot.register_next_step_handler(message, search_text)

def write_wks(message):
    global empty_cell_index, is_number_recovered
    if message.text == "Поиск по тексту":
        bot.send_message(message.chat.id, 'Введите текст который нужно найти')
        bot.register_next_step_handler(message, search_text)
    else:
        now = datetime.datetime.now()
        a_str = now.strftime('%Y-%m-%d %H:%M:%S')
        json_str = json.dumps(a_str)

        if not is_number_recovered:
            # Check if there's already a record in this row
            cell_list = wks.col_values(1)
            empty_cell_index = cell_list.index('') if '' in cell_list else len(cell_list) + 1

            # Save text and time in the first two columns
            wks.update_cell(empty_cell_index, 1, message.text)
            wks.update_cell(empty_cell_index, 2, json_str)

            is_number_recovered = True

        if is_number_recovered:
            # Requesting a number
            bot.send_message(message.chat.id, "Пожалуйста, отправьте номер")
            bot.register_next_step_handler(message, get_number)


def get_number(message):
    global empty_cell_index, is_number_recovered
    if message.text:
        # Write the number to the third column
        wks.update_cell(empty_cell_index, 3, message.text)
        is_number_recovered = False
        bot.send_message(message.chat.id, "Номер записан")

        bot.send_message(message.chat.id, 'Ввидите текст')
        bot.register_next_step_handler(message, write_wks)

def search_text(message):
    if message.text == "Ввести текст":
        bot.send_message(message.chat.id, 'Текст который вы введите будет сохранен в Google таблице по такому адресу - https://docs.google.com/spreadsheets/d/1WWXCy7dq2teamSL7rZDDvBYaR9ax_11cc_jqOudp8Oc/edit#gid=975183363')
        bot.register_next_step_handler(message, write_wks)

    else:
        bot.register_next_step_handler(message, search_text)

        f = search_spreadsheet(message.text, 1, 2, 3)
        for i in f:
            string = ''
            for j in i:
                string += j
                string += "   "
            bot.send_message(message.chat.id, string)

bot.infinity_polling()



