from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from SETTINGS import *
from run_bot import dp, bot
from keyboards import user_kb
from parse import parse
from SQL import db_user


#Нажатие на кнопку вызова меню с оценками
@dp.callback_query_handler(text='marks_menu_btn')
async def marks_menu(callback: types.CallbackQuery):
    await callback.answer('')
    await callback.message.edit_text(text=MARKS_MENU_TEXT, reply_markup=user_kb.marks_menu_keyboard)


#Кнопка назад
@dp.callback_query_handler(text='marks_go_back_btn')
async def marks_go_back_btn(callback: types.CallbackQuery):
    await callback.message.edit_text(text=MAIN_MENU_TEXT, reply_markup=user_kb.logged_keyboard)


#Оценки за сегодняшний день
@dp.callback_query_handler(text='marks_get_next_day_btn')
async def marks_get_next_day_btn(callback: types.CallbackQuery):
    await callback.answer('Это займет около 10 секунд', show_alert=True)

    user_data = db_user.sql_get_auth_data(callback.from_user.id)
    marks_list = parse.get_today_marks(user_data['login'], user_data['password'])
    
    if marks_list == 'no_homework_today':
        await callback.message.answer('Сегодня вы еще не получили ни одной оценки')
    elif marks_list is not None:
        #Формируем сообщение
        mes = ''
        for subj in marks_list:
            mes += '<b>' + subj + '</b>' + ': ' + marks_list[subj] + '\n'

        await callback.message.answer(f'''<b>Оценки за сегодняший день:</b>

{mes}''')

        #Переносим меню
        await callback.message.answer(text=MARKS_MENU_TEXT, reply_markup=user_kb.marks_menu_keyboard)
        await callback.message.delete()
    else:
        await callback.message.answer('Возникла неизвестная ошибка')



#Оценки за неделю
@dp.callback_query_handler(text='marks_get_week_btn')
async def marks_get_week_btn(callback:types.CallbackQuery):
    await callback.answer('Подождите, это займет приблизительно 10 секунд...', show_alert=True)

    user_data = db_user.sql_get_auth_data(callback.from_user.id)
    res = parse.get_week_marks(user_data['login'], user_data['password'])

    finally_message = '''<b><i>Оценки на этой неделе:</i></b>
    
'''

    for day in res:
        day_marks = res[day]     
        day_message = ''

        for subject in day_marks:
            day_message += '<b>' + subject + '</b>' + ': ' + day_marks[subject] + '\n'

        finally_message += f'''<b>{day}</b>:
{day_message}        

'''

    await callback.message.answer(finally_message)
    await callback.message.delete()
    await callback.message.answer(MARKS_MENU_TEXT, reply_markup=user_kb.marks_menu_keyboard)



