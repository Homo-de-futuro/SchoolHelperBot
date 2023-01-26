from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from run_bot import dp, bot
from keyboards import user_kb
from parse import parse
from SQL import db_user

from SETTINGS import *

import datetime



class HWByDateFSM(StatesGroup):
    date = State()




def make_homework_message(hw_list):
    hw_message = ''

    for subject in hw_list:
        hw_message += '• ' + '<b>' + subject + '</b>' + ' - ' + hw_list[subject] + '\n'
    
    return hw_message


#Нажатие на кнопку вызова меню домашнего задания
@dp.callback_query_handler(text='hw_menu_btn')
async def hw_settings(callback: types.CallbackQuery):
    await callback.answer(' ')
    await callback.message.edit_text(text=HOMEWORK_MENU_TEXT, reply_markup=user_kb.hw_menu_keyboard)
    


@dp.callback_query_handler(text='hw_get_next_day_btn') 
async def hw_back(callback: types.CallbackQuery):
    await callback.answer('Это займет приблезительно 10 секунд', show_alert=True)
    data = db_user.sql_get_auth_data(callback.from_user.id)
    try:
        parse_res = parse.get_next_homework(data['login'], data['password'])
        print('start next part')
        day_of_week = parse_res[1]
        hw_list = parse_res[0]

        mess = make_homework_message(hw_list)

        await callback.message.answer(f'''
        <b>Домашнее задание на {day_of_week}</b>
        
{mess}
    ''')
        await callback.message.answer(text=HOMEWORK_MENU_TEXT, reply_markup=user_kb.hw_menu_keyboard)
        await callback.message.delete()
    except:
        await callback.message.answer('Возникла неизвестная ошибка')



# --------------- HW BY DATE ---------------
@dp.callback_query_handler(text='hw_get_by_date_btn')
async def hw_by_date(callback: types.CallbackQuery):
    global menu_message_id

    menu_message_id = callback.message.message_id
    await callback.message.answer('''Хорошо, теперь введите дату в формате: 
    
ДЕНЬ[пробел]МЕСЯЦ[пробел]ГОД

<i>Пример: 4 3 2023</i>''', reply_markup=user_kb.exit)
    await HWByDateFSM.date.set()


# @dp.message_handler(Text(equals='отмена', ignore_case=True),state=HWByDateFSM.date)
# async def cancel(message:types.Message, state:FSMContext):
#     await bot.delete_message(message.chat.id, menu_message_id)
#     await message.answer(HOMEWORK_MENU_TEXT, reply_markup=user_kb.hw_menu_keyboard)


@dp.message_handler(state=HWByDateFSM.date)
async def check_date(message:types.Message, state:FSMContext):
    ERROR_MESSAGE = '''<b>Неверный ввод</b>, введите дату в формате:

<b>ДЕНЬ[пробел]МЕСЯЦ[пробел]ГОД</b>

<i>Пример: 4 3 2023</i>'''

    input = message.text.split(' ')

    if len(input) == 3:
        try:
            await message.answer('Подождите около 10 секунд, собираем ифнормацию...', reply_markup=ReplyKeyboardRemove())
            date = datetime.date(int(input[2]), int(input[1]), int(input[0]))
            auth_data = db_user.sql_get_auth_data(message.from_user.id)
            hw_result = parse.get_homework_by_date(auth_data['login'], auth_data['password'], date)

            if hw_result == 'WEEKEND':
                await message.answer('На этот день не было задано домашнее задание')
            elif hw_result == 'YEAR':
                await message.answer('Вы можете получить домашнюю работу только за <b>текущий учебный год</b>!')
            else:
                day_of_week = hw_result[1]
                hw_list = hw_result[0]
                mess = make_homework_message(hw_list)
                
                await message.answer(f'''
<b>Домашнее задание на {input[0]+'.'+input[1]+'.'+input[2]} ({day_of_week})</b>
    
{mess}
''')            
                # Переносим меню вниз страницы, удаляя старое и создавая новое вначале.
                await bot.delete_message(message.from_user.id, menu_message_id)
                await message.answer(text=HOMEWORK_MENU_TEXT, reply_markup=user_kb.hw_menu_keyboard)
                await state.finish()
        except Exception as ex:
            await message.answer('Неправильный формат даты, попробуйте еще раз')
            
            print(ex)

    else:
        await message.answer(ERROR_MESSAGE)

    
@dp.callback_query_handler(text='hw_go_back_btn')
async def hw_back(callback: types.CallbackQuery):
    await callback.answer(' ')
    await callback.message.edit_text(text=MAIN_MENU_TEXT, reply_markup=user_kb.logged_keyboard)
    

@dp.message_handler(commands=['отмена'], state=HWByDateFSM.date)
async def exit(message:types.Message, state:FSMContext):
    await message.answer('Как скажете', reply_markup=ReplyKeyboardRemove())
    await bot.delete_message(message.chat.id, menu_message_id)
    await message.answer(text="📚 <b>Домашние задания</b>", reply_markup=user_kb.hw_menu_keyboard)
    await state.finish()


