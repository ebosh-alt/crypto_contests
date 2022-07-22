import datetime
from telebot import types
# from main import bot
from config import *





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
        self.time_cooldown = None
        self.stop_list = []

    def variables_for_mes(self, value):
        match value:
            case "time_start_contest":
                return self.time_start_contest
            case "time_end_contest":
                return self.time_end_contest
            case "remaining_time_contest":
                return str(self.time_end_contest - datetime.datetime.now()).split('.')[0]
            case "remaining_time_registration":
                return str(self.time_end_registration - datetime.datetime.now()).split('.')[0]
            case "wallet_leader":
                return self.wallet_leader
            case "username_leader":
                return self.username_leader

    def presenting(self) -> str:
        text = f"Конкурс выглядит так:\n" \
               f"номер контракта: {self.contract_number}\n" \
               f"начало конкурса: {self.time_start_contest}\n" \
               f"конец конкурса: {self.time_end_contest}\n" \
               f"время открытия регистрации: {self.time_start_registration}\n" \
               f"время закрытии регистрации: {self.time_end_registration}\n" \
               f"время закрытия конкурса от новых участников: " \
               f"{self.time_end_for_new_user}\n" \
               f"время бездействия для отправки уведомления: " \
               f"{self.time_inaction} минут(а)\n" \
               f"периодичность напоминания о конкурсе: " \
               f"{self.time_reminder} минут(а)\n" \
               f"текст анонса: {self.text_announcement}\n" \
               f"текст финала: {self.text_final}\n" \
               f"текст отдачи статуса: {self.text_for_new_leader}\n" \
               f"текст поддержки: {self.text_encouragement}\n" \
               f"текст напоминания: {self.text_reminder}\n" \
               f"текст Вы можете изменить в админ панель -> изменить текста"
        return text


class User:
    def __init__(self) -> None:
        self.flag = 0
        self.wallet = ""
        self.status_of_last_registration = False
        self.message_id = 0
        self.status = True
        self.username = ""
        self.status_contest = False


class Contest_user:
    def __init__(self) -> None:
        self.wallet = ""
        self.username = ""
        self.status_contest = False
        self.buy = 0
        self.max_buy = 0
        self.sell = 0


###Класс нереляционной бд
class nsql_database:
    def __init__(self) -> None:
        self.data = {}

    # Получение значения по ключу
    def get_elem(self, key: int | str) -> User | Contest_user | bool:
        if key in self.data:
            return self.data[key]
        else:
            return False


class Contest_users(nsql_database):
    def __init__(self) -> None:
        super().__init__()
        self.action_new_user = True
        self.action_old_user = True
        self.leader = []

    def __contains__(self, other) -> bool:
        if other in self.data:
            return True
        else:
            return False

    def __add_user(self, id) -> None:
        self.data[id] = Contest_user()
        return self

    def __add__(self, id: int):
        return self.__add_user(id)

    def __iadd__(self, id: int) -> None:
        return self.__add_user(id)

    def del_elem(self, id: int) -> bool:
        if id in self.data:
            del self.data[id]
            return True
        else:
            return False

    def gat_all_wallet(self):
        res = []
        for i in self.data:
            res.append(self.data[i].wallet)
        return res

    def get_id_for_wallet(self, wallet: str) -> int:
        for i in self.data:
            obj_user = self.get_elem(i)
            if wallet == obj_user.wallet:
                return i

    def get_elem_for_wallet(self, wallet: str, list_wallet: list) -> Contest_user | bool:
        for i in self.data:
            obj_user = self.get_elem(i)
            if wallet == obj_user.wallet and wallet in list_wallet:
                return obj_user
        else:
            return False

    def get_id_for_buy(self, buy: float) -> int:
        for i in self.data:
            obj_user = self.get_elem(i)
            if buy == obj_user.max_buy:
                return i

    def new_leader(self, buy: float, wallet: str) -> bool:
        value = list(map(lambda i: self.get_elem(i).max_buy, self.leader))
        if len(value) >= 20:
            if min(value) < buy:
                self.leader[self.get_id_for_buy(min(value))] = self.get_id_for_wallet(wallet)
            if max(value) < buy:
                return True
            else:
                return False
        else:
            self.leader.append(self.get_id_for_wallet(wallet))
            return True

    def response_for_admin(self):
        response = "Список лидеров:\n"
        for id in self.leader:
            user = self.get_elem(id)
            response += f"user_id: {id}\nuser_name: {user.username}\nКошелёк: {user.wallet}\n" \
                        f"Продано: {user.sell}\nКуплено: {user.buy}\nМаксимальная покупка: {user.max_buy}\n\n"
        return response

    def keyboard_with_leaders(self):
        keyboard = types.InlineKeyboardMarkup()
        for id in self.leader:
            keyboard.add(types.InlineKeyboardButton(text=id, callback_data=id))
        return keyboard


class Users(nsql_database):
    count_user = 0

    def __init__(self) -> None:
        super().__init__()

    def __add__(self, id):
        self.data[id] = User()
        Users.count_user += 1
        return self

    def __contains__(self, other) -> bool:
        if other in self.data:
            return True
        else:
            return False

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

    def gat_all_wallet(self):
        res = []
        for i in self.data:
            res.append(self.data[i].wallet)
        return res


class Leader:
    def __init__(self, wallet, sell, buy, total_amount):
        self.wallet = wallet
        self.sell = sell
        self.buy = buy
        self.total_amount = total_amount



