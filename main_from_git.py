import datetime

import telebot
import pickle
#from selenium import webdriver
#from selenium.webdriver.common.by import By
#from selenium.webdriver.firefox.service import Service
#from webdriver_manager.firefox import GeckoDriverManager
#from selenium.webdriver import FirefoxOptions

from selenium import webdriver
#from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from multiprocessing import *
import schedule
import time
import json
from datetime import timedelta
# from flask import Flask, request
from keyboard import *
from classes import *
from config import *


def save_object(data, file_name="tasks.pkl"):
    with open(file_name, "wb+") as fp:
        pickle.dump(data, fp)


def load_object(file_name="tasks.pkl"):
    with open(file_name, "rb+") as fp:
        data = pickle.load(fp)
    return data


###сохранение файла в .json
def save_data(data, file_name="users_bd.json") -> None:
    with open(file_name, "w+", encoding="UTF-8") as f:
        json.dump(data, f, indent=4)


###загрузка файла из .json
def load_data(file_name="users_bd.json") -> dict:
    with open(file_name, "r+", encoding="UTF-8") as f:
        data = json.load(f)
    return data


def start_contest():
    contest_users = Contest_users()
    contest___ = Schedule_contest()
    contest = load_object(file_name="contest.pkl")
    print(contest.__dir__)
    print(contest.__dict__)
    schedule.every(contest.time_cooldown).minutes.do(contest___.main_func, contest_users)
    #        schedule.every(30).seconds.do(Schedule_contest.main_func, args=(process, leaders))

    while True:
        if contest___.logic_steps == 5:
            break
        schedule.run_pending()
        time.sleep(5)


