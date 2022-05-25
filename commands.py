from config import bot, contest, start_text, save_object, admin, users_bd
from keyboard import *


@bot.message_handler(commands=["start"])
def start(message):
    global users_bd
    user_id = message.from_user.id
    print(user_id)
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
    global users_bd
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
