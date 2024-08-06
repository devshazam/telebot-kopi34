from django.shortcuts import HttpResponse
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache

import telebot
from telebot.types import LabeledPrice, ShippingOption
from telebot import types # для указание типов

# import redis

from requests.auth import HTTPBasicAuth
import json 
import os
from dotenv import load_dotenv
import re
import logging

from .config.goods import goodsArray, goodsDict
from .models import Users, TeleOrders

# CONFIG
load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
LOG_NAME = os.getenv("LOG_NAME")

bot = telebot.TeleBot(API_TOKEN)
logging.basicConfig(filename=f'{LOG_NAME}.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
def debugToLog(text):
    logging.warning(f"{text}")

user_state_data = {}

hideBoard = types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard







# https://api.telegram.org/bot7397048375:AAFUc0nI6IQpsIgIWWW6ccU-gkgKSrLkMKQ/setWebhook?url=https://03ac-80-90-179-8.ngrok-free.app/
# https://api.telegram.org/bot7397048375:AAFUc0nI6IQpsIgIWWW6ccU-gkgKSrLkMKQ/deleteWebhook?url=https://089e-80-90-179-8.ngrok-free.app/
@csrf_exempt
def index(request):
    # bot.set_webhook('https://bf06-80-90-179-8.ngrok-free.app/')
    if request.method == "POST":
        update = telebot.types.Update.de_json(request.body.decode('utf-8'))
        bot.process_new_updates([update])

    return HttpResponse('<h1>Ты подключился!</h1>')
 

















@bot.message_handler(content_types="web_app_data")
def answer(message):
    try:
        x1 = json.loads(message.web_app_data.data)

        chat_id = message.chat.id

        cache.set(f"{chat_id}_order", { 'name': x1['name'], 'description': x1["description"], 'cost': x1["value"], 'messages': []}, 3600)
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_save = telebot.types.InlineKeyboardButton(text="Оплатить!", callback_data="pay")
        button_save2 = telebot.types.InlineKeyboardButton(text="Добавить описание!", callback_data="add_description")
        keyboard.add(button_save, button_save2)

        bot.send_message(chat_id, "Данные получены!",  reply_markup=hideBoard)
        bot.send_message(chat_id, f'Ваш заказ стоит: {x1["value"]}', reply_markup=keyboard) 
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №1 - {str(e)}')
        bot.send_message(chat_id, str(e))



@bot.callback_query_handler(func=lambda call: call.data == 'add_description')
def save_btn(call):
    try:
        message = call.message
        chat_id = message.chat.id
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text="Выбор сделан!")
        mesg = bot.send_message(message.chat.id, 'Опишите ваш заказ или добавьте файл:', reply_markup=hideBoard)

        debugToLog(f'Error №q1')

        bot.register_next_step_handler(mesg, loop5)
        debugToLog(f'Error №q2')
    except Exception as e:
        debugToLog(f'Error №q3')
        # debugToLog(f'Error №4 - {str(e)}')
        
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, str(e))

def loop5(message):
    try:
        debugToLog(f'Error №q4')
        chat_id = message.chat.id
        cached_data = cache.get(f'{chat_id}_order')
        if cached_data is None:
            raise Exception("Нужно начать по порядку с начала!")
        cached_data['messages'].append(message.message_id)
        debugToLog(f'Error №q5')
        cache.set(f"{chat_id}_order", cached_data, 3600)
        debugToLog(f'Error №q6')
        keyboard = telebot.types.InlineKeyboardMarkup()
        button_save = telebot.types.InlineKeyboardButton(text="Оплатить",
                                                        callback_data='pay')
        button_change = telebot.types.InlineKeyboardButton(text="Добавить описание или файл",
                                                        callback_data='add_description')
        keyboard.add(button_save, button_change)
        debugToLog(f'Error №q7')
        bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=keyboard)
    except Exception as e:
        debugToLog(f'Error №q8')
        # debugToLog(f'Error №5 - {str(e)}')
        bot.send_message(message.chat.id, str(e))       



