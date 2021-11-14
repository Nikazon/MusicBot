#
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
import youtube_dl
from youtube_search import YoutubeSearch
import requests


import os
from config import Config

bot = Client(
    'Nikazon',
    bot_token = Config.BOT_TOKEN,
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)



# конверт врмени
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------------------------------
@bot.on_message(filters.command(['start']))
def start(client, message):
    darkprince = f'👋 Привет @{message.from_user.username}\n Введи "/a название песни" для ее загрузки в телеграмм'
    message.reply_text(
        text=darkprince, 
        quote=False,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('Админ🎸', url='https://t.me/Nikazon'),
                ]
            ]
        )
    )



@bot.on_message(filters.command(['a']))
def a(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('🔎 Поиск песни...')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]

            ## UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            # if time_to_seconds(duration) >= 1800:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('Ничего не нашел. Попробуйте немного изменить название.')
            return
    except Exception as e:
        m.edit(
            "✖️ Ничего не нашел. Извините.\n\nПопробуйте другое ключевое слово или название"
        )
        print(str(e))
        return
    m.edit("⏬ Загрузка.")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎧 **Название**: [{title[:35]}]({link})\n⏳ **Продолжительность**: `{duration}`\n👁‍🗨 **Просмотров**: `{views}`'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='md',quote=False, title=title, duration=dur, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('❌ Ошибка')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

bot.run()