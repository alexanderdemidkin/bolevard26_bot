import telebot
from telebot import types
import answer_list
import os
from transliterate import translit
import sqllite_helper as sq
from io import BytesIO

bot = telebot.TeleBot("Bot Token", parse_mode=None)

dir_docs = os.getcwd() + '/docs'
dir_instr = os.getcwd() + '/instr'

###################   start  ###################################
@bot.message_handler(commands=['start'])
def start_bot(message):
    bot.send_message(message.chat.id,answer_list.welcome)

###################   phone  ###################################

@bot.message_handler(commands=['contacts'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    buttonA = types.KeyboardButton('Телефоны служб ТСН')
    buttonB = types.KeyboardButton('Контакты совета дома')

    markup.row(buttonA, buttonB)
    bot.send_message(message.chat.id,'выберите действие', reply_markup=markup) 


@bot.message_handler(regexp='Телефоны служб ТСН')
def test1(message):    
	bot.send_message(message.chat.id,answer_list.phones)
        
@bot.message_handler(regexp='Контакты совета дома')
def test1(message):    
	bot.send_message(message.chat.id,answer_list.contacts)
        

###################   offer  ###################################      

@bot.message_handler(commands=['offer'])
def start(message):
  markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
  buttonA = types.KeyboardButton('Внести предложение')
  buttonB = types.KeyboardButton('Посмотреть предложения')
  buttonC = types.KeyboardButton('История предложений')

  markup.row(buttonA, buttonB, buttonC)
  bot.send_message(message.chat.id,'выберите действие', reply_markup=markup)
  #bot.send_message(message.chat.id,'выбрано', reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(regexp='Внести предложение')
def add_offer(message):
    chat_id = message.from_user.id
    msg = bot.send_message(message.chat.id,'Напишите ваше предложение по благоустройству',reply_markup=types.ReplyKeyboardRemove() )
    bot.register_next_step_handler(msg,add_offer_step,chat = chat_id)


def add_offer_step(message,chat):
    offer_list = []
    offer_list.append(chat)
    offer_list.append(message.text)
    sq.insert_offers(offer_list)
    bot.send_message(message.chat.id,'ваше предложение зарегистрировано')




@bot.message_handler(regexp='Посмотреть предложения')
def offer_view(message):
    bot.send_message(message.chat.id,sq.select_offer_year())
    

@bot.message_handler(regexp='История предложений')
def offer_hist(message):
    bot.send_message(message.chat.id,sq.select_offers_history(message.from_user.id))



###################   meters  ###################################  


	
@bot.message_handler(commands=['meters'])
def meter_start(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
    buttonA = types.KeyboardButton('Внести показания')
    buttonB = types.KeyboardButton('Посмотреть показания')
    buttonC = types.KeyboardButton('История показаний')
    markup.row(buttonA, buttonB, buttonC)
    bot.send_message(message.chat.id,'выберите действие', reply_markup=markup)


@bot.message_handler(regexp='Внести показания')
def meter_add(message):
    msg = bot.send_message(message.chat.id,'Введите номер квартиры',reply_markup=types.ReplyKeyboardRemove() )
    bot.register_next_step_handler(msg,meter_add_quart,user = message.from_user.id)


def meter_add_quart(message,user):
    meter = []
    name = message.text
    if name.isdigit() and int(name) in range(1,150):
        meter.append(user)
        meter.append(name)
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)
        buttonA = types.KeyboardButton('ХВС')
        buttonB = types.KeyboardButton('ГВС')
        markup.row(buttonA, buttonB)
        msg = bot.send_message(message.chat.id, 'Выберите тип счетчика', reply_markup=markup)
        bot.register_next_step_handler(msg, meter_value_step,mt = meter)
    else:
        bot.send_message(message.chat.id,'Введена неверная квартира')




def meter_value_step(message,mt):
    name = message.text
    if name in ('ХВС','ГВС'):
        mt.append(name)
        msg = bot.send_message(message.chat.id,'Введите показания счетчика',reply_markup=types.ReplyKeyboardRemove() )
        bot.register_next_step_handler(msg,meter_end_step,meter = mt)
    else:
        bot.send_message(message.chat.id,'Введен неверный тип счетчика')


def meter_end_step(message,meter):
    name = message.text
    if name.isdigit(): 
        meter.append(float(name))
        sq.insert_counters(meter)
        bot.send_message(message.chat.id,'Данные успешно переданы квартира {kv} счетчик {st} значение {vl}'.format(kv = meter[1],st = meter[2],vl = meter[3]) )
    else: 
        bot.send_message(message.chat.id,'Введено неверное значение')



@bot.message_handler(regexp='Посмотреть показания')
def offer_view(message):
    sq.select_counters_month()
    with open('Показания.xlsx', 'rb') as tmp:
        obj = BytesIO(tmp.read())
        obj.name = 'Показания_счетчиков.xlsx'
        bot.send_document(message.chat.id, obj)




@bot.message_handler(regexp='История показаний')
def offer_hist(message):
    bot.send_message(message.chat.id,sq.select_counters_history(message.from_user.id))




# def process_age_step(message):
#     try:
#         chat_id = message.chat.id
#         age = message.text
#         if not age.isdigit():
#             msg = bot.reply_to(message, 'Age should be a number. How old are you?')
#             bot.register_next_step_handler(msg, process_age_step)
#             return
        

#         user = user_dict[chat_id]
#         user.age = age
#         markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
#         markup.add('Male', 'Female')
#         msg = bot.reply_to(message, 'What is your gender', reply_markup=markup)
#         bot.register_next_step_handler(msg, process_sex_step)
#     except Exception as e:
#         bot.reply_to(message, 'oooops')


###################   docs  ###################################  


@bot.message_handler(commands=[''])
def welcome(message):
    filenames = os.listdir(dir_docs)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)

    for fl in filenames:
        fl = types.KeyboardButton(fl)
        markup.add(fl)
    mesg = bot.send_message(message.chat.id,'выберите документ', reply_markup=markup)
    #bot.send_document(message.chat.id,file)
    bot.register_next_step_handler(mesg,file_send_next_step)

def file_send_next_step(message):
    #file = open(dir_docs + '/' + message.text)
    with open(dir_docs + '/' + message.text, 'rb') as tmp:
        obj = BytesIO(tmp.read())
        obj.name = message.text
        bot.send_document(message.chat.id, obj)
    #bot.send_message(message.chat.id,file)


###################   instr  ################################### 


@bot.message_handler(commands=['instr'])
def welcome(message):
    filenames = os.listdir(dir_instr)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,resize_keyboard=True)

    for fl in filenames:
        fl = types.KeyboardButton(fl)
        markup.add(fl)
    mesg = bot.send_message(message.chat.id,'выберите инструкцию', reply_markup=markup)
    #bot.send_document(message.chat.id,file)
    bot.register_next_step_handler(mesg,instr_send_next_step)

def instr_send_next_step(message):
    with open(dir_instr + '/' + message.text, 'rb') as tmp:
        obj = BytesIO(tmp.read())
        obj.name = message.text
        bot.send_document(message.chat.id, obj)



bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.infinity_polling()