@bot.callback_query_handler(func=lambda call: call.data == 'pay')
def save_btn(call):
    try:
        message = call.message
        chat_id = message.chat.id
        message_id = message.message_id  
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, 
                             text='⚠️Оплата работает только на смартфоне⚠️!')  
        cached_data = cache.get(f'{chat_id}_order')
        if cached_data is None:
            raise Exception("Оплата не работает на Компьютере, только на смартфоне!")
        
        prices = [LabeledPrice(label=f'{cached_data["name"]}', amount=int(cached_data['cost'])*100)]

        bot.send_invoice(
            message.chat.id,  #chat_id
            f'{cached_data["name"]}', #title
            f'{cached_data["description"]}', #description
            'Kopi34.ru - sales', #invoice_payload
            PROVIDER_TOKEN, #provider_token
            'rub', #currency
            prices, #prices # True If you need to set up Shipping Fee
            start_parameter='kopi34_start_param',)
    except Exception as e:      # works on python 3.x
        
        debugToLog(f'Error №3 - {str(e)}')
        bot.send_message(message.chat.id, str(e))


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    try:
        print(pre_checkout_query)
        bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №6 - {str(e)}')

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    try:
        chat_id = message.chat.id
        cached_data = cache.get(f'{chat_id}_order')
        if cached_data is None:
            raise Exception("Ошибка платежного сервиса, обратитесь к администрации!")
        TeleOrders.objects.create(userChatTelegramId=chat_id, cost=cached_data['cost'], name=cached_data['name'], description=cached_data['description'], messages=json.dumps(cached_data['messages']))

        bot.send_message(message.chat.id,
                        'Оплата прошла успешно!\nПожалуйста поделитесь с нами номером Вашего телефона, нажав на /number\nДля проверки статуса заказа нажмите /user',
                        parse_mode='Markdown')
        
        bot.send_message(ADMIN_CHAT_ID, 'Поступил новый заказ\nДля просмотра последних 10 заказов нажмите /get_orders', parse_mode='Markdown') 
        
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №7 - {str(e)}') 
        bot.send_message(message.chat.id, str(e))  
























@bot.message_handler(commands=['diag'])
def clientId(message):
    try: 
        chat_id = message.chat.id
        cached_data = cache.get(f'{chat_id}_order')
        if cached_data is None:
            raise Exception("Нет данных!")
        bot.send_message(message.chat.id, f'На данный момент объект user_state_data содержит элементов: {json.dumps(cached_data)}')
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №d1 - {str(e)}')
        bot.send_message(message.chat.id, str(e))  





















# USER COMANDS:
@bot.message_handler(commands=['start'])
def clientId(message):
    try: 

        bot.send_message(message.chat.id, 'Здравствуйте, я робот компании kopi34.ru!'
                                            '\nЯ могу отвечаю на вопросы о товарах и ценах и совершенных заказах!'
                                            '\nКоманды:'
                                            '\n/contacts - вывод списка контактов и график работы'
                                            '\n/number - добавить номер телефона'
                                            '\n/help - вывод списка всех команд'
                                            '\n/i_can - списка всех товаров') # Duplicate with a message that the user will now send his phone number to the bot (just in case, but this is not necessary)
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №8 - {str(e)}')
        bot.send_message(message.chat.id, str(e))  


@bot.message_handler(commands=['i_can'])
def clientId(message):
    try: 
        x1 = ''
        for x in goodsArray:
            x1 += f'{x[2]}\n'
        bot.send_message(message.chat.id, x1) # Duplicate with a message that the user will now send his phone number to the bot (just in case, but this is not necessary)
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №9 - {str(e)}')
        bot.send_message(message.chat.id, str(e))  