class Schedule_contest:
    logic_steps = 0
    ending_an_hour = False
    time_of_last_reminder = None
    time_appear_new_leader = None
    print(logic_steps)

    def main_func(self, contest_users: Contest_users):
        contest = load_object(file_name="contest.pkl")
        contest_users = load_object(file_name="contest_users.pkl")
        users_bd = load_object(file_name="users_bd.pkl")
        cur_time = datetime.datetime.today()

        if contest.time_start_registration > cur_time:
            pass

        else:
            # Начало регистрации
            if self.logic_steps == 0:
                self.channel_sending(text=text_for_reg_in_chanel, contest=contest)
                self.sending_all_users_mes(users_bd=users_bd,
                                           text=text_for_reg_in_ls,
                                           contest=contest,
                                           reply_markup=registration_for_contest)
                self.logic_steps += 1
            # Старт конкурса
            if self.logic_steps == 1:
                if contest.time_start_contest <= cur_time:
                    self.channel_sending(text=contest.text_announcement, contest=contest, img=contest.photo_announcement)
                    self.logic_steps += 1

            # Закрытие регистрации для новых пользователей
            if self.logic_steps == 2:
                if contest.time_end_for_new_user <= cur_time:
                    # print("Конец регистрации для новых пользователей")
                    contest_users.action_new_user = False
                    self.channel_sending(text=text_for_end_reg_new_user, contest=contest)
                    self.logic_steps += 1

            # Закрытие регистрации для всех пользователей
            if self.logic_steps == 3:
                if contest.time_end_registration <= cur_time:
                    # print("Конец регистрации для всех пользователей")
                    contest_users.action_old_user = False
                    self.channel_sending(text=text_for_end_reg_old_user, contest=contest)
                    self.logic_steps += 1

            # Напомминание
            if self.time_of_last_reminder is None:
                self.time_of_last_reminder = contest.time_start_contest
            elif (cur_time - self.time_of_last_reminder) >= datetime.timedelta(minutes=contest.time_reminder):
                self.channel_sending(text=contest.text_reminder, contest=contest, img=contest.photo_reminder)

            # Поддержка
            if self.time_appear_new_leader is not None:
                if (cur_time - self.time_appear_new_leader) >= datetime.timedelta(
                        minutes=contest.time_inaction):
                    self.channel_sending(text=contest.text_encouragement,
                                         contest=contest,
                                         img=contest.photo_encouragement)

            # Парсинг
            # print("parsing")
            if contest.time_start_contest <= cur_time:
                self.parsing(contest_users, contest.contract_number, contest.time_cooldown, contest)

            # До конца конкурса остался час
            if not self.ending_an_hour:
                if (contest.time_end_contest - cur_time) <= datetime.timedelta(hours=1):
                    self.channel_sending(text="До конца конкурса остался час", contest=contest)
                    self.ending_an_hour = True
            # Конец конкурса
            if self.logic_steps == 4:
                if contest.time_end_contest <= cur_time:
                    self.channel_sending(text=contest.text_final, contest=contest, img=contest.photo_final)
                    for id in contest_users.data:
                        contest_user = contest_users.get_elem(id)
                        user = users_bd.get_elem(id)
                        user.status_contest = contest_user.status_contest
                        user.status_of_last_registration = False

                    # 20 лидеров для админа
                    if contest_users.leader:
                        self.sending_admins(admins=admin, text="Нет лидеров")
                        pass
                    else:
                        self.sending_admins(admins=admin,
                                            text=contest_users.response_for_admin(),
                                            keyboard=contest_users.keyboard_with_leaders())
                    contest_users = Contest_users()
                    save_object(users_bd, "contest_users_bd.pkl")
                    save_object(contest_users, "contest_users.pkl")
                    self.logic_steps += 1

    @staticmethod
    def sending_all_users_mes(users_bd, text, contest: Contest, reply_markup=None):
        text = text.format(time_start_contest=contest.variables_for_mes("time_start_contest"),
                           time_end_registration=contest.variables_for_mes("time_end_registration"),
                           remaining_time_contest=contest.variables_for_mes("remaining_time_contest"),
                           remaining_time_registration=contest.variables_for_mes("remaining_time_registration"),
                           wallet_leader=contest.variables_for_mes("wallet_leader"),
                           username_leader=contest.variables_for_mes("username_leader"))
        for id in users_bd.data:
            bot.send_message(chat_id=id, text=text, reply_markup=reply_markup)

    @staticmethod
    def channel_sending(text, contest: Contest, img=None, reply_markup=None):
        value = list(map(lambda i: contest_users.get_elem(i).max_buy, contest_users.leader))
        if len(value) != 0:
            max_buy = max(value)
            leader = contest_users.get_elem(contest_users.get_id_for_buy(max_buy))
        try:
            wallet_leader = leader.wallet
            username_leader = "@" + leader.username
        except:
            wallet_leader = None
            username_leader = None
        print(contest.__dict__)
        text = text.format(time_start_contest=contest.variables_for_mes("time_start_contest"),
                           time_end_contest=contest.variables_for_mes("time_end_contest"),
                           remaining_time_contest=contest.variables_for_mes("remaining_time_contest"),
                           remaining_time_registration=contest.variables_for_mes("remaining_time_registration"),
                           wallet_leader=wallet_leader,
                           username_leader=username_leader)
        if img is None:
            bot.send_message(chat_id=channel_id, text=text, reply_markup=reply_markup)
        else:
            bot.send_photo(chat_id=channel_id, photo=img, caption=text)

    @staticmethod
    def sending_admins(admins, text, keyboard=None):
        for admin in admins:
            bot.send_message(chat_id=admin, text=text, reply_markup=keyboard)

    def parsing(self, contest_users, contract, periodic_time, contest):
        try:
            link = "https://bscscan.com/token/" + contract
            service = Service("chromedriver.exe")
            options = webdriver.ChromeOptions()
            #service = Service(GeckoDriverManager().install())
            #options = FirefoxOptions()
            user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                         'Chrome/89.0.4389.86'
            options.add_argument(f"user-agent={user_agent}")
            options.add_argument('--headless')
            options.add_argument("--log-level=3")
            driver = webdriver.Chrome(service=service, options=options)
            #driver = webdriver.Firefox(service=service, options=options)
            driver.get(url=link)
            time.sleep(2)
            frame = driver.find_element(by=By.CSS_SELECTOR, value="div[class$='table-responsive'] iframe")
            href = frame.get_attribute("src").replace("&p=1", '')
            page = 1
            stop = False
            while not stop:
                driver.get(f"{href}&p={page}")
                driver.implicitly_wait(5)
                time.sleep(2)
                elements = driver.find_elements(by=By.TAG_NAME, value="div.table-responsive table tbody tr td")
                info = list()
                for i in range(len(elements)):
                    if elements[i].text != '':
                        info.append(elements[i].text)
                data = dict()
                for i in range(5, len(info), 6):
                    if len(info[i - 3].split(' ')) == 3:
                        if (int(info[i - 3].split(' ')[0]) <= periodic_time and
                            info[i - 3].split(' ')[1] in ['mins', 'min']) \
                                or info[i - 3].split(' ')[1] in ["sec", 'secs']:
                            data[float(info[i].replace(',', ''))] = {"type": info[i - 4],
                                                                     "time": info[i - 3],
                                                                     "from": info[i - 2],
                                                                     "to": info[i - 1]
                                                                     }
                if len(data) != 0:
                    key = sorted(data, reverse=True)
                    try:
                        other = {datetime.datetime.today(): data}
                        save_data(other, "info_pars.json")
                    except:
                        pass
                    list_wallet = contest_users.gat_all_wallet()
                    for buy in key:
                        if contest_user := contest_users.get_elem_for_wallet(data[buy]["from"], list_wallet):
                            if contest_users.action_new_user or contest_user.status_contest:
                                if "Swap" in data[buy]["type"]:
                                    if contest_users.new_leader(buy, data[buy]["from"]):
                                        self.time_appear_new_leader = datetime.datetime.today()
                                        self.channel_sending(text=contest.text_for_new_leader,
                                                             contest=contest,
                                                             img=contest.photo_for_new_leader)
                                        contest_user.max_buy = buy
                                    contest_user.buy += buy
                                elif "Transfer" in data[buy]["type"]:
                                    contest_user.sell += buy
                    page += 1

                else:
                    stop = True
            driver.close()
            driver.quit()
        except Exception as ex:
            bot.send_message(chat_id=754513655,
                             text="ERRROR\n" + str(ex))
        print("finish")


