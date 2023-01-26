from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from run_bot import dp, Bot
from keyboards import user_kb
from parse import parse
from SQL import db_user, db_bot
from SETTINGS import *

from handlers.homework import *
from handlers.settings import *
from handlers.marks import *


class SigInFSM(StatesGroup):
    login = State()
    password = State()


@dp.message_handler(commands=['start',])
async def send_welcome(message:types.Message):
    WELCOME_TEXT = '''<b><i>Привет!</i></b>

<b>Что может этот бот?</b>
    • Опевещение о пропусках/прогулах, полученных оценках
    • Выдача домашних задачний за определенную дату
    • Оценки по выбранному предмету
    • Отправка оценок по кнопке


<b>Вы также можете настроить:</b>
    • Время, когда будет приходить оповещение о домашнем задании
    • Оповещения, т.е. выключить их или включить

'''
    
    if db_user.sql_is_user_exist(message.from_user.id):     
        await message.answer(MAIN_MENU_TEXT, reply_markup=user_kb.logged_keyboard)

        if not(scheduler.get_job('hw_scheduler')):
            #Проверяем, существуют ли планировщики, если нет, то запускаем его
            time = db_bot.sql_get_hw_sheduler_time(message.from_user.id)
            time = time.split(':')
            scheduler.add_job(get_homework_by_scheduler, 'cron', hour=time[0], minute=time[1], id='hw_scheduler', args=[message.chat.id, message.from_user.id])

            
            print('---Scheduler has been added')
         
        if not(scheduler.get_job('meks_schedluer')):
            #Если еще нет, то запускаем проверку обновления оценок с помощью планироващика каждые 10 секунд.
            scheduler.add_job(check_marks_updating, 'interval', minutes=10, args=[message.chat.id, message.from_user.id])
    else:
        await message.answer(WELCOME_TEXT, reply_markup=user_kb.unlogged)


@dp.message_handler(commands=['help',])
async def send_help(message:types.Message):
    WELCOME_TEXT = '''
<b>Что может этот бот?</b>
    • Опевещение о пропусках/прогулах, полученных оценках
    • Выдача домашних задачний за определенную дату
    • Отправка оценок нажатием кнопки


<b>Вы также можете настроить:</b>
    • Время, когда будет приходить оповещение о домашнем задании
    • Отключение оповещений

'''
    await message.answer(WELCOME_TEXT)


# --------------- SIGN_IN ---------------
# Регистрация пользователя.
@dp.callback_query_handler(text='sign_in')
async def sign_in(callback: types.CallbackQuery):
    if db_user.sql_is_user_exist(callback.from_user.id):
        await callback.answer('Вы уже вошли в систему', show_alert=True)
        await callback.message.delete()     
    else:
        await callback.answer(' ')
        await callback.message.answer('Хорошо, теперь вам необходмо ввести свой номер телефона')
        await SigInFSM.login.set()

    
@dp.message_handler(state=SigInFSM.login)
async def sing_in_login(message: types.Message, state: FSMContext):
    await state.update_data(login=message.text)
    await message.answer("Теперь введите пароль")
    await SigInFSM.next()


@dp.message_handler(state=SigInFSM.password)
async def sign_in_password(message: types.Message, state:FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    wait_message = await message.answer('Подождите немного (это может занять до 15 секунд)...')

    user_account_check = parse.is_account_exist_gos(data['login'], data['password'])

    if user_account_check:     
        if db_user.sql_add_new_user(message.from_user.id, data['login'], data['password']):
            await bot.delete_message(message.from_user.id, wait_message['message_id'])
            await message.answer(MAIN_MENU_TEXT, reply_markup=user_kb.logged_keyboard)
            
            #После успешного входа пользователя добавляем планировщик, который будет автоматически отправлять ему домашнее задание, оценки, пропуски
            scheduler.add_job(get_homework_by_scheduler, 'cron', hour='15', id='hw_scheduler', args=[message.chat.id, message.from_user.id])
            scheduler.add_job(check_marks_updating, 'interval', minutes=10, args=[message.chat.id, message.from_user.id])
        else:
            await message.answer('Вы уже вошли в систему! Если вы хотите добавть другой аккаунт, в настройках выберите пунт "удалить привязку"')
                
    else:
        await message.answer('Неверный логин или пароль. Проверьте регистр и правильность написания')
    await state.finish()

    # elif data['login_type'] == 'standart':
    #     user_account_check = parse.is_account_exist_standart(data['login'], data['password'])

    #     if user_account_check:     
    #         if db_user.sql_add_new_user(message.from_user.id, data['login'], data['password'], data['login_type']):
    #             await message.answer(MAIN_MENU_TEXT, reply_markup=user_kb.logged)
    #         else:
    #             await message.answer('Вы уже вошли в систему! Если вы хотите добавть другой аккаунт, в настройках выберите пунт "удалить привязку"')
                
    #     else:
    #         await message.answer('Неверный логин, пароль, или выбранный тип входа. Проверьте регистр и правильность написания')



