# -*- coding:utf -8 -*-
import datetime
from aiogram.utils import executor
from create_bot import dp
from handlers import client, admin
from apscheduler.schedulers.asyncio import AsyncIOScheduler



async def on_startup(_):
    print('Бот вкл  '+str(datetime.datetime.now()))
    scheduler.start()
    client.scheduler = scheduler
    try:
        scheduler.add_job(client.delete_last_message_end, "interval", minutes=1, id='del_mes')
    except:
        scheduler.remove_all_jobs()
        scheduler.add_job(client.delete_last_message_end, "interval", minutes=1, id='del_mes')

scheduler = AsyncIOScheduler()
admin.register_handlers_client(dp)
client.register_handlers_client(dp)
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
