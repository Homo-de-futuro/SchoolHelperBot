from lib2to3.pgen2 import driver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from datetime import datetime, timedelta
import os
import time
import pickle




def get_next_homework_date():
    now = datetime.now()
    
    if datetime.weekday(now) == 4:
        #Если это пятница, то мы добавляем еще 3 дня к дате, чтобы получить дз на понедельник 
        date = (datetime.now() + timedelta(days=3)).strftime("%d.%m.%Y")
    elif datetime.weekday(now) == 5:
        date = (datetime.now() + timedelta(days=2)).strftime("%d.%m.%Y")
    else:
        date = (datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y")

    return date, datetime.weekday(now)



def get_day_ow_week_from_int(day):
    if day == 0:
        return 'вторник'
    elif day == 1:
        return 'среду'
    elif day == 2:
        return 'четверг'
    elif day == 3:
        return 'пятницу'
    elif day == 4:
        return 'понедельник'
    elif day == 5:
        return 'понедельник'
    elif day == 6:
        return 'понедельник'



def init_driver(): 
    options = webdriver.ChromeOptions()  
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    # options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), options=options)

    return driver


#---------------------------------------------------------------------
#-----------------------------ACCOUNT---------------------------------
#---------------------------------------------------------------------

def is_account_exist_gos(user_login, user_password):
    url = 'https://login.dnevnik.ru/esia/redirect/adygea'
    driver = init_driver()
        
    try:
        print("--- Start is_account_exist_gos()")
        driver.get(url)
        print("--- Get url") 
        delay = 15

        # Вебдрайвер будет ждать загрузку страницы 10 секунд, иначе вызовет исключение
        login = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "login")))
        login.clear()
        login.send_keys(user_login)
        password = driver.find_element("id", "password")
        password.clear()
        password.send_keys(user_password)
        login_button = driver.find_element(By.CLASS_NAME, "plain-button_wide")
        login_button.click()
            
        # Здесь мы проверяем либо наличие ошибки при вводе указанных данных, что говорит о том, что такого пользователя нет, либо же факт загрузки главной страницы, что говорит об обратном.
        try:
            error = WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, "error-label")))
            if (error):
                print('---Account not exist')
                return False                  
        except:
            pass

        try:
            # Поиск ничего не значащего элемента на главной странице, который является подтверждением ее загрузки
            check = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "header-links__link")))

            if check:
                print('--- Account exist')
                
                return True
        except  Exception as ex1:
            print('--- ERROR in check_if_user_exist()')
            print(ex1)
            is_account_exist_gos(user_login, user_password)

    except Exception as ex:
        print('--- ERROR in check_if_user_exist()')
        print(ex)
        is_account_exist_gos(user_login, user_password)
    finally:
        driver.close()
        driver.quit()


#---------------------------------------------------------------------
#----------------------------HOMEWORK---------------------------------
#---------------------------------------------------------------------

def get_main_page(user_login, user_password, driver, delay):
    url = 'https://login.dnevnik.ru/esia/redirect/adygea'
    delay = 7

    driver.get(url)
    login = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, "login")))
    login.clear()
    login.send_keys(user_login)
    password = driver.find_element("id", "password")
    password.clear()
    password.send_keys(user_password)
    login_button = driver.find_element(By.CLASS_NAME, "plain-button_wide")
    login_button.click()



