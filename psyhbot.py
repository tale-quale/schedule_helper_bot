import asyncio
from telethon import TelegramClient, events, connection
from telethon import Button
from telethon.tl.types import TextBold
import telethoncalendar
from datetime import datetime as dt
import pymongo
import logging
import db_engine


# don`t forget about logging
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

# credentails for connection
api_id = '101010101'
api_hash = 'delleted_for_security_reasons'

client = TelegramClient('psyhbot', api_id, api_hash, 
                        connection=connection.ConnectionTcpMTProxyRandomizedIntermediate,
                        proxy=('proxy.digitalresistance.dog', 443, 'd41d8cd98f00b204e9800998ecf8427e'))

admin_username = '@getthatthing'

# define keyboards
def get_main_keyboard():
    return client.build_reply_markup([
                                      [Button.inline(text='Запись', data='new_record'), Button.inline(text='Мои записи', data='show_records')],
                                      [Button.inline(text='test', data='test'), Button.inline(text='Календарь', data='calendar')],
                                      ])

def get_text_keyboard():
    return client.build_reply_markup([
                                      [Button.text(text='Запись', resize=True), Button.text(text='Мои записи', resize=True)],
                                      [Button.text(text='Удалить записи', resize=True), Button.text(text='Еще', resize=True)],
                                      ])

def get_new_record_keyboard():
    return client.build_reply_markup([
                                      [Button.inline(text='Удаленно (Skype, Whatsapp)', data='online_record')],
                                      [Button.inline(text='У меня в кабинете', data='offline_record')]
                                      ])

new_record_keyboard = get_new_record_keyboard()
main_keyboard = get_text_keyboard()

settings = db_engine.get_settings()
week_days_online = [i for i, v in enumerate(settings['work_days_online']) if v == 0]
week_days_offline = [i for i, v in enumerate(settings['work_days_offline']) if v == 0]
work_hours_online = settings['work_hours_online']
work_hours_offline = settings['work_hours_online']
telethoncalendar.week_days_online = week_days_online
telethoncalendar.week_days_offline = week_days_offline
telethoncalendar.work_hours_online = work_hours_online
telethoncalendar.work_hours_offline = work_hours_offline

calendar_keyboard_online = telethoncalendar.create_calendar(howto='online')
calendar_keyboard_offline = telethoncalendar.create_calendar(howto='offline')

# test function
async def clock(delay):
    while True:
        await client.send_message('@getthatthing', str(dt.now()))
        await asyncio.sleep(delay)

'''
        -- Handlers for admin commands:
            - my schedule
            - my work days and hours
            - messages with comments (audio, text) attached to the concrete session with client
            - reports (comments by client/session, statistic by client and at overall)
        -- Handlers for user commands:
            - new record (date calendar, time calendar), cancel record, pay (qiwi?), my records;
            - fill personal name, surname and phone number;
    '''

# ==============================  ADMIN  =================================
# ==============================  HANDLERS  ==============================
#
@client.on(events.NewMessage(from_users=admin_username, pattern='/start'))
async def handler_admin_start(event):
    pass

@client.on(events.NewMessage(from_users=admin_username, pattern='/schedule'))
async def handler_admin_schedule(event):
    pass

@client.on(events.NewMessage(from_users=admin_username, pattern='/worktime'))
async def handler_admin_worktime(event):
    pass

@client.on(events.NewMessage(from_users=admin_username, pattern='/comments'))
async def handler_admin_comments(event):
    pass

@client.on(events.NewMessage(from_users=admin_username, pattern='/reports'))
async def handler_admin_reports(event):
    pass
#
# ==============================  End of ADMIN HANDLERS  ==============================

# ===============================  USER  ===============================
# =============================  HANDLERS  =============================
#
@client.on(events.NewMessage(pattern='/start'))
async def handler_user_start(event):
    sender = await event.get_input_sender()
    await event.delete()
    await client.send_message(sender, 'Hola!', buttons=main_keyboard)

@client.on(events.NewMessage(pattern='^(\/record_new|Запись|запись)$'))
async def handler_user_record_new(event):
    sender = await event.get_input_sender()
    await event.delete()
    await client.send_message(sender, 'Как Вам удобно лечить мозг?', buttons=new_record_keyboard)

@client.on(events.NewMessage(pattern='/record_cancel'))
async def handler_user_record_cancel(event):
    pass

@client.on(events.NewMessage(pattern='/record_my'))
async def handler_user_record_my(event):
    pass
#
# ==============================  End of USER HANDLERS  ==============================

# ==========================  Callback Query  ==========================
# =============================  HANDLERS  =============================
#

@client.on(events.CallbackQuery) # pattern='record' - argument don`t working properly (searching only exact match, can`t find 'online_record')
async def handler_callbackquery(event):
    
    sender = await event.get_input_sender()
    data = event.data
    if 'record' in str(data):
        if data == b'new_record':
            await client.send_message(sender, 'Как Вам удобно лечить мозг?', buttons=new_record_keyboard)
        elif data == b'online_record':
            await client.send_message(sender, 'Выберите дату:', buttons=calendar_keyboard_online)
        elif data == b'offline_record':
            await client.send_message(sender, 'Выберите дату:', buttons=calendar_keyboard_offline)
        elif data == b'show_records':
            pass

# trigger then new callback query is catched
#@client.on(events.CallbackQuery)
async def main_keyboard_handler222(event):
    sender = await event.get_input_sender()
    message = await event.get_message()
    await message.edit(buttons=None)
    data = event.data
    if 'record' in str(data):
        await manage_records(sender, data)
    elif data == b'show_records':
        records_list = []
        records_cur = await db_engine.get_records_by_user(tg_id=sender.user_id)
        for rec in records_cur:
            records_list.append(rec['time'])
        await client.send_message(sender, str(records_list), buttons=main_keyboard)
    elif data == b'calendar':
        settings = await db_engine.get_settings()
        await client.send_message(sender, 'Выберите дату:', buttons=calendar_keyboard_online)
    elif data == b'test':
        print(dir(event))
    else:
        # calendar buttons hundler
        print(await telethoncalendar.process_calendar_selection(client, event))


async def main():
    pass
    # await clock(1.12)

with client:
    #client.loop.run_until_complete(main())
    #client.start()
    client.run_until_disconnected()
    #client.loop.run_forever()