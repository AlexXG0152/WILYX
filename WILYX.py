import collections
import logging
import sys
from collections import Counter

import instagram
import telebot
from instagram import Account, WebAgent

TOKEN = "token"

bot = telebot.TeleBot(TOKEN, True, 4)


@bot.message_handler(content_types=["text"])
def start(message):
    bot.send_message(message.chat.id, "<a>Привет! Я могу посчитать ТОП-10 пользователей, которые "
                                      "больше всего и чаще всего лайкают последние 50 "
                                      "публикаций из выбранного аккаунта. "
                                      "Пользуйся полученной информацией с умом.</a>", parse_mode="HTML")
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Напиши имя пользователя в Insagram. Например: username")
        bot.register_next_step_handler(message, get_name)
    else:
        bot.send_message(message.from_user.id, "Напиши /start")


@bot.message_handler(content_types=["text"])
def get_name(message):
    while True:
        try:
            global name
            name = message.text
            bot.send_message(message.from_user.id, "Работаю. Возможно придется немного подождать...")

            bot.register_next_step_handler(message, count(name))
            print(name)

        except Exception:
            logging.error("error: {}".format(sys.exc_info()[0]))
            break

        bot.register_next_step_handler(message, print_res())

        max_len = max([len(x[0]) for x in Counter(counter).most_common(10)])
        for element in Counter(counter).most_common(10):
            if element == ("0", 1):
                bot.send_message(message.from_user.id, "Ошибка. Проверьте введенные данные!")
                break
            else:
                bot.send_message(message.from_user.id, (
                    "https://www.instagram.com/{value0:{width0}}{value1}".format(value0=element[0], width0=max_len + 10,
                                                                                 value1=element[1])))
        bot.send_message(message.from_user.id, "С этим пользователем все выяснили, \n"
                                               "напиши /start для проверки следующего ")
        bot.clear_step_handler(message)
        return name


def count(name):
    while True:
        try:
            global counter
            agent = WebAgent()
            acc_name = name
            print("Вычисляем...")

            account = Account(acc_name)

            media1, pointer = agent.get_media(account)
            media2, pointer = agent.get_media(account, pointer=pointer, count=100, delay=1)

            posts = []

            for i in media2:
                try:
                    media = agent.get_likes(i, pointer=None, count=50, limit=5000, delay=10, settings=None)
                    postlike = ([i, media[:1]])
                    posts.append(postlike)
                except:
                    continue

            posts = dict(posts)
            counter = collections.Counter()

            string = []
            for key, value in posts.items():
                for i in value:
                    for x in i:
                        string.append(str(x))

            for word in string:
                counter[word] += 1

            return counter
        except instagram.exceptions.InternetException:
            logging.error("error: {}".format(sys.exc_info()[0]))
            counter = "0"
            break


def print_res():
    try:
        print("Пользователь", " " * 8, "Лайки")
        max_len = max([len(x[0]) for x in Counter(counter).most_common(10)])
        for element in Counter(counter).most_common(10):
            print("{value0:{width0}}{value1}".format(value0=element[0], width0=max_len + 5, value1=element[1]))
    except Exception:
        logging.error("error: {}".format(sys.exc_info()[0]))
        pass


bot.polling(none_stop=True, interval=0)


#  https://github.com/ping/instagram_private_api
#  https://instagram-private-api.readthedocs.io/en/latest/usage.html#web-api
###! https://instagram-private-api.readthedocs.io/en/latest/api.html#instagram_private_api.ClientCompatPatch.media
###! https://github.com/OlegYurchik/pyInstagram#authorized-agent
### https://stackoverflow.com/questions/28467372/python-is-there-a-way-to-pretty-print-a-list
### https://core.telegram.org/bots/api#formatting-options
### https://github.com/eternnoir/pyTelegramBotAPI#asynchronous-delivery-of-messages
