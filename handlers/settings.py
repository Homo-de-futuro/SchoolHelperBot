from aiogram import types
from aiogram.types import ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from run_bot import dp, bot, scheduler
from keyboards import user_kb, settings_kb
from parse import parse
from SQL import db_user, db_bot, db_updates

from SETTINGS import *
from handlers.homework import make_homework_message

import datetime as DT
#User settings
# hw_alerts = True
# hw_schedule_time = '15:00'




class ScheduleTimeFSM(StatesGroup):
    time = State()




# Scheduler
#Запускается каждый день в определенное время, отправляет домашнее задаине на слудующий день.
async def get_homework_by_scheduler(chat_id, user_id):
    data = db_user.sql_get_auth_data(user_id)
    try:
        parse_res = parse.get_next_homework(data['login'], data['password'])
        day_of_week = parse_res[1]
        hw_list = parse_res[0]

        mess = make_homework_message(hw_list)

        await bot.send_message(chat_id, f'''
        <b>Домашнее задание на {day_of_week}</b>
        
{mess}
    ''')
    except:
        get_homework_by_scheduler(chat_id, user_id)


#Эта функция будет каждые n минут проверять наличие изменений в оценках.
# @dp.message_handler(commands=['test'])
# async def check_marks_updating(message:types.Message):
async def check_marks_updating(chat_id, user_id):
    # chat_id, user_id = message.chat.id, message.from_user.id
    auth_data = db_user.sql_get_auth_data(user_id)
    # today_marks = parse.get_today_marks(auth_data['login'], auth_data['password'])
    today_marks = {'Информатика': '5'}

    date = str(DT.datetime.now().date())
    last_update = db_updates.sql_get_last_marks_updates(user_id)

    #Перебираем полученный словарь с оценками, если он не пустой, сравниваем с предыдущим.
    if today_marks != 'no_homework_today' and last_update['marks'] is not None:
        new_marks = {}

        for subj in today_marks:
            #Получаем оценки по предмету за эту проверку и предыдущую, разбиваем строки по пробелам, делаем из них массивы
            actual_marks = today_marks[subj].split(' ')
            last_marks = last_update['marks'][subj].split(' ')

            print(subj)
            print(actual_marks, last_marks)

            #Проверяем каждую оценку, сравниваем её количество, добавляем в новый массив, если кол-во оценок увеличилось по сравнению с прошлым разом
            for i in ('1', '2', '3' ,'4' ,'5' ):
                if actual_marks.count(i) != last_marks.count(i):
                    if subj in new_marks:
                        new_marks[subj] = new_marks[subj] + (i + ' ') *  (actual_marks.count(i) - last_marks.count(i))
                        # print('2----', new_marks)  
                    else:
                        new_marks[subj] = (i + ' ') *  (actual_marks.count(i) - last_marks.count(i))
                        # print('2----', new_marks) 
                        #  
        for subj in new_marks:
            mes += '<b>' + subj + '</b>' + ': ' + new_marks[subj] + '\n'

        await bot.send_message(chat_id, f'''<b>Получены новые оценки!</b>
        

{mes}''')   
        #Заносим изменения в бд.    
        db_updates.sql_update_last_marks(user_id, date, today_marks)
    elif last_update['marks'] is None or date != last_update['date']:
        #Если оценки еще ни разу не заносили в базу или даты не совпадают, то заносим целиком
        mes = ''

        for subj in today_marks:
            mes += '<b>' + subj + '</b>' + ': ' + today_marks[subj] + '\n'

        await bot.send_message(chat_id, f'''<b>Получены новые оценки!</b>

{mes}''')

        #Заносим изменения в бд.
        db_updates.sql_update_last_marks(user_id, date, today_marks)




#Проверяет наличиче пропусков.
@dp.message_handler(commands=['test'])
# async def check_passes_updates(chat_id, user_id):
async def test(message: types.Message):
    chat_id, user_id = message.chat.id, message.from_user.id
    auth_data = db_user.sql_get_auth_data(user_id)
    actual_passes = parse.get_passses(auth_data['login'], auth_data['password'])

    last_passes_update = db_updates.sql_get_last_passes(user_id)

    #Если хоть одна запись в бд уже существует
    if last_passes_update is not None:
        last_pass_date = last_passes_update['date']
        last_pass = last_passes_update['passes']

        actual_date = str(DT.datetime.now().date())

        #Если уведомление уже отправлялось сегодня, т. даты равны
        if last_pass_date == actual_date:
            passes_update = {}
            for subj in actual_passes:
                for i in 'ПНБ':
                    if actual_passes.count(i) != last_pass.count(i):
                        if not subj in passes_update:
                            passes_update[subj] = (i + ' ') *  (actual_passes.count(i) - last_pass.count(i))
                        else:
                            passes_update[subj] = passes_update[subj] + (i + ' ') *  (actual_passes.count(i) - last_pass.count(i))

            mes = ''
            for subj in passes_update:
                mes += '<b>' + subj + '</b>' + ': ' + passes_update[subj] + '\n'

            await bot.send_message(chat_id, f'''<b>Пропуски за сегодняшний день:</b>     

{mes}''')   

            #Обновляем данные в бд.
            db_updates.sql_update_passes(user_id, actual_passes, actual_date)
        else:
            #Если за сегодня это впервые
            for subj in actual_passes:
                mes += '<b>' + subj + '</b>' + ': ' + actual_passes[subj] + '\n'

            await bot.send_message(chat_id, f'''<b>Пропуски за сегодняшний день:</b>     

{mes}''')  
            #Обновляем данные в бд.
            db_updates.sql_update_passes(user_id, actual_passes, actual_date)
    else:
        for subj in actual_passes:
            mes += '<b>' + subj + '</b>' + ': ' + actual_passes[subj] + '\n'

        await bot.send_message(chat_id, f'''<b>Пропуски за сегодняшний день:</b>     

{mes}''')  
        #Обновляем данные в бд.
        db_updates.sql_update_passes(user_id, actual_passes, actual_date)

