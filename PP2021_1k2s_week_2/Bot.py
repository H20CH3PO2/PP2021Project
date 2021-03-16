#UPDATE 0.04
#Добавлены задержки перед отправлением новостей во имя избежания ошибок из-зи большого количества запросов.
#Нажатия пользователя на кнопки теперь обрабатывается в одной функции.
#Убрана команда /nextnews. В место нее теперь универсальная команда /newnews.
#Добавлена команда /everydayNews. Она является переключателем для функции ежедневного вывода новостей.


import DataBase
import PesronList
import telebot
from telebot import types
from psycopg2 import Error
import threading
import time

bot = telebot.TeleBot('1631242798:AAEBKc1x16vZpEO3QkzAecK5HEM8jE2v510')
person_name = "No_Name"     #Имя гостя
number_of_artical = 0       #Текущая статья
page_count = 5              #Кол-во статей за 1 вывод
page = 0                    #Текущая страница
everydayNews = False


#Создание списка новостей
def get_news():
    rss_list = []
    DataBase.open_db_connection()
    list_rss_news = DataBase.get_all_rss()
    DataBase.close_db_connection()
    for row in list_rss_news:
        print(row)
        content = "" + row[2]
        rss_list.append([f"   <b><u>{row[1]}</u></b>\n <b>Опубликовано:</b> {row[3]:%d/%m/%Y}\n <b>Сайт: {row[0]}</b>\n======================================\n{content[0:500]}", row[0]])
    return rss_list


#Регистрация оценкок пользователя
def register_grades(person_name, rss_list, grade, number_of_artical):
    PesronList.open_db_connection_p()
    PesronList.write_one_row_in_db_p(person_name, rss_list[number_of_artical][1], grade)
    PesronList.close_db_connection_p()

#Получение статей
rss_list = get_news()

def everydayNews(everydayNews):
    rss_list = get_news();



#Выводим лист всех RSS подписок.
#TODO: сделать возможность удалять или дополнять этот лист RSS подписками по вводу 1й RSS ссылки
@bot.message_handler(commands=['list'])
def start_message(message):
    bot.send_message(message.chat.id, DataBase.RSS_feeds(), None)


# Регистрация пользователя по имени, т.е. запись его в глобальную переменную
#TODO: фигня какая-то. Вообще переделать и сделать автоматическим.
@bot.message_handler(commands=['register'])
def start_message(message):
    bot.send_message(message.chat.id, "Регистрация пользователя завершена!", None)
    global person_name
    person_name = message.from_user.id


#Вывод следующих page_count статей
@bot.message_handler(commands=['newnews'])
def next_news(message):
    global rss_list
    global page
    global page_count
    global number_of_artical
    if (page + 1)*page_count < len(rss_list):
        for i in range(page_count*page, page_count*(page + 1)):
            keyboard = types.InlineKeyboardMarkup()
            one_k = types.InlineKeyboardButton(text='1', callback_data='1')
            two_k = types.InlineKeyboardButton(text='2', callback_data='2')
            three_k = types.InlineKeyboardButton(text='3', callback_data='3')
            four_k = types.InlineKeyboardButton(text='4', callback_data='4')
            five_k = types.InlineKeyboardButton(text='5', callback_data='5')
            keyboard.add(one_k, two_k, three_k)
            keyboard.add(four_k, five_k)
            try:
                bot.send_message(message.chat.id, rss_list[i][0], reply_markup=keyboard, parse_mode="HTML")
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
                number_of_artical += 1
            time.sleep(1)
    else:
        for i in range(page_count*page, len(rss_list)):
            keyboard = types.InlineKeyboardMarkup()
            one_k = types.InlineKeyboardButton(text='1', callback_data='1')
            two_k = types.InlineKeyboardButton(text='2', callback_data='2')
            three_k = types.InlineKeyboardButton(text='3', callback_data='3')
            four_k = types.InlineKeyboardButton(text='4', callback_data='4')
            five_k = types.InlineKeyboardButton(text='5', callback_data='5')
            keyboard.add(one_k, two_k, three_k)
            keyboard.add(four_k, five_k)
            try:
                bot.send_message(message.chat.id, rss_list[i][0], reply_markup=keyboard, parse_mode="HTML")
            except (Exception, Error) as error:
                print("Ошибка при работе с PostgreSQL", error)
                number_of_artical += 1
            time.sleep(1)
    page += 1


@bot.message_handler(commands=['everydayNews'])
def everydayNews(message):
    keyboardYN = types.InlineKeyboardMarkup()
    one_k = types.InlineKeyboardButton(text='Да', callback_data='yes_everydayNews')
    two_k = types.InlineKeyboardButton(text='Нет', callback_data='no_everydayNews')
    keyboardYN.add(one_k, two_k)
    bot.send_message(message.chat.id, "Вы хотите каждый день получать рассылку новостей?", reply_markup=keyboardYN)


#Получаем ответ пользователя, т.е. обработка всех ответов кнопочек и всего подобного
#TODO: реализовать сохранение оценки не поочередно, а с помощью ID ответа
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    global rss_list
    global number_of_artical
    if call.data == "1" or call.data == "2" or call.data == "3" or call.data == "4" or call.data == "5":
        register_grades(person_name, rss_list, call.data, number_of_artical)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        number_of_artical += 1
        bot.send_message(call.message.chat.id, "Ваши оценка статьи записана!")
    global everydayNews
    if call.data == "yes_everydayNews":
        everydayNews = True
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Теперь каждый день в это время вам будут приходить новые статьи!')
    if call.data == "no_everydayNews":
        everydayNews = False
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Ежедневные новости отключены!')


bot.polling()
