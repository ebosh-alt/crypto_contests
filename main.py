# import json
import telebot

# from telebot import types
# import re
import datetime
import pickle

# from multiprocessing import *
# import schedule
# import time
from datetime import timedelta
# from flask import Flask, request
from keyboard import *


def save_object(data, file_name="tasks.pkl"):
    with open(file_name, "wb+") as fp:
        pickle.dump(data, fp)


def load_object(file_name="tasks.pkl"):
    with open(file_name, "rb+") as fp:
        data = pickle.load(fp)
    return data


class Contest:
    def __init__(self):
        self.contract_number = None
        self.time_start_contest = None
        self.time_end_contest = None
        self.time_start_registration = None
        self.time_end_registration = None
        self.time_end_for_new_user = None
        self.text_final = "Конкурс окончен"
        self.photo_final = None
        self.text_announcement = "Начался конкурс"
        self.photo_announcement = None
        self.text_for_new_leader = "Появился новый лидер"
        self.photo_for_new_leader = None
        self.text_encouragement = "Поднажмите"
        self.photo_encouragement = None
        self.time_inaction = None
        self.time_reminder = None
        self.text_reminder = "Идет конкурс"
        self.photo_reminder = None
        self.max_transaction = 0
        self.wallet_leader = None
        self.username_leader = None
        self.stop_list = []

    def variables_for_mes(self, value):
        match value:
            case "time_start_contest":
                return self.time_start_contest
            case "time_end_registration":
                return self.time_end_registration
            case "remaining_time_contest":
                return self.time_end_registration - datetime.now()
            case "remaining_time_registration":
                return self.time_end_registration - datetime.now()
            case "wallet_leader":
                return self.wallet_leader
            case "username_leader":
                return self.username_leader


class User:
    def __init__(self):
        self.flag = 0
        self.wallet = None
        self.status_of_last_registration = False
        self.message_id = 0
        self.status = True


class Users:
    count_user = 0

    def __init__(self):
        self.data = {}

    def __add__(self, id):
        self.data[id] = User()
        Users.count_user += 1
        return self

    def set_message_id(self, id, value):
        self.data[id].message_id = value

    def set_flag(self, id, value):
        self.data[id].flag = value

    def set_wallet(self, id, value):
        self.data[id].wallet = value

    def set_status_of_last_registration(self, id):
        self.data[id].status_of_last_registration = True

    def set_status(self, id, value):
        if id not in self.data:
            self.data[id] = User()
        self.data[id].status = value

    def get_status(self, id):
        return self.data[id].status

    def get_status_of_last_registration(self, id):
        return self.data[id].status_of_last_registration

    def get_message_id(self, id):
        return self.data[id].message_id

    def get_flag(self, id):
        return self.data[id].flag

    def get_wallet(self, id):
        return self.data[id].wallet

    def get_user(self, id):
        return self.data[id]

    def get_all(self):
        return self.data

    def get_wallet_list(self):
        wallet_list = []
        for i in self.data:
            wallet_list.append(self.data[i].wallet)
        return wallet_list


contest = load_object("contest.pkl")
users_bd = load_object("users_bd.pkl")
#print(users_bd.__dict__)
start_text = "Вас приветствует xxx. Какое-то описание необходимо"
admin = [5191469996, 2059338796]
API_TOKEN = "5002199932:AAEGc9BEvAsIPF9ro4Ig1HaNmKAtTcmq8QA"
bot = telebot.TeleBot(API_TOKEN)
bot.delete_webhook()
data_text_for_create_contest = {1: 'введите номер контракта',
                                2: 'введите начало конкурса(ДД.ММ.ГГ ЧЧ)',
                                3: 'введите конец конкурса(ДД.ММ.ГГ ЧЧ)',
                                4: 'введите за сколько до начала конкурса открывается регистрация(в минутах)',
                                5: 'введите за сколько до окончания конкурса закрывается регистрация(в минутах)',
                                6: 'введите за сколько до окончания конкурса '
                                   'новые участники не смогут попасть в конкурс (в минутах)',
                                7: 'через сколько минут бездействия, надо писать в чат сообщение?(в минутах)',
                                8: 'через сколько минут напоминать о том, что идет конкурс?(в минутах)'}


@bot.message_handler(func=lambda message: message.from_user.id in users_bd.data and not users_bd.get_status(
    message.from_user.id))
def other(message):
    global users_bd
    user_id = message.from_user.id
    bot.send_message(chat_id=user_id,
                     text="Ваш профиль заблокирован в нашем сервисе")
    # save_object(contest, "contest.pkl")


