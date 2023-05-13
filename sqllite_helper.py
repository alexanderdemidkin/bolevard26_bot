import sqlite3
from xlsxwriter.workbook import Workbook


def select(sql_str):
    conn = sqlite3.connect('bolevard26.sqlite3')
    cur = conn.cursor()
    itog = cur.execute(sql_str).fetchall()
    conn.close()
    return itog


def insert(sql_str):
    conn = sqlite3.connect('bolevard26.sqlite3')
    cur = conn.cursor()
    cur.execute(sql_str)
    conn.commit()
    conn.close()
    return cur.lastrowid

def select_counters_history(chat_id):
    sql = f'SELECT quart,type_meter  ,value ,counter_time  from counters c where chat_id = {chat_id} order by 4 desc'
    it = select(sql)
    msg = 'История передачи показаний с вашего аккаунта: \n' 
    for i in it:
        msg += 'квартира: {qv} счетчик: {tp} показание: {vl} дата передачи: {dt}  \n'.format(qv=i[0],tp=i[1], vl=i[2],dt=i[3])
    return msg

def select_counters_month():
    sql ='SELECT quart,type_meter  ,value , counter_time  from counters c where counter_time >= date(CURRENT_DATE,"-1 month") order by 1,2'
    mysel = select(sql)
    workbook = Workbook('Показания.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 0, 20)
    worksheet.set_column(1, 0, 20)
    worksheet.set_column(2, 0, 20)
    worksheet.set_column(3, 0, 30)
    worksheet.write(0,0,u'Кваритира')
    worksheet.write(0,1,u'Счетчик')
    worksheet.write(0,2,u'Значение')
    worksheet.write(0,3,u'Дата передачи')
    for i, row in enumerate(mysel):
        i = i + 1
        worksheet.write(i, 0, row[0])
        worksheet.write(i, 1, u'{rw}'.format(rw = row[1]   ))
        worksheet.write(i, 2, row[2])
        worksheet.write(i, 3, row[3])
    workbook.close()
    return "ok"

def insert_counters(meter_list):
    sql = 'insert into counters (quart,type_meter ,value,chat_id) values ("{qv}","{tp}",{vl},{ct})'.format(qv = meter_list[1],tp = meter_list[2],vl = meter_list[3], ct=meter_list[0])
    a = insert(sql)
    return a   

def select_offers_history(chat_id):
    sql = f'SELECT o.offer_date as od,offer_text  from offers o where chat_id = {chat_id}'
    it = select(sql)
    msg = 'История передачи предложений с вашего аккаунта: \n' 
    for i in it:
        msg += 'дата предложения: {dt}  предложение: {vl}   \n'.format(vl=i[1],dt=i[0])
    print(msg)
    return msg

def select_offer_year():
    sql ='SELECT o.offer_date as od,offer_text  from offers o where o.offer_date >= date(CURRENT_DATE,"-1 year")'
    it = select(sql)
    msg = 'Все предложения по благоустройству за последний год: \n' 
    for i in it:
        msg += 'дата предложения: {dt}  предложение: {vl}   \n'.format(vl=i[1],dt=i[0])
    return msg

def insert_offers(offer):
    sql ='INSERT into offers (chat_id,offer_text) values ({ct},"{ofr}")'.format(ct = offer[0],ofr = offer[1])
    a = insert(sql)
    return a   