class Process_for_contest:
    p0 = Process(target=start_contest, args=())

    def start_process(self):
        self.p0 = Process(target=start_contest)
        self.p0.start()

    def stop_process(self):
        self.p0.terminate()


contest_users = Contest_users()
contest = Contest()
users_bd = Users()
contest_proc = Process_for_contest()
test_win = ['6453728', '6453865', '6454002', '6454139', '6454276', '6454413', '6454550', '6454687', '6454824',
            '6454961', '6455098', '6455235', '6455372', '6455509', '6455646', '6455783', '6455920', '6456057',
            '6456194', '6456331']

bot = telebot.TeleBot(API_TOKEN)
bot.delete_webhook()
data_text_for_create_contest = {1: 'введите номер контракта',
                                2: 'введите начало конкурса(ДД.ММ.ГГ ЧЧ)',
                                3: 'введите конец конкурса(ДД.ММ.ГГ ЧЧ)',
                                4: 'введите за сколько до начала конкурса открывается регистрация(в минутах)',
                                5: 'введите за сколько до окончания конкурса закрывается регистрация(в минутах)',
                                6: 'введите за сколько до окончания конкурса '
                                   'новые участники не смогут попасть в конкурс (в минутах)',
                                7: 'TIME_INACTION',
                                8: 'через сколько минут напоминать о том, что идет конкурс?(в минутах)',
                                9: 'введите кулдаун(в минутах)'}


def test_res():
    response = ''
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for i in range(6453728, 6453728 + 137 * 20, 137):
        user_id = i
        username = None
        wallet = '0x' + str(i * 2)
        sell = i // 2
        buy = int(i * 1.5)
        max_buy = int(i * 0.7)
        response += f"user_id: {user_id}\nuser_name: {username}\nКошелёк: {wallet}\n" \
                    f"Продано: {sell}\nКуплено: {buy}\nМаксимальная покупка: {max_buy}\n\n"
        keyboard.add(types.InlineKeyboardButton(text=user_id, callback_data=user_id))

    bot.send_message(chat_id=5191469996,
                     text=response,
                     reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.from_user.id in users_bd.data and not users_bd.get_status(
    message.from_user.id))