#Скрипт для получения страницы с домашним заданием на след. день и дальнейшим её парсингом.
def get_next_homework(login, password):
    driver = init_driver()
    delay = 7

    try: 
        get_main_page(login, password, driver, delay)
        home_work = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, "Домашние задания")))
        home_work.click()

        #Fills in fields with homework dates
        date, day_of_week = get_next_homework_date()
        
        date_from = driver.find_element(By.ID, 'datefrom')
        date_to = driver.find_element(By.ID, 'dateto')
        date_from.clear()
        date_to.clear()
        date_from.send_keys(date)
        date_to.send_keys(date)

        date_button = driver.find_element(By.ID, 'choose')
        date_button.click()

        page = BeautifulSoup(driver.page_source, 'lxml')

        #Разделяем дз на группы
        lines = page.find_all("tr")
        homework_dict = {}

        for i in range(1, len(lines)):
            #Find in this block subject and task and put it into variables
            subject = lines[i].find(class_="tac light").text
            task = lines[i].find(class_="breakword").text

            #Delete all unnecessary indents
            subject = " ".join(subject.split())
            task = " ".join(task.split())

            # If there is already a task in the dictionary, we add an additional task in this key
            if not(subject in homework_dict):
                homework_dict[subject] = task
            else:
                if homework_dict[subject] == task:
                    pass
                else:
                    homework_dict[subject] = homework_dict[subject] + ' ; ' + task
        print('--- Parse ended')
        return homework_dict, get_day_ow_week_from_int(day_of_week)
    except Exception as ex:
        print('--- ERROR in get_next_homework()')
        print(ex)
        get_next_homework(login, password)
    finally:
        driver.quit()
        print('--- Driver work ended')



def get_homework_by_date(login, password, date):
    driver = init_driver()
    delay = 7
    try:
        get_main_page(login, password, driver, delay)
        home_work = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, "Домашние задания")))
        home_work.click()

        day_ow_week = get_day_ow_week_from_int(datetime.weekday(date))

        dt = datetime.strptime(str(date), '%Y-%m-%d')
        date = dt.strftime('%d.%m.%Y')

        date_from = driver.find_element(By.ID, 'datefrom')
        date_to = driver.find_element(By.ID, 'dateto')
        date_from.clear()
        date_to.clear()
        date_from.send_keys(date)
        date_to.send_keys(date)

        date_button = driver.find_element(By.ID, 'choose')
        date_button.click()

        #Проверяем наличие ошибок, связанных с отсутствием домашнего задания
        try:
            hw_empty = driver.find_element(By.CLASS_NAME, 'emptyData')
            if hw_empty:
                print('--- WEEKEND')
                return 'WEEKEND'
        except:
            pass

        
        error_window = driver.find_element(By.ID, 'errors').text
        print(error_window)
        if error_window:
            print('--- YEAR')
            return 'YEAR'



        page = BeautifulSoup(driver.page_source, 'lxml')

        #Разделяем дз на группы
        lines = page.find_all("tr")
        homework_dict = {}

        for i in range(1, len(lines)):
            #Find in this block subject and task and put it into variables
            subject = lines[i].find(class_="tac light").text
            task = lines[i].find(class_="breakword").text

            #Delete all unnecessary indents
            subject = " ".join(subject.split())
            task = " ".join(task.split())

            # If there is already a task in the dictionary, we add an additional task in this key
            if not(subject in homework_dict):
                homework_dict[subject] = task
            else:
                if homework_dict[subject] == task:
                    pass
                else:
                    homework_dict[subject] = homework_dict[subject] + ' ; ' + task
        print('--- Parse ended')

        return homework_dict, day_ow_week

    except Exception as ex:
        print('--- ERROR in get_homework_by_date()')
        print(ex)
        get_homework_by_date(login, password, date)
    finally:
        driver.quit()



#---------------------------------------------------------------------
#------------------------------MARKS---------------------------------
#---------------------------------------------------------------------

def get_today_marks(login, password):
    driver = init_driver()
    delay = 10

    get_main_page(login, password, driver, delay)
     
    try:
        #Ищем кнопку домашнего задания, чтобы убедиться, что страница загружена
        home_work = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, "Домашние задания")))
            
        page = BeautifulSoup(driver.page_source, 'lxml')
        last_marks_div = page.find(class_='XzgGs')
        
        if last_marks_div is not None:
            #Получаем дату
            last_marks_date = last_marks_div.find(class_='_8aeAc').text
                
            if last_marks_date == 'Сегодня':
                today_marks = last_marks_div.find_all(class_='LO0nf')

                #Формируем словарь с предметами и оценками
                marks = {}
                for item in today_marks:
                    subject = item.find(class_='_36lYy').text
                    mark = item.find(class_='_38lGE').text

                    if not(subject in marks):
                        marks[subject] = mark
                    else:
                        marks[subject] = marks[subject] + ' ' + mark
                
                print(marks)
                return marks
            else:
                return 'no_homework_today'
        else:
            return 'no_homework_today'
    except Exception as ex:
        print('--- ERROR in get_today_marks()')
        get_today_marks(login, password)
    finally:
        driver.quit()


