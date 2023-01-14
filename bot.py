import sqlite3
import telebot
from threading import Thread
import schedule
import os
import random
import datetime

bot = telebot.TeleBot("5883001802:AAFznn0RawJ5JaXGjTnIXyx3FCMGg-wii1E")

markup = telebot.types.ReplyKeyboardMarkup(True,None,None)
item1 = telebot.types.KeyboardButton('Подписаться')
item2 = telebot.types.KeyboardButton('Отписаться')

markup.row(item1,item2)

def sub(time):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    id_list = cursor.execute("SELECT user FROM users").fetchall()
    for id in id_list:
        conn1 = sqlite3.connect('users.db')
        cursor1 = conn1.cursor()
        a = cursor1.execute(f"SELECT * FROM call WHERE les_time = '{time}'").fetchall()
        num_class = cursor.execute(f"SELECT num_class FROM users WHERE user = {id[0]}").fetchall()
        try:
            meme = (random.choice(conn1.execute("SELECT meme FROM memes").fetchall()))[0]
            if a[0][2] != '0':
                if a[0][-1] != 'NO':
                    s = a[0][-1].split('-')
                    if int(s[0]) <= int(num_class[0][0][:-1]) <= int(s[1]):
                        bot.send_message(id[0],f'Закончился {a[0][0]} урок. Перемена будет длиться до {a[0][2]}. Можешь пойти перекусить!')
                        photo = open(f"{meme}.jpg", 'rb')
                        bot.send_photo(id[0],photo)
                        bot.send_message(id[0], f'Автор мема: @{meme.split("_")[0]}')
                    else:
                        bot.send_message(id[0],f'Закончился {a[0][0]} урок. Перемена будет длиться до {a[0][2]}. Поесть сейчас не получится, перемена для {a[0][-1]} классов.')
                        photo = open(f"{meme}.jpg", 'rb')
                        bot.send_photo(id[0], photo)
                        bot.send_message(id[0], f'Автор мема: @{meme.split("_")[0]}')
            else:
                bot.send_message(f'Учебный день закончился, беги отдыхать!')
        except:
            if a[0][2] != '0':
                if a[0][-1] != 'NO':
                    s = a[0][-1].split('-')
                    if int(s[0]) <= int(num_class[0][0][:-1]) <= int(s[1]):
                        bot.send_message(id[0],f'Закончился {a[0][0]} урок. Перемена будет длиться до {a[0][2]}. Можешь пойти перекусить!')
                    else:
                        bot.send_message(id[0],f'Закончился {a[0][0]} урок. Перемена будет длиться до {a[0][2]}. Поесть сейчас не получится, перемена для {a[0][-1]} классов.')
            else:
                bot.send_message(id[0],f'Учебный день закончился, беги отдыхать!')


class Calls(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):#Отправка в точное время
        if datetime.date.today().weekday() < 5:
            schedule.every().day.at("09:15").do(lambda: sub('09:15'))
            schedule.every().day.at("10:15").do(lambda: sub('10:15'))
            schedule.every().day.at("11:20").do(lambda: sub('11:20'))
            schedule.every().day.at("12:20").do(lambda: sub('12:20'))
            schedule.every().day.at("13:15").do(lambda: sub('13:15'))
            schedule.every().day.at("14:20").do(lambda: sub('14:20'))
            schedule.every().day.at("15:20").do(lambda: sub('15:20'))
            schedule.every().day.at("16:20").do(lambda: sub('16:20'))
            while True:
                schedule.run_pending()


@bot.message_handler(commands=['start'])
def start(message):#Обработка /start
    bot.send_message(message.chat.id,'Привет\nХочешь подписаться на рассылку звонков по расписанию?',reply_markup=markup)

'''''''''
Это планы на будущее
@bot.message_handler(commands=['like'])
def like(message):
    text = message.reply_to_message.text
    bot.send_message(message.chat.id,'Вау! Круто!')
    conn_like = sqlite3.connect('users.db')
    cursor_like = conn_like.cursor()
    cursor_like.execute(f"UPDATE memes SET like=like+1 WHERE meme = '{text}'")
    conn_like.commit()


@bot.message_handler(commands=['dislike'])
def dislike(message):
    text = message.reply_to_message.text
    bot.send_message(message.chat.id,'Поменьше бы таких мемов...')
'''

def registration(message):#Регистрация
    if 2 <= len(message.text) <= 3 and 1 <= int(message.text[:-1]) <= 11:
        try:
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO users (user, num_class) VALUES ('{message.chat.id}', '{message.text}')").fetchall()
            conn.commit()
            bot.send_message(message.chat.id, "Регистрация пройдена, молодец!")
        except:
            bot.send_message(message.chat.id,'Вы уже добавились...')
    else:
        bot.reply_to(message, "Где-то ты, кажется, ошибся...")
        msg = bot.send_message(message.chat.id, "Тебе необходимо написать класс, в котором ты учишься (пример: 9Г).")
        bot.register_next_step_handler(msg, registration)



@bot.message_handler(content_types=["text"])
def start(message):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    id_list = [int(x[0]) for x in cursor.execute("SELECT admin FROM admins").fetchall()]
    conn.close()
    if message.text == 'Подписаться':#Подписаться на рассылку звонков и мемов
        msg = bot.send_message(message.chat.id, "Тебе необходимо написать класс, в котором ты учишься (пример: 9Г).")
        bot.register_next_step_handler(msg,registration)
    elif message.text == 'Отписаться':#Отписаться от рассылки звонков и мемов
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM users WHERE user = '{message.chat.id}'")
        conn.commit()
        bot.send_message(message.chat.id, 'Вы отказались от подписки...')
    elif message.text == '-' and message.chat.id in id_list:#Отклонение мема
        try:
            os.remove(f"{message.reply_to_message.text}.jpg")
            bot.send_message(message.chat.id, 'Мем отклонен')
            bot.send_message(int(text.split('_')[1]),'Ваша мем отклонен')
        except:
            bot.send_message(message.chat.id,'Пожалуйста, ответьте на сообщение!')
    elif message.text == '+' and message.chat.id in id_list:#Принятие заявки на мем
        try:
            text = message.reply_to_message.text
            conn = sqlite3.connect('users.db')
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO memes (meme,like,dislike) VALUES ('{text}',0,0)")
            conn.commit()
            bot.send_message(message.chat.id, 'Фото добавлено в мемы!')
            bot.send_message(int(text.split('_')[1]),'Ваша мем одобрен')
        except:
            bot.send_message(message.chat.id,'Пожалуйста, ответьте на сообщение!')
    else:
        bot.send_message(message.chat.id,'Я Вас не понял...')





@bot.message_handler(content_types=["photo"])#Обработчик фото
def photo(message):
    try:
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path = os.path.abspath('bot.py')
        new_path = '/'.join(path.replace('\\','/').split('/')[:-1])
        src =  new_path + f"/{str(message.chat.username)}_{str(message.chat.id)}_{file_info.file_unique_id}.jpg"
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Фото отправлено на модерацию!")
        photo = open(f"{str(message.chat.username)}_{str(message.chat.id)}_{file_info.file_unique_id}.jpg", 'rb')
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        id_list = cursor.execute("SELECT admin FROM admins").fetchall()
        random_id = int(random.choice(id_list)[0])
        bot.send_photo(random_id, photo)
        bot.send_message(random_id, f"{str(message.chat.username)}_{str(message.chat.id)}_{file_info.file_unique_id}")
    except:
        bot.send_message(message.chat.id,'Произошла ошибка, попробуйте заново.')

while True:
    Calls().start()
    bot.polling(none_stop=True)