def other(message):
    global users_bd
    user_id = message.from_user.id
    bot.send_message(chat_id=user_id,
                     text=text_for_ban_user)
    save_object(contest, "contest.pkl")


@bot.message_handler(commands=['end_cont'])
def ll(message):
    test_res()


@bot.callback_query_handler(func=lambda call: call.data in test_win)
def end(call):
    bot.send_message(chat_id=channel_id,
                     text=f"{text_for_winner} {call.data} {None} Максимальная покупка: {int(int(call.data) * 0.7)}")


@bot.message_handler(commands=["start"])
def start(message):
    global users_bd
    user_id = message.from_user.id
    if str(user_id) in contest.stop_list:
        users_bd.set_status(user_id)
        bot.send_message(chat_id=user_id,
                         text=text_for_ban_user)
        save_object(contest, "contest.pkl")

    if user_id not in users_bd.data:
        users_bd += user_id
        r = bot.send_message(chat_id=user_id,
                             text=text_for_start)
        users_bd.set_message_id(user_id, r.id)
        save_object(users_bd, "users_bd.pkl")
    elif user_id in users_bd.data:
        r = bot.send_message(chat_id=user_id,
                             text=text_for_start)
        users_bd.set_message_id(user_id, r.id)
        save_object(users_bd, "users_bd.pkl")


@bot.message_handler(commands=["admin"], func=lambda message: message.from_user.id in admin)
def command_admin(message):
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
    users_bd.set_flag(user_id, 10)
    users_bd.set_message_id(user_id, r.id)


@bot.message_handler(func=lambda message: (users_bd.get_flag(message.from_user.id) == 10))
def reg_wallet(message):
    global users_bd, contest, contest_users
    user_id = message.from_user.id
    if str(user_id) in contest.stop_list or message.text in contest.stop_list:
        users_bd.set_status(user_id, False)
        bot.send_message(chat_id=user_id,
                         text=text_for_ban_user)
        save_object(contest, "contest.pkl")

    elif not users_bd.get_status_of_last_registration(user_id): #зарегистрирован ли пользователь (если не зарегистрирован)
        if contest_users.action_old_user: # Можно ли страрым регистрироваться
            user = users_bd.get_elem(user_id)
            print(users_bd)
            if not user.status_contest and not contest_users.action_new_user: # если новый и закрыта регистрация для новых
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Извините, но для Вас регистрация уже закрыта!")
            else:
                user.wallet = message.text
                user.status_of_last_registration = True
                contest_users += user_id
                contest_user = contest_users.get_elem(user_id)
                contest_user.wallet = message.text
                with open("wallet.txt", "a+") as f:
                    f.write(f"{contest_user.wallet}\n")
                contest_user.username = message.from_user.username
                contest_user.status_contest = user.status_contest
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Вы успешно зарегистрированы!")
                save_object(contest_users, "contest_users.pkl")
        else:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text="Извините, но регистрация на конкурс уже закрыта!")

        users_bd.set_flag(user_id, 0)
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        save_object(users_bd, "users_bd.pkl")


@bot.callback_query_handler(func=lambda call: call.data == "registration_for_contest")
def call_reg(call):
    global users_bd
    user_id = call.from_user.id
    # print(users_bd.get_status_of_last_registration(user_id))
    if str(user_id) in contest.stop_list:
        users_bd.set_status(user_id, False)
        bot.send_message(chat_id=user_id,
                         text="Ваш профиль заблокирован в нашем сервисе")
        save_object(contest, "contest.pkl")

    if not users_bd.get_status_of_last_registration(user_id):
        users_bd.set_message_id(user_id, call.message.message_id)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text="Введите номер кошелька")
        users_bd.set_flag(user_id, 10)


@bot.message_handler(content_types=["text", "photo", "document"],
                     func=lambda message: (message.from_user.id in admin) and
                                          (users_bd.get_flag(message.from_user.id) != 10))