@bot.message_handler(commands=['help'])
def clientId(message):
    try: 
        # bot.sendMessage(chatId, '<b>TEST</b>', {parse_mode: 'HTML'})
        bot.send_message(message.chat.id, 'Здравствуйте, я @kopi34_bot!'
                                            '\nЯ отвечаю на вопросы о товарах, ценах и заказах!'
                                            '\nKОМАНДЫ (нажмите для исполнения):'
                                            '\n/contacts - вывод списка контактов и график работы'
                                            '\n/user - вывод списка не выполненных заказов'
                                            '\n/number - поделиться номером телефона для связи!5'
                                            '\n/help - вывод списка всех команд'
                                            '\n/i_can - списка всех товаров'
                                            '\nАдминистратор: @kopiprint34')
    except Exception as e:      # works on python 3.x
         debugToLog(f'Error №10 - {str(e)}')
         bot.send_message(message.chat.id, str(e))  
        


@bot.message_handler(commands=['contacts'])
def clientId(message):
    try: 

        bot.send_message(message.chat.id, '<b>Наши контакты:</b>\nСайт: https://kopi34.ru\nТелефон: +7(909) 380-25-19\nТелеграм: @kopiprint34\nОфис №1: Петропавловская 87\nОфис №2: Казахская 25\nГрафик работы: Пн-Пт 9:00-19:00', parse_mode='html') 
    except Exception as e:      # works on python 3.x
         debugToLog(f'Error №11 - {str(e)}')
         bot.send_message(message.chat.id, str(e))  
        





# Запрос на получение номера телефона
@bot.message_handler (commands = ['number']) # Announced a branch to work on the <strong> number </strong> command
def phone (message):
    try:
        keyboard = types.ReplyKeyboardMarkup (row_width = 1, resize_keyboard = True) # Connect the keyboard
        button_phone = types.KeyboardButton (text = "Разрешить!", request_contact = True) # Specify the name of the button that the user will see
        keyboard.add (button_phone) #Add this button
        bot.send_message (message.chat.id, 'Пожалуйста, разрешите доступ к вашему номеру телефона для возможности уточнить информацию!', reply_markup = keyboard) 
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №12 - {str(e)}')
        bot.send_message(message.chat.id, str(e))  
 
@bot.message_handler (content_types = ['contact']) # Announced a branch in which we prescribe logic in case the user decides to send a phone number :)
def contact (message):
    try:
        message_id = message.message_id  
        if message.contact is not None: # If the sent object <strong> contact </strong> is not zero
            if Users.objects.filter(userChatTelegramId=message.contact.user_id).exists():
                getDay = Users.objects.filter(userChatTelegramId=message.contact.user_id).get()
                getDay.phone = message.contact.phone_number
                getDay.save()
                # Journal.objects.filter(name=todayDate).update(number=(int(x1) + 1))
            else:
                newPay = Users(userChatTelegramId=message.contact.user_id, phone=message.contact.phone_number, firstName=message.contact.first_name)
                newPay.save()
        x3 = f'Клиент с Id: {message.contact.user_id} поделился телефоном: {message.contact.phone_number}'
        bot.send_message (message.chat.id, 'Отлично! Теперь мы сможем с Вами связаться!', reply_markup=hideBoard) 
        bot.send_message (ADMIN_CHAT_ID, x3) 
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №13 - {str(e)}')
        bot.send_message(message.chat.id, str(e)) 




@bot.message_handler(commands=['user'])
def clientId(message):
    try: 

        if TeleOrders.objects.filter(userChatTelegramId=message.chat.id, doneStatus=False).exists():
            useOrders = TeleOrders.objects.filter(userChatTelegramId=message.chat.id)   
            x1 = ''
            x2 = 1
            for x in useOrders:
                x1 += f'№{x2}; Цена: {x.cost}; Оплачено: {"Да" if x.payStatus else "Нет"}; Готово: {"Да" if x.doneStatus else "Нет"}.\n'
                x2 += 1
            bot.send_message (message.chat.id, f'{x1}', parse_mode='html') 
        else:

            bot.send_message (message.chat.id, 'У Вас нет не выполненных заказов!') 
    except Exception as e:      # works on python 3.x
         debugToLog(f'Error №14 - {str(e)}')
         bot.send_message(message.chat.id, str(e)) 
        



























