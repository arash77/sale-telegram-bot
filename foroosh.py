#!/usr/local/bin/python
#-*- coding:utf-8 -*-
import sys
import time
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
import MySQLdb as db

reload(sys)
sys.setdefaultencoding('utf8')

HOST = "localhost"
USER = "root"
PASSWORD = "1377458"
DB = "foroosh"

def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id, msg['text'], msg['chat']['first_name'])

    if content_type != 'text':
        return
    command = msg['text']

    first_name = msg['chat']['first_name']

    if msg['chat']['username'] is not None:
        chat_username = msg['chat']['username']
    else:
        chat_username = "no username!"

    if msg['chat']['last_name'] is not None:
        last_name = msg['chat']['last_name']
    else:
        last_name = "no last name!"

    connection.commit()
    if (cursor.execute("SELECT * FROM user WHERE chat_id=%s" % (chat_id))):
        result = cursor.fetchall()
        for row in result:
            a = row[2]
            kala = row[6]
            shahr = row[7]
            phonenum = row[8]
    else:
        cursor.execute("INSERT INTO user (chat_id,username,name,fname,stage) VALUES (%s,'%s','%s','%s',%s);" % (chat_id,chat_username,first_name,last_name,0))
        a = 0

    if command == '/start' and a==0:
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='ثبت سفارش',  callback_data='foroosh')]])
        bot.sendMessage(chat_id, '%s,\nلطفا یکی از گزینه های زیر را انتخاب کنید:' % (first_name), reply_markup=markup)
        cursor.execute("UPDATE user SET stage=%s WHERE chat_id=%s" % (0,chat_id))
        connection.commit()
        return

    if command == '/start' and a!=0:
        bot.sendMessage(chat_id, 'لطفا ثبت سفارش را تکمیل کنید و یا از دکمه انصراف استفاده کنید!')
        return

    elif command == 'انصراف':
        markup = ReplyKeyboardRemove()
        bot.sendMessage(chat_id, 'شما از ثبت سفارش انصراف دادید!', reply_markup=markup)
        cursor.execute("UPDATE user SET stage=%s WHERE chat_id=%s" % (0,chat_id))
        connection.commit()
        a = 0
        return

    elif a == 1:
        kala = msg['text']
        cursor.execute("UPDATE user SET stage=%s , kala='%s' WHERE chat_id=%s" % (2,kala,chat_id))
        connection.commit()
        bot.sendMessage(chat_id, 'لطفا شماره تماس خود را وارد کنید:')
        return
    elif a == 2:
        try:
            int(msg['text'])
            phonenum = msg['text']
            cursor.execute("UPDATE user SET stage=%s , phonenum='%s' WHERE chat_id=%s" % (3,phonenum,chat_id))
            connection.commit()
            bot.sendMessage(chat_id, 'لطفا نام شهر خود را وارد کنید:')
        except ValueError:
            bot.sendMessage(chat_id, 'لطفا فقط از عدد استفاده کنید!')
        return
    elif a == 3:
        shahr = msg['text']
        cursor.execute("UPDATE user SET stage=%s , shahr='%s' WHERE chat_id=%s" % (4,shahr,chat_id))
        connection.commit()
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='بله',  callback_data='yes'),InlineKeyboardButton(text='خیر',  callback_data='no')]])
        bot.sendMessage(chat_id, 'آیا اطلاعات زیر را تایید میکنید:\n\nنام کالا: %s\nنام شهر: %s\nشماره تلفن تماس: %s' % (kala,shahr,phonenum), reply_markup=markup)
        return
    elif command == '/about':
        markup = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='ارتباط با من', url='https://t.me/KadArash'),InlineKeyboardButton(text='وبسایت شخصی', url='http://arash77.ir')]])
        bot.sendMessage(chat_id, 'این ربات توسط آرش کدخدایی طراحی و ساخته شده است!', reply_markup=markup)
        return
    elif a == 0:
        bot.sendMessage(chat_id, 'متوجه منظورتان نمیشوم!')
        return

def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    message = msg['message']
    print('Callback query:', query_id, from_id, data, message)

    connection.commit()
    cursor.execute("SELECT * FROM user WHERE chat_id=%s" % (from_id))
    result = cursor.fetchall()
    for row in result:
        a = row[2]
        name = row[4]
        fname = row[5]
        chat_username = row[3]
        kala = row[6]
        shahr = row[7]
        phonenum = row[8]

    if data == 'foroosh' and a == 0:
        bot.editMessageText((message['chat']['id'],message['message_id']) , 'در حال ثبت سفارش...')
        bot.answerCallbackQuery(query_id, text='در حال ثبت سفارش...')
        markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='انصراف')]],resize_keyboard=True)
        bot.sendMessage(from_id, 'نام کالا را وارد کنید:', reply_markup=markup)
        cursor.execute("UPDATE user SET stage=%s WHERE chat_id=%s" % (1,from_id))
        connection.commit()
        return
    if data == 'yes' and a == 4:
        bot.editMessageText((message['chat']['id'],message['message_id']) , 'اطلاعات زیر توسط شما تایید شد:\nنام کالا: %s\n\nنام شهر: %s\nشماره تلفن تماس: %s' % (kala,shahr,phonenum))
        bot.answerCallbackQuery(query_id, text='اطلاعات تایید شد!')
        markup = ReplyKeyboardRemove()
        bot.sendMessage(from_id, 'ثبت سفارش شما با موفقیت انجام شد!\nدر اسرع وقت با شما تماس میگیریم...', reply_markup=markup)
        cursor.execute("UPDATE user SET stage=%s WHERE chat_id=%s" % (0,from_id))
        connection.commit()
        try:
            cursor.execute("INSERT INTO foroosh (name, fname, username, kala, shahr, phonenum) VALUES ('%s','%s','%s','%s','%s','%s');" % (name, fname, chat_username, kala, shahr, phonenum))
            connection.commit()
            bot.sendMessage(106103222, '%s , %s\n@%s\n%s\n%s\n%s' % (name, fname,chat_username,kala,shahr,phonenum))
        except:
            print ('error')
            connection.rollback()
        return
    if data == 'no' and a == 4:
        bot.editMessageText((message['chat']['id'],message['message_id']), 'اطلاعات زیر توسط شما تایید نشد:\nنام کالا: %s\n\nنام شهر: %s\nشماره تلفن تماس: %s' % (kala,shahr,phonenum))
        bot.answerCallbackQuery(query_id, text='اطلاعات تایید نشد!')
        markup = ReplyKeyboardRemove()
        bot.sendMessage(from_id, 'ثبت سفارش شما لغو شد.\nبرای ثبت نام /start را بفشارید!', reply_markup=markup)
        cursor.execute("UPDATE user SET stage=%s WHERE chat_id=%s" % (0,from_id))
        connection.commit()
        return
    else:
        bot.answerCallbackQuery(query_id, text='لطفا دوباره دستور /start را ارسال کنید!')
        return

bot = telepot.Bot('...')

MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()
print('Listening ...')

while 1:
    connection = db.Connection(host=HOST, user=USER, passwd=PASSWORD, db=DB, use_unicode=True, charset='utf8')
    cursor = connection.cursor()
    cursor.execute("SET NAMES utf8mb4;")
    cursor.execute("SET CHARACTER SET utf8mb4;")
    cursor.execute("SET character_set_connection=utf8mb4;")
    time.sleep(3600)