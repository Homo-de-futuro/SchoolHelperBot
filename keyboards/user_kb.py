from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

unlogged = InlineKeyboardMarkup(resize_keyboard=True)
unlogged.add(InlineKeyboardButton('Войти', callback_data='sign_in'))


# Main menu
logged_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
hw_menu_btn = InlineKeyboardButton('Домашнее задание', callback_data='hw_menu_btn')
marks_menu_btn = InlineKeyboardButton('Оцекни', callback_data='marks_menu_btn')
set_menu_btn = InlineKeyboardButton('Настройки', callback_data='set_menu_btn')
logout_btn = InlineKeyboardButton('Выйти', callback_data='logout_btn')
logged_keyboard.add(hw_menu_btn, marks_menu_btn).row(set_menu_btn).row(logout_btn)


# Homework menu
hw_menu_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
hw_get_next_day_btn  = InlineKeyboardButton('На завтра', callback_data='hw_get_next_day_btn')
hw_get_by_date_btn = InlineKeyboardButton('По дате', callback_data='hw_get_by_date_btn')
hw_go_back_btn  = InlineKeyboardButton('Назад', callback_data='hw_go_back_btn')
# hw_menu.row(hw_next_day).row(hw_date).row(hw_week)
hw_menu_keyboard.row(hw_get_next_day_btn).row(hw_get_by_date_btn).row(hw_go_back_btn)

# hw_cancel_menu = ReplyKeyboardMarkup(resize_keyboard=True)
# hw_cancel_menu.row(KeyboardButton('Отмена'))


#Marks menu 
marks_menu_keyboard = InlineKeyboardMarkup()
marks_get_next_day_btn = InlineKeyboardButton('Полученные сегодня', callback_data='marks_get_next_day_btn')
marks_get_week_btn = InlineKeyboardButton('Полученные на этой неделе', callback_data='marks_get_week_btn')
marks_get_suject_btn = InlineKeyboardButton('По конкретному предмету', callback_data='marks_get_suject_btn')
marks_go_back_btn = InlineKeyboardButton('Назад', callback_data='marks_go_back_btn')
marks_menu_keyboard.row(marks_get_next_day_btn).row(marks_get_week_btn).row(marks_get_suject_btn).row(marks_go_back_btn)

exit = ReplyKeyboardMarkup(resize_keyboard=True)
exit_button = KeyboardButton('/отмена')
exit.row(exit_button)