#Включение меню настроек
@dp.callback_query_handler(text='set_menu_btn')
async def settings(callback: types.CallbackQuery):
    await callback.message.edit_text(text=SETTINGS_MENU_TEXT, reply_markup=settings_kb.settings_menu)

#Кнопка НАЗАД
@dp.callback_query_handler(text='settings_back_btn')
async def settings_back(callback:types.CallbackQuery):
    await callback.message.edit_text(text=MAIN_MENU_TEXT, reply_markup=user_kb.logged_keyboard)



# -----------------HOMEWORK-----------------
@dp.callback_query_handler(text='hw_settings_btn')
async def settings_hw(callback:types.CallbackQuery):
    await callback.answer('')

    if db_bot.sql_get_hw_alerts(callback.from_user.id):
        await callback.message.edit_text(text=SETTINGS_HOMEWORK_MENU_TEXT, reply_markup=settings_kb.hw_settings_menu_alerts_on)
    else:
        await callback.message.edit_text(text=SETTINGS_HOMEWORK_MENU_TEXT, reply_markup=settings_kb.hw_settings_menu_alerts_off)


#Изменение времени оповещений о дз
@dp.callback_query_handler(text='hw_time_settings_btn')
async def hw_time_settings(callback:types.CallbackQuery):
    global menu_message_id

    menu_message_id = callback.message.message_id
    await callback.message.answer('''Хорошо, теперь укажите время, в которое я буду присылать вам домашнее задание.

<i>Пример: 14:00</i>''')
    await ScheduleTimeFSM.time.set()

@dp.message_handler(state=ScheduleTimeFSM.time)
async def hw_time_editor(message: types.Message, state: FSMContext):
    if ':' in message.text:
        time = message.text.split(':')
        hour = time[0]
        minute = time[1]

        if len(hour) == 2 and len(minute) == 2 and int(hour) <= 23 and int(hour) >= 0 and int(minute) >= 0 and int(hour) <= 59:
            hw_schedule_time = message.text

            #Меняем время в бд и в планировщике
            db_bot.sql_change_hw_sheduler_time(message.from_user.id, hw_schedule_time)

            if scheduler.get_job('hw_scheduler'):
                if hour[0] == '0':
                    hour = hour[1:]
                if minute[0] == '0':
                    minute = minute[1:]

                scheduler.reschedule_job('hw_scheduler', trigger='cron', hour=hour, minute=minute)
            else:
                scheduler.add_job(get_homework_by_scheduler, 'cron', hour=hour, minute=minute, id='hw_scheduler', args=[message.chat.id, message.from_user.id])


            await message.answer(f'Время отправки домашних заданий изменено на <i><b>{hw_schedule_time}</b></i>')
            await bot.delete_message(message.chat.id, menu_message_id)
            await message.answer(SETTINGS_MENU_TEXT, reply_markup=settings_kb.settings_menu)

            await state.finish()
        else:
            await message.answer('Введены неверные данные')
    else:
        await message.answer('Дата должна быть в 24-часовом формате <i>(часы:минуты)</i>')




@dp.callback_query_handler(text='hw_alerts_off_btn')
async def hw_alerts_off(callback:types.CallbackQuery):
    db_bot.sql_change_hw_alerts(callback.from_user.id, False)

    # Удаляем задание отправки дз из планироващика, если оно есть
    if scheduler.get_job('hw_scheduler'):
        scheduler.remove_job('hw_scheduler')

    await callback.message.edit_reply_markup(settings_kb.hw_settings_menu_alerts_off)
    await callback.answer('Оповещения выключены', show_alert=True)


#Кнопка включения оповещений
@dp.callback_query_handler(text='hw_alerts_on_btn')
async def hw_alerts_off(callback:types.CallbackQuery):
    db_bot.sql_change_hw_alerts(callback.from_user.id, True)

    #Создаем задание заново
    time = db_bot.sql_get_hw_sheduler_time(callback.from_user.id)

    time = time.split(':')
    hour = time[0]
    minute = time[1]

    #Убираем ненужные нули вначале времени
    if hour[0] == '0':
        hour = hour[1:]
    if minute[0] == '0':
        minute = minute[1:]

    scheduler.add_job(get_homework_by_scheduler, 'cron', hour=hour, minute=minute, id='hw_scheduler', args=[callback.message.chat.id, callback.from_user.id])


    await callback.message.edit_reply_markup(settings_kb.hw_settings_menu_alerts_on)
    await callback.answer('Оповещения включены', show_alert=True)




@dp.callback_query_handler(text='hw_settings_back_btn')
async def hw_settings_back(callback:types.CallbackQuery):
    await callback.message.edit_text(text=SETTINGS_MENU_TEXT, reply_markup=settings_kb.settings_menu)



# -----------------MARKS----------------
@dp.callback_query_handler(text='marks_settings_btn')
async def marks_settings_btn(callback:types.CallbackQuery):
    await callback.answer('ok', show_alert=True)