def work__admin(message):
    global users_bd, contest
    user_id = message.from_user.id
    flag = users_bd.get_flag(user_id)

    if flag in [12, 13, 14, 15, 16]:
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
            if flag == 12:
                contest.text_final = message.text

            elif flag == 13:
                contest.text_announcement = message.text

            elif flag == 14:
                contest.text_for_new_leader = message.text

            elif flag == 15:
                contest.text_final = message.text

            elif flag == 16:
                contest.text_reminder = message.text

        else:
            if flag == 12:
                contest.photo_final = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_final,
                               caption=contest.text_final,
                               reply_markup=complete_or_change_new_text2)
            elif flag == 13:
                contest.photo_announcement = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_announcement,
                               caption=contest.text_announcement,
                               reply_markup=complete_or_change_new_text2)

            elif flag == 14:
                contest.photo_for_new_leader = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_for_new_leader,
                               caption=contest.text_for_new_leader,
                               reply_markup=complete_or_change_new_text2)

            elif flag == 15:
                contest.photo_encouragement = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_encouragement,
                               caption=contest.text_encouragement,
                               reply_markup=complete_or_change_new_text2)

            elif flag == 16:
                contest.photo_reminder = bot.download_file(
                    bot.get_file(message.photo[len(message.photo) - 1].file_id).file_path
                )
                bot.send_photo(chat_id=user_id,
                               photo=contest.photo_reminder,
                               caption=contest.text_reminder,
                               reply_markup=complete_or_change_new_text2)

    elif flag in [1, 2, 3, 4, 5, 6, 7, 8, 9]:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"Вы ввели: \n{message.text}",
                              reply_markup=complete_or_change_contest)

    elif flag == 11:
        bot.delete_message(chat_id=user_id,
                           message_id=message.id)
        check = True
        if message.text.isdigit():
            if int(message.text) in users_bd.data:
                users_bd.set_status(int(message.text), False)
                # print(111111111111111)
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

                    break

        elif check:
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=f"пользователь/кошелек - {message.text} не найден. Добавить в стоп лист?",
                                  reply_markup=action_stop_list)

    elif flag == 18:
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


@bot.callback_query_handler(func=lambda call: call.from_user.id in admin and users_bd.get_flag(call.from_user.id) != 10)
def work_admin(call):
    global contest, data_text_for_create_contest
    user_id = call.from_user.id
    flag = users_bd.get_flag(user_id)
    if call.data == "add_contest":
        users_bd.set_flag(user_id, 1)
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=data_text_for_create_contest[users_bd.get_flag(user_id)],
                              reply_markup=back_in_admin_panel)

    elif call.data == "complete_value_contest":
        ###check maximum flag
        print(users_bd.get_flag(user_id))
        new_set = call.message.text.split('\n')[1]
        if flag == 1:
            contest.contract_number = new_set
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                  reply_markup=back_keyboard_in_creating_contest)
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
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                          reply_markup=back_keyboard_in_creating_contest)
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
                                              text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                              reply_markup=back_keyboard_in_creating_contest)
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
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                          reply_markup=back_keyboard_in_creating_contest)
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
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                          reply_markup=back_keyboard_in_creating_contest)
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
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                          reply_markup=back_keyboard_in_creating_contest)
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
                                          text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                          reply_markup=back_keyboard_in_creating_contest)
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
                #try:
                contest.time_reminder = int(new_set)
                bot.edit_message_text(chat_id=user_id,
                                        message_id=users_bd.get_message_id(user_id),
                                        text=data_text_for_create_contest[users_bd.get_flag(user_id) + 1],
                                        reply_markup=back_keyboard_in_creating_contest)
                users_bd.set_flag(user_id, flag + 1)

                #except Exception as ex:
                #bot.answer_callback_query(callback_query_id=call.id,
                #                            text=str(ex),
                #                            show_alert=True)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")
        elif flag == 9:
            if new_set.isdigit():
                contest.time_cooldown = int(new_set)
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
                                           f"кулдаун: {contest.time_cooldown}минут(а)"
                                           f"текст Вы можете изменить в админ панель -> изменить текста")
                save_object(contest, "contest.pkl")
                if contest_proc.p0.is_alive():
                    contest_proc.stop_process()
                contest_proc.start_process()
                users_bd.set_flag(user_id, 0)
            else:
                bot.edit_message_text(chat_id=user_id,
                                      message_id=users_bd.get_message_id(user_id),
                                      text="Скорее всего Вы написали не в правильном формате. Попробуйте ещё раз")

    elif call.data == "change_introduced_value_contest":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=data_text_for_create_contest[users_bd.get_flag(user_id)])

    elif call.data == "previous_lvl_in_creating_contest":
        if flag == 1:
            users_bd.set_flag(user_id, flag - 1)
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text="Выберите действие",
                                  reply_markup=admin_start)
        else:
            users_bd.set_flag(user_id, flag - 1)
            bot.edit_message_text(chat_id=user_id,
                                  message_id=users_bd.get_message_id(user_id),
                                  text=data_text_for_create_contest[users_bd.get_flag(user_id)],
                                  reply_markup=back_keyboard_in_creating_contest)

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
        users_bd.set_flag(user_id, 13)

    elif call.data == "change_final":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_final}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 12)

    elif call.data == "change_status_return":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_for_new_leader}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 14)

    elif call.data == "change_support":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_encouragement}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 15)

    elif call.data == "change_reminder":
        bot.edit_message_text(chat_id=user_id,
                              message_id=users_bd.get_message_id(user_id),
                              text=f"введите новый текст. \n"
                                   f"установленное значение на данные момент: `{contest.text_reminder}`",
                              reply_markup=back_in_change_text,
                              parse_mode="Markdown")
        users_bd.set_flag(user_id, 16)

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
        users_bd.set_flag(user_id, 11)

    elif call.data == "present_context":
        if contest_proc.p0.is_alive():
            bot.send_message(chat_id=call.from_user.id,
                             text=contest.presenting(),
                             reply_markup=back_in_admin_panel)
        else:
            bot.answer_callback_query(callback_query_id=call.id,
                                      text="Конкурс неактивен",
                                      show_alert=True)

    elif call.data == "unblock_user":
        id_wallet = ''
        data = users_bd.data
        for i in data:
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
            users_bd.set_flag(user_id, 18)

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

    # elif datetime.today >= contest.time_end_contest:
    # leaders = load_object("leaders.pkl")
    # if call.data in leaders.data:
    #    bot.send_message(chat_id=channel_id, text=f"Победил юзер: {users_bd.get_wallet(call.data)}")