@bot.message_handler(commands=["start"])
def start(message):
    global users_bd
    user_id = message.from_user.id
    #print(user_id)
    if str(user_id) in contest.stop_list:
        users_bd.set_status(user_id)
        bot.send_message(chat_id=user_id,
                         text="Ваш профиль заблокирован в нашем сервисе")
        save_object(contest, "contest.pkl")

    if user_id not in users_bd.data:
        users_bd += user_id
        r = bot.send_message(chat_id=user_id,
                             text=start_text)
        users_bd.set_message_id(user_id, r.id)
        save_object(users_bd, "users_bd.pkl")
    elif user_id in users_bd.data:
        r = bot.send_message(chat_id=user_id,
                             text=start_text)
        users_bd.set_message_id(user_id, r.id)
        save_object(users_bd, "users_bd.pkl")


@bot.message_handler(commands=["admin"], func=lambda message: message.from_user.id in admin)
def command_admin(message):
    global admin
    user_id = message.from_user.id
    r = bot.send_message(chat_id=user_id,
                         text="Выберите действие",
                         reply_markup=admin_start)

    users_bd.set_message_id(user_id, r.id)


@bot.message_handler(commands=["reg"])
def reg(message):
    global users_bd
    user_id = message.from_user.id
    r = bot.send_message(chat_id=user_id,
                         text="Вы можете зарегистрироваться",
                         reply_markup=registration_for_contest)
    users_bd.set_flag(user_id, 9)
    users_bd.set_message_id(user_id, r.id)


@bot.message_handler(func=lambda message: (users_bd.get_flag(message.from_user.id) == 9))
def reg_wallet(message):
    global users_bd, contest
    user_id = message.from_user.id
    #print(users_bd.get_status_of_last_registration(user_id))
    if str(user_id) in contest.stop_list or message.text in contest.stop_list:
        users_bd.set_status(user_id, False)
        bot.send_message(chat_id=user_id,
                         text="Ваш профиль заблокирован в нашем сервисе")
        save_object(contest, "contest.pkl")

    elif not users_bd.get_status_of_last_registration(user_id):
        users_bd.set_wallet(user_id, message.text)
        users_bd.set_status_of_last_registration(user_id)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Вы успешно зарегистрированы!")
        users_bd.set_flag(user_id, 0)
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        save_object(users_bd, "users_bd.pkl")


@bot.callback_query_handler(func=lambda call: call.data == "registration_for_contest")
def call_reg(call):
    global users_bd
    user_id = call.from_user.id
    #print(users_bd.get_status_of_last_registration(user_id))
    if str(user_id) in contest.stop_list:
        users_bd.set_status(user_id, False)
        bot.send_message(chat_id=user_id,
                         text="Ваш профиль заблокирован в нашем сервисе")
        save_object(contest, "contest.pkl")

    if not users_bd.get_status_of_last_registration(user_id):
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Введите номер кошелька")
        users_bd.set_flag(user_id, 9)


@bot.message_handler(content_types=["text", "photo", "document"],
                     func=lambda message: (message.from_user.id in admin) and
                                          (users_bd.get_flag(message.from_user.id) != 9))
def work__admin(message):
    global users_bd, contest
    user_id = message.from_user.id
    flag = users_bd.get_flag(user_id)

    if flag in [11, 12, 13, 14, 15]:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        if message.photo is None:
            if "{" in message.text and "}" in message.text:
                s = message.text.split(' ')
                txt = ''
                for i in range(0, len(s)):
                    if '{' in s[i] and '}' in s[i]:
                        s[i] = s[i].replace('{', '').replace('}', '')
                        # print(contest.variables_for_mes(s[i]))
                        txt += f'{contest.variables_for_mes(s[i])}'
                    else:
                        txt += s[i] + ' '
            else:
                txt = message.text
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=f"Вы ввели: \n" + f'{txt}',
                                  reply_markup=complete_or_change_new_text)
            if flag == 11:
                contest.text_final = message.text

            elif flag == 12:
                contest.text_announcement = message.text

            elif flag == 13:
                contest.text_for_new_leader = message.text

            elif flag == 14:
                contest.text_final = message.text

            elif flag == 15:
                contest.text_reminder = message.text

        else:
            if flag == 11:
                contest.photo_final = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_final,
                               caption=contest.text_final,
                               reply_markup=complete_or_change_new_text2)
            elif flag == 12:
                contest.photo_announcement = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_announcement,
                               caption=contest.text_announcement,
                               reply_markup=complete_or_change_new_text2)

            elif flag == 13:
                contest.photo_for_new_leader = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_for_new_leader,
                               caption=contest.text_for_new_leader,
                               reply_markup=complete_or_change_new_text2)

            elif flag == 14:
                contest.photo_encouragement = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_encouragement,
                               caption=contest.text_encouragement,
                               reply_markup=complete_or_change_new_text2)

            elif flag == 15:
                contest.photo_reminder = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_reminder,
                               caption=contest.text_reminder,
                               reply_markup=complete_or_change_new_text2)

    elif flag in [1, 2, 3, 4, 5, 6, 7, 8]:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"Вы ввели: \n{message.text}",
                              reply_markup=complete_or_change_contest)

    elif flag == 10:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        check = True
        if message.text.isdigit():
            if int(message.text) in users_bd.data:
                users_bd.set_status(int(message.text), False)
                #print(111111111111111)
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Пользователь заблокирован",
                                      reply_markup=back_in_admin_panel)
                check = False

        if message.text in users_bd.get_wallet_list() and check:
            for i in users_bd.data:
                if users_bd.data[i].wallet == message.text:
                    users_bd.set_status(int(i), False)
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text="Пользователь заблокирован",
                                          reply_markup=back_in_admin_panel)

                    check = False
                    break
        elif check:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=f"пользователь/кошелек - {message.text} не найден. Добавить в стоп лист?",
                                  reply_markup=action_stop_list)

    elif flag == 17:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        if message.text.isdigit():
            if int(message.text) in users_bd.data:
                users_bd.set_status(int(message.text), True)
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Пользователь разблокирован",
                                      reply_markup=back_in_admin_panel)

        if message.text in users_bd.get_wallet_list():
            for i in users_bd.data:
                if users_bd.data[i].wallet == message.text:
                    users_bd.set_status(int(i), True)
                    break

            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text="Пользователь разблокирован",
                                  reply_markup=back_in_admin_panel)