# ADMIN COMMANDS:
@bot.message_handler(commands=['admin'])
def clientId(message):
    try: 
        # bot.sendMessage(chatId, '<b>TEST</b>', {parse_mode: 'HTML'})
        bot.send_message(message.chat.id, 'Привет администратор!'
                                            # '\n/alert_done_orders - оповестить клиентов о готовности заказа'
                                            '\n/user_phone_by_id - попросить клиента связаться по его id'
                                            '\n/get_orders - получить 10 последних заказов'
                                            '\n/get_order_by_id - получить информацию о заказе по его id')
    except Exception as e: 
         debugToLog(f'Error №15 - {str(e)}')
         bot.send_message(message.chat.id, str(e)) 


@bot.message_handler(commands=['user_phone_by_id'])
def clientId(message):
    try: 
        chat_id = message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            mesg = bot.send_message(message.chat.id, 'Введите id клиента:')
            bot.register_next_step_handler(mesg, loop1)
        else:
            bot.send_message(message.chat.id, 'Только администратор может использовать эту команду!')
    except Exception as e:      # works on python 3.x
        bot.clear_step_handler_by_chat_id(message.chat.id)
        debugToLog(f'Error №16 - {str(e)}')
        bot.send_message(message.chat.id, str(e)) 

def loop1(message):
    try:
        x1 = re.search(r"\d+", message.text)
        if not x1 :
            raise Exception("Значение id не корректное! Начните заново!")
        x2 = int(x1.group())
        bot.send_message(x2, 'Уважаемый клиент, пожалуйста поделитесь с нами вашим номером телефона для уточнения заказа, нажав на /number')
        bot.send_message(message.chat.id, 'Сообщение отправлено клиенту. Вы получите уведомление как только он поделится своим телефоном, а также запись появится в базе данных!')


    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №17 - {str(e)}')
        bot.send_message(message.chat.id, str(e))



@bot.message_handler(commands=['get_orders'])
def clientId(message):
    try: 
        chat_id = message.chat.id
        if chat_id == ADMIN_CHAT_ID:
            if TeleOrders.objects.filter(doneStatus=False).exists():
                useOrders = TeleOrders.objects.filter(doneStatus=False).order_by("-created_at")[0:10].all().values()
                print(useOrders)
                x3 = ''
                for x in useOrders:
                    x3 += f'id: {x["id"]}; Цена: {x["cost"]}; Оплачено: {"Да" if x["payStatus"] else "Нет"}; Готово: {"Да" if x["doneStatus"] else "Нет"}.\n'

                bot.send_message(message.chat.id, x3) 
        else:
            bot.send_message(message.chat.id, 'Только администратор может использовать эту команду!')

    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №18 - {str(e)}')
        bot.send_message(message.chat.id, str(e)) 
        




@bot.message_handler(commands=['get_order_by_id'])
def clientId(message):
    try: 
        # chat_id = message.chat.id
        # if chat_id == ADMIN_CHAT_ID:
            mesg = bot.send_message(message.chat.id, 'Введите id заказа:')
            bot.register_next_step_handler(mesg, loop2)
        # else:
            # bot.send_message(message.chat.id, 'Только администратор может использовать эту команду!')

    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №19 - {str(e)}')
        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.send_message(message.chat.id, str(e)) 

