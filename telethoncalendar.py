import asyncio
from telethon import Button
import calendar
import datetime
import math

week_days_online = []
week_days_offline = []
work_hours_online = []
work_hours_offline = []

def create_callback_data(action,year,month,day):
    ''' Create the callback data associated to each button'''
    return ';'.join([action,str(year),str(month),str(day)])

def separate_callback_data(data):
    ''' Separate the callback data'''
    #print(str(data))
    # коллбек куэри возвращает данные в бинарном формате b'word', обошел это поиском по вхождению подстроки, переделать по-человечески
    return str(data).split(';')

def create_calendar(year=None, month=None, howto=''):
    '''
    Create an inline keyboard with the provided year and month
    :param int year: Year to use in the calendar, if None the current year is used.
    :param int month: Month to use in the calendar, if None the current month is used.
    :return: Returns the InlineKeyboardMarkup object with the calendar.
    '''
    now = datetime.datetime.now()
    if year == None: year = now.year
    if month == None: month = now.month
    data_ignore = create_callback_data('IGNORE', year, month, 0)

    if howto == 'online':
        week_days = week_days_online
    elif howto == 'offline':
        week_days = week_days_offline
    else:
        week_days = []
    
    keyboard = []
    #First row - Month and Year
    row=[]
    row.append(Button.inline(calendar.month_name[month]+' '+str(year),data=data_ignore))
    keyboard.append(row)
    #Second row - Week Days
    row=[]
    for day in ['Mo','Tu','We','Th','Fr','Sa','Su']:
        row.append(Button.inline(day,data=data_ignore))
    keyboard.append(row)

    my_calendar = calendar.monthcalendar(year, month)
    for week in my_calendar:
        row=[]
        for i, day in enumerate(week):
            if day == 0 or i in week_days:
                row.append(Button.inline('--',data=data_ignore))
            else:
                row.append(Button.inline(str(day),data=create_callback_data(howto+'_'+'DAY',year,month,day)))
        keyboard.append(row)
    #Last row - Buttons
    row=[]
    row.append(Button.inline('<',data=create_callback_data(howto+'_'+'PREV-MONTH', year, month, day)))
    row.append(Button.inline(' ',data=data_ignore))
    row.append(Button.inline('>',data=create_callback_data(howto+'_'+'NEXT-MONTH', year, month, day)))
    keyboard.append(row)

    return keyboard

def create_time_keyboard(date_only, howto=''):
    if howto == 'online':
        work_hours = work_hours_online
    elif howto == 'offline':
        work_hours = work_hours_offline
    else:
        work_hours = [11, 20]

    start_hour, end_hour = min(work_hours), max(work_hours)
    cols_count = int(math.sqrt(end_hour - start_hour))
    keyboard = []

    cur_hour = start_hour
    data_first_part = howto + '_' + 'HOUR;' + str(date_only) + ';'
    while cur_hour < end_hour:
        row = []
        for i in range(cols_count):
            time_text = str(datetime.time(hour=cur_hour, minute=0))
            callback_data = data_first_part + str(cur_hour)
            row.append(Button.inline(text=time_text, data=callback_data))
            cur_hour += 1
            if cur_hour >= end_hour:
                break
        keyboard.append(row)

    return keyboard

async def process_time_selection(client, event, date_only, howto=''):
    sender = await event.get_input_sender()
    await client.send_message(sender, date_only.strftime('%a %d.%b.%Y'), buttons=create_time_keyboard(date_only, howto))

async def process_calendar_selection(client, event):
    '''
    Process the callback_query. This method generates a new calendar if forward or
    backward is pressed. This method should be called inside a CallbackQueryHandler.
    :param telegram.Bot bot: The bot, as provided by the CallbackQueryHandler
    :param telegram.Update update: The update, as provided by the CallbackQueryHandler
    :return: Returns a tuple (Boolean,datetime.datetime), indicating if a date is selected
                and returning the date if so.
    '''
    ret_data = (False, None)
    query = event.data
    (action,year,month,day) = separate_callback_data(query)
    curr = datetime.datetime(int(year), int(month), 1)

    if 'online' in action:
        howto = 'online'
    elif 'offline' in action:
        howto = 'offline'
    else:
        howto = ''

    if 'IGNORE' in action:
        pass
        # await client.answer_callback_query(callback_query_id= query.id)
    elif 'HOUR' in action:
        pass
    elif 'DAY' in action:
        date_only = datetime.datetime(int(year),int(month),int(day[:-1]))     # remove last symbol in day variable (it is '-symbol)
        date_time = await process_time_selection(client, event, date_only, howto)
        ret_data = True, date_time
    elif 'PREV-MONTH' in action:
        pre = curr - datetime.timedelta(days=1)
        await client.edit_message(entity=event.chat_id, message=event.message_id,
            buttons=create_calendar(int(pre.year), int(pre.month), howto))
    elif 'NEXT-MONTH' in action:
        ne = curr + datetime.timedelta(days=31)
        await client.edit_message(entity=event.chat_id, message=event.message_id,
            buttons=create_calendar(int(ne.year), int(ne.month), howto))
    else:
        pass
        # await client.answer_callback_query(callback_query_id= query.id,text='Something went wrong!')
        # UNKNOWN
    return ret_data