#Получение оценок за неделю
def get_week_marks(login, password):
    driver = init_driver()
    delay = 10

    try:
        get_main_page(login, password, driver, delay)

        #Ищем кнопку домашнего задания, чтобы убедиться, что страница загружена
        page_with_marks_btn = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, "Успеваемость")))
        page_with_marks_btn.click()

        #Ищем ничего не значащий элемент для полной загрузки страницы
        e = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'TabStats')))

        page = BeautifulSoup(driver.page_source, 'lxml')
        
        #Т.к. страница разделена на 2 блока, проходимся по каждому из них (правый и левый)
        pages_sides = [page.find(id='diarydaysleft'), page.find(id='diarydaysright')]

        days = {}

        for side in pages_sides:
            #Получаем блоки div каждого дня недели
            divs_with_days_of_week = side.find_all(class_='col24')

            for div in divs_with_days_of_week:
                day_of_week = div.find('h3').text.split(',')[0]

                #Разбиваем на строки каждый блок
                makrs_and_subjects = {}
                strings = div.find_all('tr')
                
                for s in strings:
                    #Название предмета
                    subject = s.find(class_='s2').find('a').text
                    
                    #Проверяем, есть ли оценка
                    mark = s.find_all(class_='tac')[1].find('span')
                    
                    if mark is not None: 
                        #Если 2 оценки по одному предмету, то они записываются через пробел
                        if day_of_week in makrs_and_subjects:
                            makrs_and_subjects[subject] = makrs_and_subjects[subject] + ' ' + mark.text
                        else:
                            makrs_and_subjects[subject] = mark.text


                if len(makrs_and_subjects) > 0:
                    days[day_of_week] = makrs_and_subjects
        
        return days

    except Exception as ex:
        print(ex)
        get_week_marks(login, password)
    finally:
        driver.quit()




def get_passses(login, password):
    driver = init_driver()
    delay = 10

    try:
        get_main_page(login, password, driver, delay)


        page_with_marks_btn = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.LINK_TEXT, "Успеваемость")))
        page_with_marks_btn.click()

        #Ищем ничего не значащий элемент для полной загрузки страницы
        e = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'TabStats')))

        page = BeautifulSoup(driver.page_source, 'lxml')
        
        #Т.к. страница разделена на 2 блока, проходимся по каждому из них (правый и левый)
        pages_sides = [page.find(id='diarydaysleft'), page.find(id='diarydaysright')]
        
        actual_passes = {}
        for side in pages_sides:
            #Получаем блоки div каждого дня недели
            divs_with_days_of_week = side.find_all(class_='col24')

            for div in divs_with_days_of_week:
                #Получаем число месяца из этого блока, убираем ненужные пробелы, сравниваем его с сегодняшним, если совпадают - ищем пропуски 
                day = div.find('h3').text.split(',')[1].split('&nbsp')[0].split('\xa0')[0]
                day = str(day).replace(' ', '')
                
                #Если это блок за сегодняшний день - ищем пропуски
                if day == '23' and div.find('emptyData') is None:
                    strings = div.find_all('tr')
                    for s in strings:
                        subject = s.find(class_='s2').find('a').text
                        pass_status = s.find(class_='tac').find('span')
                        # print(s.find(class_='tac').find('span'))
                        if pass_status is not None:
                            if subject not in actual_passes:
                                actual_passes[subject] = pass_status.text + ' ' 
                            else:
                                actual_passes[subject] = pass_status[subject] + pass_status.text
                    break    
        if len(actual_passes) != 0:
            return actual_passes
        else:
            return False

    except Exception as ex:
        print(f'--- ERROR in get_passses(): {ex}')
        get_passses(login, password)
    finally:
        driver.quit()



# print(get_passses('+79649255673', 'dbtuvkUf_4gk'))