@bot.callback_query_handler(func=lambda call: call.from_user.id in admin and users_bd.get_flag(call.from_user.id) != 9)
def work_admin(call):
    global contest, data_text_for_create_contest
    user_id = call.from_user.id

    if call.data == "add_contest":
        users_bd.set_flag(user_id, 1)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=data_text_for_create_contest[users_bd.get_flag(user_id)],
                              reply_markup=back_in_admin_panel)

    elif call.data == "complete_value_contest":
        ###check maximum flag
        flag = users_bd.get_flag(user_id)

        new_set = call.message.text.split('\n')[1]
        if flag == 1:
            contest.contract_number = new_set
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
            users_bd.set_flag(user_id, flag + 1)

        elif flag == 2:
            new_set = new_set.replace('.', ' ').split(' ')
            if len(new_set) == 4:
                try:  # день.месяц.год час
                    time_start = datetime.datetime(year=int(new_set[2]),
                                                   month=int(new_set[1]),
                                                   day=int(new_set[0]),
                                                   hour=int(new_set[3]),
                                                   minute=0)

                    contest.time_start_contest = time_start
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
                    users_bd.set_flag(user_id, flag + 1)

                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")
        elif flag == 3:
            new_set = new_set.replace('.', ' ').split(' ')
            if len(new_set) == 4:
                try:
                    time_end = datetime.datetime(year=int(new_set[2]),
                                                 month=int(new_set[1]),
                                                 day=int(new_set[0]),
                                                 hour=int(new_set[3]),
                                                 minute=0)
                    if time_end > contest.time_start_contest:
                        contest.time_end_contest = time_end

                        bot.edit_message_text(chat_id=user_id,
                                              message_id=users_bd.get_message_id(user_id),
                                              text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
                        users_bd.set_flag(user_id, flag + 1)
                    else:
                        bot.edit_message_text(chat_id=user_id,
                                              message_id=users_bd.get_message_id(user_id),
                                              text="Скорее всего Вы написали не в правильном формате. "
                                                   "Попробуйте ещё раз")

                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

        elif flag == 4:

            if new_set.isdigit():
                try:  # день.месяц.год час
                    detime = timedelta(minutes=int(new_set))
                    new_set = contest.time_start_contest - detime
                    contest.time_start_registration = new_set

                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
                    users_bd.set_flag(user_id, flag + 1)
                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

        elif flag == 5:
            if new_set.isdigit():
                try:  # день.месяц.год час
                    detime = timedelta(minutes=int(new_set))
                    new_set = contest.time_end_contest - detime
                    contest.time_end_registration = new_set
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
                    users_bd.set_flag(user_id, flag + 1)
                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

        elif flag == 6:
            if new_set.isdigit():
                try:  # день.месяц.год час
                    detime = timedelta(minutes=int(new_set))
                    new_set = contest.time_end_contest - detime
                    contest.time_end_for_new_user = new_set
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
                    users_bd.set_flag(user_id, flag + 1)
                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

        elif flag == 7:
            if new_set.isdigit():
                try:  # день.месяц.год час
                    contest.time_inaction = int(new_set)
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1])
                    users_bd.set_flag(user_id, flag + 1)
                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

        elif flag == 8:
            if new_set.isdigit():
                try:  # день.месяц.год час
                    contest.time_reminder = int(new_set)
                    bot.edit_message_text(chat_id=user_id,
                                          message_id=users_bd.get_message_id(user_id),
                                          text=f"Конкурс выглядит так:\n"
                                               f"номер контракта: {contest.contract_number}\n"
                                               f"начало конкурса: {contest.time_start_contest}\n"
                                               f"конец конкурса: {contest.time_end_contest}\n"
                                               f"время открытия регистрации: {contest.time_start_registration}\n"
                                               f"время закрытии регистрации: {contest.time_end_registration}\n"
                                               f"время закрытия конкурса от новых участников: "
                                               f"{contest.time_end_for_new_user}\n"

                                               f"время бездействия для отправки уведомления: "
                                               f"{contest.time_inaction} минут(а)\n"

                                               f"периодичность напоминания о конкурсе: "
                                               f"{contest.time_reminder} минут(а)\n"

                                               f"текст анонса: {contest.text_announcement}\n"
                                               f"текст финала: {contest.text_final}\n"
                                               f"текст отдачи статуса: {contest.text_for_new_leader}\n"
                                               f"текст поддержки: {contest.text_encouragement}\n"
                                               f"текст напоминания: {contest.text_reminder}\n"
                                               f"текст Вы можете изменить в админ панель -> изменить текста")
                    save_object(contest, "contest.pkl")
                    users_bd.set_flag(user_id, 0)
                except Exception as ex:
                    bot.answer_callback_query(callback_query_id=call.id,
                                              text=str(ex),
                                              show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

    elif call.data == "change_introduced_value_contest":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=data_text_for_create_contest[users_bd.get_flag(user_id)])

    elif call.data == "change_text":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Выберите действие",
                              reply_markup=admin_change_text)
        users_bd.set_flag(user_id, 0)

    elif call.data == "change_announcement":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_announcement}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 12)

    elif call.data == "change_final":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_final}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 11)

    elif call.data == "change_status_return":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_for_new_leader}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 13)

    elif call.data == "change_support":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_encouragement}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 14)

    elif call.data == "change_reminder":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_reminder}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 15)

    elif call.data == "complete_new_text":
        try:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text='Изменение прошло успешно',
                                      show_alert=True)
            if len(call.message.reply_markup.keyboard) == 2:
                bot.delete_message(chat_id=user_id,
                                   message_id=call.message.id)

            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text="Выберите действие",
                                  reply_markup=admin_start)
            users_bd.set_flag(user_id, 0)

        except Exception as ex:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text='Произошла ошибка' + str(ex),
                                      show_alert=True)
        finally:
            save_object(contest, "contest.pkl")

    elif call.data == "change_introduced_text":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="введите новый текст",
                              reply_markup=back_in_change_text)

    elif call.data == "block_user":
        id_wallet = ''
        data = users_bd.data
        for i in data:
            if data[i].status:
                id_wallet += f"`{i}` - `{data[i].wallet}` \n"
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"отправьте id пользователя или же его номер кошелька. "
                                   f"Вот данные, которые есть в базе данных(id - номер кошелька)\n"
                                   f"{id_wallet}",
                              reply_markup=back_in_admin_panel,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 10)
    elif call.data == "unblock_user":
        id_wallet = ''
        data = users_bd.data
        for i in data:
            #print(data[i].__dict__)
            if not data[i].status:
                id_wallet += f"`{i}` - `{data[i].wallet}` \n"

        if id_wallet == "":
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="на данный момент нет заблокированных пользователей или кошельков",
                                      show_alert=True)
        else:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=f"отправьте id пользователя или же его номер кошелька. "
                                       f"Вот данные, которые есть в базе данных(id - номер кошелька)\n"
                                       f"{id_wallet}",
                                  reply_markup=back_in_admin_panel,
                                  parse_mode="Markdown")
            users_bd.set_flag(user_id, 17)

    elif call.data == "yes_stop_list":
        id_wallet = call.message.text.split(" ")[2]
        contest.stop_list.append(id_wallet)
        bot.answer_callback_query(callback_query_id=call.id,
                                  text="пользователь добавлен в стоп лист",
                                  show_alert=False)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Выберите действие",
                              reply_markup=admin_start)
        users_bd.set_flag(user_id, 0)

    elif call.data == "add_photo":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Отправьте фотографию")

    elif call.data == "back_in_admin_panel":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Выберите действие",
                              reply_markup=admin_start)
        users_bd.set_flag(user_id, 0)


if __name__ == "__main__":
    print("START")
    bot.infinity_polling()
