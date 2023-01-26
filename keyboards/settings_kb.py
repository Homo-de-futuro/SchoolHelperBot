from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup


#Settings 
settings_menu = InlineKeyboardMarkup(resize_keyboard=True)
hw_settings_btn = InlineKeyboardButton('⚙️ Домашние задания', callback_data='hw_settings_btn')
marks_settings_btn = InlineKeyboardButton('🔔 Оценки', callback_data='marks_settings_btn')
pass_settings_btn = InlineKeyboardButton('🔔 Пропуски', callback_data='pass_settings_btn')
settings_back_btn = InlineKeyboardButton('Назад', callback_data='settings_back_btn')

settings_menu.row(hw_settings_btn).row(marks_settings_btn).row(pass_settings_btn).row(settings_back_btn)


#Клавиатура, если оповещения включены
hw_settings_menu_alerts_on = InlineKeyboardMarkup()
hw_time_settings_btn = InlineKeyboardButton('⏰Настроить время автоматических опопвещений', callback_data='hw_time_settings_btn')
hw_alerts_off_btn = InlineKeyboardButton('🔔Выключить оповещения', callback_data='hw_alerts_off_btn')
hw_settings_back_btn = InlineKeyboardButton('Назад', callback_data='hw_settings_back_btn')

hw_settings_menu_alerts_on.row(hw_time_settings_btn).row(hw_alerts_off_btn).row(hw_settings_back_btn)


#Клавиатура, если оповещения выключены
hw_settings_menu_alerts_off = InlineKeyboardMarkup()
# hw_time_settings1_btn = InlineKeyboardButton('⏰Настроить время автоматических опопвещений', callback_data='hw_time_settings1_btn')
hw_alerts_on_btn = InlineKeyboardButton('🔔Включить оповещения', callback_data='hw_alerts_on_btn')
# hw_settings_back1_btn = InlineKeyboardButton('Назад', callback_data='hw_settings_back_btn')

hw_settings_menu_alerts_off.row(hw_time_settings_btn).row(hw_alerts_on_btn).row(hw_settings_back_btn)