def loop2(message):
    try:
        x1 = re.search(r"\d+", message.text)
        if not x1 :
            raise Exception("Значение id не корректное! Начните заново!")
        x2 = int(x1.group())
        if TeleOrders.objects.filter(id=x2).exists():
            useOrders = TeleOrders.objects.get(id=x2)  

            bot.send_message (message.chat.id, f'id: {useOrders.id}, цена: {useOrders.cost}, название: {useOrders.name}, описание: {useOrders.description}') 

            if len(json.loads(useOrders.messages)) > 0:
                bot.forward_messages(message.chat.id, useOrders.userChatTelegramId, json.loads(useOrders.messages))


            linked_user = f'[Клиент](tg://user?id={useOrders.userChatTelegramId})'
            bot.send_message(message.chat.id, f'{linked_user}',
            parse_mode='MarkdownV2',
            disable_web_page_preview=True)
        else:
            raise Exception("Такого id заказа не существует!")

    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №20 - {str(e)}')
        bot.send_message(message.chat.id, str(e))

























# Диспетчер
@bot.message_handler(content_types=['text'])
def func(message):
    try:
        bot.send_message(message.chat.id, '...', reply_markup=hideBoard)
        x1 = 0
        for x in goodsArray:
            if re.search(fr"{x[1]}", message.text, re.IGNORECASE):

                    keyboard = telebot.types.InlineKeyboardMarkup()
                    button_save = telebot.types.InlineKeyboardButton(text="Подтвердить!", callback_data=f'{x[0]}')
                    keyboard.add(button_save)
                    bot.send_message(message.chat.id, f'Вы хотите -  {x[2]}?', reply_markup=keyboard)
                    x1 = 1
                    break

        if x1 == 0:
            bot.send_message(message.chat.id, 'Возможно допущена опечатка или в моей базе пока нет такого ТОВАРА!'
                                                '\n/help - нажмите, если Вам нужна помощь!')

    except Exception as e:      # works on python 3.x
         debugToLog(f'Error №21 - {str(e)}')
         bot.send_message(message.chat.id, str(e))
        



# Для товаров, которые скоро появятся!
@bot.callback_query_handler(func=lambda call: call.data == 'soon')
def clientId(call):
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбор сделан!")
        bot.send_message(call.message.chat.id, 'Для данного товара СКОРО будет подготовлен прайс-лист!', parse_mode="Markdown")
    except Exception as e:      # works on python 3.x
        debugToLog(f'Error №22 - {str(e)}')
        bot.send_message(message.chat.id, str(e))
        

# Для товаров в магазине
@bot.callback_query_handler(func=lambda call: call.data in ['cards_store', 'stickers_store', 'banner_store', 'badge_store'])
def clientId(call):
    try:
        message = call.message
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбор сделан!")
        keyboard = types.ReplyKeyboardMarkup(row_width=1)
        webApp = types.WebAppInfo(f'{goodsDict[call.data][2]}') 
        one = types.KeyboardButton(text=f'Калькулятор {goodsDict[call.data][1]}', web_app=webApp)
        keyboard.add(one) 
        bot.send_message(message.chat.id, 'Нажмите на кнопку снизу для запуска:', parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:      # works on python 3.x
         debugToLog(f'Error №23 - {str(e)}')
         bot.send_message(message.chat.id, str(e))


# Для товаров по ссылке
@bot.callback_query_handler(func=lambda call: call.data in ['tv_pereplet', 'chertej', 'scan', 'ksero', 'lamin', 'brosh', 'photo_doc', 'rizograf', 'pechat_3d', 'pechat_holst', 'sites', 'pechat_main', ])
def agent(call):
    try:
        message = call.message
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Выбор сделан!")
        keyboard = types.ReplyKeyboardMarkup(row_width=1) #создаем клавиатуру
        x1 = []
        for x in goodsDict[call.data][1]:
            webApp = types.WebAppInfo(x[1])
            x1.append(types.KeyboardButton(text=x[0], web_app=webApp))

        keyboard.add(*x1) #добавляем кнопки в клавиатуру
        bot.send_message(message.chat.id, 'Нажмите на кнопку ниже, чтобы открыть прайс-лист ⬇️', parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:      # works on python 3.x
         debugToLog(f'Error №24 - {str(e)}')
         bot.send_message(message.chat.id, str(e))
        

