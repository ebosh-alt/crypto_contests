from telebot import types

admin_start = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="создать конкурс", callback_data="add_contest"),
    types.InlineKeyboardButton(text="забанить пользователя", callback_data="block_user"),
    types.InlineKeyboardButton(text="разблокировать пользователя", callback_data="unblock_user"),
    types.InlineKeyboardButton(text="изменить текста", callback_data="change_text"))

admin_change_text = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="изменить анонс", callback_data="change_announcement"),
    types.InlineKeyboardButton(text="изменить финал", callback_data="change_final"),
    types.InlineKeyboardButton(text="изменить текст отдачи статуса", callback_data="change_status_return"),
    types.InlineKeyboardButton(text="изменить текст поддержки", callback_data="change_support"),
    types.InlineKeyboardButton(text="изменить текст напоминания", callback_data="change_reminder"),
    types.InlineKeyboardButton(text="назад", callback_data="back_in_admin_panel")
)

back_in_admin_panel = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="back_in_admin_panel")
)

back_in_change_text = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="назад", callback_data="change_text")
)

complete_or_change_new_text = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="добавить фото", callback_data="add_photo"),
    types.InlineKeyboardButton(text="подтвердить", callback_data="complete_new_text"),
    types.InlineKeyboardButton(text="изменить", callback_data="change_introduced_text")
)

complete_or_change_new_text2 = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="complete_new_text"),
    types.InlineKeyboardButton(text="изменить", callback_data="change_introduced_text")
)

complete_or_change_contest = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="подтвердить", callback_data="complete_value_contest"),
    types.InlineKeyboardButton(text="изменить", callback_data="change_introduced_value_contest")
)

registration_for_contest = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="Зарегистрироваться", callback_data="registration_for_contest")
)

action_stop_list = types.InlineKeyboardMarkup(row_width=1).add(
    types.InlineKeyboardButton(text="да", callback_data="yes_stop_list"),
    types.InlineKeyboardButton(text="нет", callback_data="back_in_admin_panel")
)