@bot.callback_query_handler(func=lambda call: call.data in users_bd)
def end_contest(call):
    global users_bd
    winner = users_bd.get_elem(call.data)
    bot.send_message(chat_id=channel_id,
                     text=f"{text_for_winner} {winner.username}")


if __name__ == "__main__":
    print("START")

    if contest_proc.p0.is_alive():
        contest_proc.stop_process()
    contest.time_start_registration = datetime.datetime(year=int(2022),
                                                        month=int(7),
                                                        day=int(22),
                                                        hour=int(13),
                                                        minute=00)

    contest.time_start_contest = datetime.datetime(year=int(2022),
                                                   month=int(7),
                                                   day=int(22),
                                                   hour=int(14),
                                                   minute=00)

    contest.time_end_for_new_user = datetime.datetime(year=int(2022),
                                                      month=int(7),
                                                      day=int(22),
                                                      hour=int(14),
                                                      minute=30)

    contest.time_end_registration = datetime.datetime(year=int(2022),
                                                      month=int(7),
                                                      day=int(22),
                                                      hour=int(14),
                                                      minute=50)

    contest.time_end_contest = datetime.datetime(year=int(2022),
                                                 month=int(7),
                                                 day=int(22),
                                                 hour=int(15),
                                                 minute=00)
    contest.text_for_new_leader = "появился новый лидер {username_leader}"
    contest.text_final = "Конкурс окончен"
    contest.time_cooldown = 5
    contest.time_reminder = 15
    contest.time_inaction = 20
    contest.text_reminder = "конец конкурса {time_end_contest}"
    contest.text_announcement = "оставшееся время регистрации {remaining_time_registration}"
    contest.contract_number = "0x10f6f2b97f3ab29583d9d38babf2994df7220c21"
    save_object(contest, 'contest.pkl')
    #contest_proc.start_process()
    #contest_users = Contest_users()
    #save_object(contest_users, "contest_users.pkl")
    bot.infinity_polling()