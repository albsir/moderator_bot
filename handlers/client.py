import datetime
import json
import os
from json import JSONDecodeError
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.exceptions import CantParseEntities, CantInitiateConversation, BadRequest
from create_bot import bot
from handlers import admin
from apscheduler.schedulers.asyncio import AsyncIOScheduler


class FSMClient(StatesGroup):
    begin = State()


scheduler = AsyncIOScheduler()
path_deleting_messages = os.getcwd() + "/" + "json/option_for_bot/messages_deleting.json"
seconds_for_deleting_message = 55
path_json_for_bot_texts = os.getcwd() + "/" + "json/option_for_bot/texts.json"
path_to_keyboards_json_for_bot = os.getcwd() + "/" + "json/option_for_bot/texts_to_keyboards.json"
path_for_chats_options = os.getcwd() + "/" + "json/chats/options/"
path_for_people_chats = os.getcwd() + "/" + "json/people/chats/"
path_option_bot = os.getcwd() + "/" + "json/option_for_bot/option.json"


async def answers_bot_for_client_in_chat(answer_type: str):
    global path_json_for_bot_texts
    with open(path_json_for_bot_texts, "r", encoding='cp1251') as file:
        answers_text_bot = json.load(file)
    return answers_text_bot[answer_type]


async def delete_last_message_begin(message: types.Message):
    global path_deleting_messages, seconds_for_deleting_message
    message_to_json = json.loads(message.as_json())
    time_to_delete = str(datetime.datetime.now() + datetime.timedelta(seconds=seconds_for_deleting_message))
    message_to_json.update({"end_time": time_to_delete})
    try:
        with open(path_deleting_messages, "r", encoding='cp1251') as file:
            messages_deleting_bot = json.load(file)
        messages_deleting_bot.append(message_to_json)
        with open(path_deleting_messages, 'w', encoding='cp1251') as file:
            json.dump(messages_deleting_bot, file, ensure_ascii=False)
    except JSONDecodeError:
        messages_deleting_bot = [message_to_json]
        with open(path_deleting_messages, 'w', encoding='cp1251') as file:
            json.dump(messages_deleting_bot, file, ensure_ascii=False)


async def delete_last_message_end():
    global path_deleting_messages, scheduler
    messages_deleting_bot = []
    try:
        with open(path_deleting_messages, "r", encoding='cp1251') as file:
            messages_deleting_bot = json.load(file)
    except JSONDecodeError as err:
        pass
    if len(messages_deleting_bot) > 0:
        new_array = []
        time_now = datetime.datetime.now()
        for item in messages_deleting_bot:
            item["end_time"] = item["end_time"].replace(' ', 'T')
            try:
                check_time_format = "%Y-%m-%dT%H:%M:%S.%f"
                end_time_delete = datetime.datetime.strptime(item["end_time"], check_time_format)
            except ValueError:
                check_time_format = "%Y-%m-%dT%H:%M:%S"
                end_time_delete = datetime.datetime.strptime(item["end_time"], check_time_format)
            if end_time_delete <= time_now:
                try:
                    await bot.delete_message(item["chat"]["id"],
                                             item["message_id"])
                except:
                    pass
            else:
                new_array.append(item)
        messages_deleting_bot = new_array
        with open(path_deleting_messages, 'w', encoding='cp1251') as file:
            json.dump(messages_deleting_bot, file, ensure_ascii=False)
    # scheduler.remove_job('del_mes')


async def create_new_member_file(message: types.Message):
    global path_for_people_chats
    try:
        os.mkdir(path_for_people_chats + str(message.chat.id))
    except FileExistsError:
        pass
    path_for_json_human = path_for_people_chats + str(message.chat.id) + "/" + str(message.from_user.id) + ".json"
    time_str = str(datetime.datetime.now() - datetime.timedelta(days=1))
    option_this_human = {"admin": False, "check_human": False, "Warning": 0, "Ban": False,
                         "Time_to_ban_in_minutes": 0,
                         "last_sms_data": time_str, "messages_allowed_id": [], "messages_allowed_time": []}
    if await admin.check_user_for_admin(str(message.from_user.username), str(message.chat.id)):
        option_this_human["admin"] = True
        option_this_human["check_human"] = True
        with open(path_for_json_human, 'w', encoding='cp1251') as file:
            json.dump(option_this_human, file, ensure_ascii=False)
        return True
    else:
        with open(path_for_json_human, 'w', encoding='cp1251') as file:
            json.dump(option_this_human, file, ensure_ascii=False)
        return False


async def check_new_member(message: types.Message):
    global path_for_people_chats
    path_for_json_human = path_for_people_chats + str(message.chat.id) + "/" + str(message.from_user.id) + ".json"
    try:
        with open(path_for_json_human, "r", encoding='cp1251') as file:
            option_this_human = json.load(file)
        if option_this_human["admin"]:
            await admin.command_start_type_message(message)
        elif await admin.check_user_for_admin(str(message.from_user.username), str(message.chat.id)):
            option_this_human["admin"] = True
            option_this_human["check_human"] = True
            with open(path_for_json_human, 'w', encoding='cp1251') as file:
                json.dump(option_this_human, file, ensure_ascii=False)
            answer = await answers_bot_for_client_in_chat("check_right_admin")
            try:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer, parse_mode="Markdown"))
            except CantParseEntities:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
            except CantInitiateConversation:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
            await admin.command_start_type_message(message)
        elif option_this_human["check_human"]:
            return
        else:
            option_this_human["check_human"] = True
            with open(path_for_json_human, 'w', encoding='cp1251') as file:
                json.dump(option_this_human, file, ensure_ascii=False)
            answer = await answers_bot_for_client_in_chat("check_again")
            try:
                await delete_last_message_begin(
                    await bot.send_message(message.chat.id, answer, parse_mode="Markdown"))
            except CantParseEntities:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
            except CantInitiateConversation:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
    except FileNotFoundError:
        if await create_new_member_file(message):
            answer = await answers_bot_for_client_in_chat("check_right_admin")
            try:
                await delete_last_message_begin(
                    await bot.send_message(message.from_user.id, answer, parse_mode="Markdown"))
            except CantParseEntities:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
            except CantInitiateConversation:
                await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
            await admin.command_start_type_message(message)
        else:
            answer = await answers_bot_for_client_in_chat("check_first_reg")
            keyboard = InlineKeyboardMarkup()
            await link_rules_chat(message, answer, keyboard)


async def handler_new_member(message: types.Message):
    global path_for_people_chats, path_for_chats_options, path_option_bot
    path_for_json_human = path_for_people_chats + str(message.chat.id) + "/" + str(message.from_user.id) + ".json"
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    for new_member in message.new_chat_members:
        try:
            with open(path_for_json_human, 'r', encoding='cp1251') as file:
                option_this_human = json.load(file)
            if option_this_human["check_human"]:
                answer = "@" + str(new_member.username) + " "
                answer += await answers_bot_for_client_in_chat("return_in_chat")
                try:
                    await delete_last_message_begin(
                        await bot.send_message(message.chat.id, answer, parse_mode="Markdown"))
                except CantParseEntities:
                    await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
                except CantInitiateConversation:
                    await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
            else:
                answer = "@" + str(new_member.username) + " "
                answer += await answers_bot_for_client_in_chat("return_in_chat_but_not_checked")
                try:
                    await delete_last_message_begin(
                        await bot.send_message(message.chat.id, answer, parse_mode="Markdown"))
                except CantParseEntities:
                    await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
                except CantInitiateConversation:
                    await delete_last_message_begin(await bot.send_message(message.chat.id, answer))
        except FileNotFoundError:
            keyboard = InlineKeyboardMarkup()
            with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
                options_chat = json.load(file)
            for item in options_chat:
                if len(item["need_channels_subscription"]) < 1:
                    with open(path_option_bot, 'r', encoding='cp1251') as file:
                        option_bot = json.load(file)
                    button = InlineKeyboardButton('Подписаться', url=option_bot["default_link"])
                    keyboard.add(button)
                else:
                    for channel in item["need_channels_subscription"]:
                        button = InlineKeyboardButton('Подписаться', url=channel)
                        keyboard.add(button)
            if options_chat[0]["link_to_rules"] == "":
                return
            answer = "@" + str(new_member.username) + " "
            answer += await answers_bot_for_client_in_chat("new_member_welcome")
            await create_new_member_file(message)
            await link_rules_chat(message, answer, keyboard)


async def update_last_sms_human(message: types.Message):
    global path_for_people_chats
    path_for_human_chats_option = path_for_people_chats + str(message.chat.id) + "/" + str(
        message.from_user.id) + ".json"
    with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
        option_this_human = json.load(file)
    option_this_human["last_sms_data"] = str(datetime.datetime.now())
    with open(path_for_human_chats_option, "w", encoding='cp1251') as file:
        json.dump(option_this_human, file, ensure_ascii=False)


async def check_count_warning(message: types.Message, warning: bool):
    global path_for_chats_options, path_for_people_chats
    path_for_human_chats_option = path_for_people_chats + str(message.chat.id) + "/" + str(
        message.from_user.id) + ".json"
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    try:
        with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
            option_this_human = json.load(file)
    except FileNotFoundError:
        await create_new_member_file(message)
        with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
            option_this_human = json.load(file)
    if warning:
        option_this_human["Warning"] += 1
        if option_this_human["Warning"] == 5:
            with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
                options_chat = json.load(file)
            for item in options_chat:
                if item["id"] == message.chat.id:
                    new_dict = {"username": message.from_user.username, "id_user": message.from_user.id}
                    item["humans_ban"].append(new_dict)
                    break
                print("error check_count_warning")
            with open(path_to_chats_options_this_chat, "w", encoding='cp1251') as file:
                json.dump(options_chat, file, ensure_ascii=False)
            option_this_human["Warning"] = 0
            option_this_human["Ban"] = True
            option_this_human["Time_to_ban_in_minutes"] = 1440
            with open(path_for_human_chats_option, "w", encoding='cp1251') as file:
                json.dump(option_this_human, file, ensure_ascii=False)
    else:
        option_this_human["Warning"] = 0
        with open(path_for_human_chats_option, "w", encoding='cp1251') as file:
            json.dump(option_this_human, file, ensure_ascii=False)


async def check_verification(message: types.Message, completed: bool):
    global path_for_people_chats, path_for_chats_options
    path_for_human_chats_option = path_for_people_chats + str(message.chat.id) + "/" + str(
        message.from_user.id) + ".json"
    try:
        with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
            option_this_human = json.load(file)
        if option_this_human["check_human"]:
            return True
        elif completed:
            option_this_human["check_human"] = True
            with open(path_for_human_chats_option, 'w', encoding='cp1251') as file:
                json.dump(option_this_human, file, ensure_ascii=False)
            return True
        else:
            answer = await check_have_username(message) + " "
            answer += await answers_bot_for_client_in_chat("return_in_chat_but_not_checked")
            await bot.delete_message(message.chat.id, message.message_id)
            keyboard = InlineKeyboardMarkup()
            await link_rules_chat(message, answer, keyboard)
            return False
    except:
        time_str = str(datetime.datetime.now() - datetime.timedelta(days=1))
        if completed:
            option_this_human = {"admin": False, "check_human": True, "Warning": 0, "Ban": False,
                                 "Time_to_ban_in_minutes": 0,
                                 "last_sms_data": time_str}
            with open(path_for_human_chats_option, 'w', encoding='cp1251') as file:
                json.dump(option_this_human, file, ensure_ascii=False)
            return True
        else:
            option_this_human = {"admin": False, "check_human": False, "Warning": 0, "Ban": False,
                                 "Time_to_ban_in_minutes": 0,
                                 "last_sms_data": time_str}
            with open(path_for_human_chats_option, 'w', encoding='cp1251') as file:
                json.dump(option_this_human, file, ensure_ascii=False)
            answer = await check_have_username(message) + " "
            answer += await answers_bot_for_client_in_chat("return_in_chat_but_not_checked")
            await bot.delete_message(message.chat.id, message.message_id)
            keyboard = InlineKeyboardMarkup()
            await link_rules_chat(message, answer, keyboard)
            return False


async def check_ban_user(message: types.Message):
    global path_for_chats_options, path_for_people_chats
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    path_for_human_chats_option = path_for_people_chats + str(message.chat.id) + "/" + str(
        message.from_user.id) + ".json"
    try:
        with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
            option_this_human = json.load(file)
        if option_this_human["Ban"]:
            option_this_human["last_sms_data"] = option_this_human["last_sms_data"].replace(' ', 'T')
            option_this_human["last_sms_data"] = option_this_human["last_sms_data"][
                                                 :option_this_human["last_sms_data"].rfind('.')]
            last_sms_time = datetime.datetime.strptime(option_this_human["last_sms_data"], "%Y-%m-%dT%H:%M:%S")
            time_delta = datetime.datetime.now() - last_sms_time
            if time_delta.total_seconds() / 60 > option_this_human["Time_to_ban_in_minutes"]:
                with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
                    options_chat = json.load(file)
                for item in options_chat:
                    if item["id"] == message.chat.id:
                        for user_info in item["humans_ban"]:
                            if user_info["id_user"] == message.from_user.id:
                                item["humans_ban"].remove(user_info)
                                break
                        break
                    print("error check_ban_user")
                with open(path_to_chats_options_this_chat, "w", encoding='cp1251') as file:
                    json.dump(options_chat, file, ensure_ascii=False)
                option_this_human["Ban"] = False
                option_this_human["Time_to_ban_in_minutes"] = 0
                time_str = str(datetime.datetime.now() - datetime.timedelta(days=1))
                option_this_human["last_sms_data"] = str(time_str)
                with open(path_for_human_chats_option, "w", encoding='cp1251') as file:
                    json.dump(option_this_human, file, ensure_ascii=False)
                return False
            else:
                await bot.delete_message(message.chat.id, message.message_id)
                answer = await check_have_username(message) + " "
                answer += await answers_bot_for_client_in_chat("banned_user_in_chat")
                seconds_ban_user = option_this_human["Time_to_ban_in_minutes"] - time_delta.total_seconds() / 60
                round_seconds_ban_user = round(seconds_ban_user, 0)
                answer += " " + str(round_seconds_ban_user / 60)
                keyboard = InlineKeyboardMarkup()
                await link_rules_chat(message, answer, keyboard)
                return True
        else:
            return False
    except FileNotFoundError:
        await create_new_member_file(message)
        return False


async def check_channels_subscription(message: types.Message):
    global path_for_chats_options, path_for_people_chats
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    subscription = True
    keyboard = InlineKeyboardMarkup()
    with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
        options_chat = json.load(file)
    for item in options_chat:
        if len(item["need_channels_subscription"]) < 1:
            with open(path_option_bot, 'r', encoding='cp1251') as file:
                option_bot = json.load(file)
            name_channel = str(option_bot["default_link"])
            name_channel = name_channel[name_channel.rfind('/') + 1:]
            name_channel = "@" + name_channel
            try:
                user_channel_status = await bot.get_chat_member(chat_id=name_channel, user_id=message.from_user.id)
                if user_channel_status["status"] != 'left':
                    continue
                else:
                    subscription = False
                    button = InlineKeyboardButton('Подписаться', url=option_bot["default_link"])
                    keyboard.add(button)
                    break
            except BadRequest:
                subscription = False
                button = InlineKeyboardButton('Подписаться', url=option_bot["default_link"])
                keyboard.add(button)
        else:
            for channel in item["need_channels_subscription"]:
                name_channel = str(channel)
                name_channel = name_channel[name_channel.rfind('/') + 1:]
                name_channel = "@" + name_channel
                try:
                    user_channel_status = await bot.get_chat_member(chat_id=name_channel, user_id=message.from_user.id)
                    if user_channel_status["status"] != 'left':
                        continue
                    else:
                        subscription = False
                        button = InlineKeyboardButton('Подписаться', url=channel)
                        keyboard.add(button)
                except BadRequest:
                    subscription = False
                    button = InlineKeyboardButton('Подписаться', url=channel)
                    keyboard.add(button)

    if subscription:
        return True
    else:
        answer = await check_have_username(message) + " "
        answer += await answers_bot_for_client_in_chat("user_not_sub_channel")
        await bot.delete_message(message.chat.id, message.message_id)
        await link_rules_chat(message, answer, keyboard)
        return False


async def check_chat_spam(message: types.Message):
    global path_for_people_chats
    path_for_human_chats_option = path_for_people_chats + str(message.chat.id) + "/" + str(
        message.from_user.id) + ".json"
    try:
        with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
            option_this_human = json.load(file)
    except FileNotFoundError:
        time_str = str(datetime.datetime.now() - datetime.timedelta(days=1))
        option_this_human = {"admin": False, "check_human": True, "Warning": 0, "Ban": False,
                             "Time_to_ban_in_minutes": 0,
                             "last_sms_data": time_str}
        with open(path_for_human_chats_option, 'w', encoding='cp1251') as file:
            json.dump(option_this_human, file, ensure_ascii=False)
        return False
    option_this_human["last_sms_data"] = option_this_human["last_sms_data"].replace(' ', 'T')
    option_this_human["last_sms_data"] = option_this_human["last_sms_data"][
                                         :option_this_human["last_sms_data"].rfind('.')]
    last_sms_time = datetime.datetime.strptime(option_this_human["last_sms_data"], "%Y-%m-%dT%H:%M:%S")
    time_delta = datetime.datetime.now() - last_sms_time
    if time_delta.total_seconds() <= 2.5:
        answer = await check_have_username(message) + " "
        answer += await answers_bot_for_client_in_chat("user_is_spam")
        await bot.delete_message(message.chat.id, message.message_id)
        keyboard = InlineKeyboardMarkup()
        await link_rules_chat(message, answer, keyboard)
        return True
    else:
        return False


async def check_ban_words(message: types.Message):
    global path_for_chats_options
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    check_text_in_word_ban = message.text
    check_text_in_word_ban = check_text_in_word_ban.lower()
    with open(path_to_chats_options_this_chat, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == message.chat.id:
            for word in item["words_ban"]:
                if check_text_in_word_ban.find(word) >= 0:
                    answer = await check_have_username(message) + " "
                    answer += str(await answers_bot_for_client_in_chat("user_use_ban_word_begin")) + " "
                    answer += "*" + str(word) + "* "
                    answer += str(await answers_bot_for_client_in_chat("user_use_ban_word_end"))
                    await bot.delete_message(message.chat.id, message.message_id)
                    keyboard = InlineKeyboardMarkup()
                    await link_rules_chat(message, answer, keyboard)
                    return True
            return False


async def check_hashtag_without_photo_in_message(message: types.Message):
    global path_for_chats_options
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    if message.text.find('#') >= 0:
        new_message = message.text.lower()
        new_message = new_message[new_message.find('#'):]
        if new_message.find(' ') >= 0:
            new_message = new_message[:new_message.find(' ')]
        elif new_message.find('\n') >= 0:
            new_message = new_message[:new_message.find('\n')]
        new_message = new_message.replace('#', '')
        with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
            options_chat = json.load(file)
        for item in options_chat:
            for hashtag in item["allow_hashtag_without_photo"]:
                if hashtag == new_message:
                    return True
        new_message = "#" + new_message
        answer = await check_have_username(message) + " "
        answer += str(await answers_bot_for_client_in_chat("user_use_ban_hashtag_without_photo_begin")) + " "
        answer += "*" + new_message + "* "
        answer += str(await answers_bot_for_client_in_chat("user_use_ban_hashtag_without_photo_end"))
        await bot.delete_message(message.chat.id, message.message_id)
        keyboard = InlineKeyboardMarkup()
        await link_rules_chat(message, answer, keyboard)
        return False
    else:
        return True


async def check_hashtag_with_photo_in_message(message: types.Message):
    global path_for_chats_options
    await admin.option_in_bot_after_add_chat(message)
    if await admin.check_user_for_admin(str(message.from_user.username), str(message.chat.id)):
        return
    check = False
    answer = ""
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    new_message = message.caption
    if new_message is None:
        answer = "@" + str(message.from_user.username) + " "
        answer += await answers_bot_for_client_in_chat("user_not_use_hashtag_with_photo")
        check = False
    elif new_message.find('#') >= 0:
        new_message = new_message.lower()
        new_message = new_message[new_message.find('#'):]
        if new_message.find(' ') >= 0:
            new_message = new_message[:new_message.find(' ')]
        elif new_message.find('\n') >= 0:
            new_message = new_message[:new_message.find('\n')]
        new_message = new_message.replace('#', '')
        with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
            options_chat = json.load(file)
        for item in options_chat:
            for hashtag in item["allow_hashtag_with_photo"]:
                if hashtag == new_message:
                    check = True
                    break
        if not check:
            new_message = "#" + new_message
            answer = await check_have_username(message) + " "
            answer += str(await answers_bot_for_client_in_chat("user_use_ban_hashtag_with_photo_begin")) + " "
            answer += "*" + new_message + "* "
            answer += str(await answers_bot_for_client_in_chat("user_use_ban_hashtag_with_photo_end"))
            check = False
    else:
        check = True
    if not check:
        if answer == "":
            await update_last_sms_human(message)
            await check_count_warning(message, False)
        else:
            await bot.delete_message(message.chat.id, message.message_id)
            await check_count_warning(message, True)
            await update_last_sms_human(message)
            keyboard = InlineKeyboardMarkup()
            await link_rules_chat(message, answer, keyboard)


async def delete_link_in_chat(message: types.Message):
    global path_for_chats_options
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    message_text = message.text.lower()
    for entity in message.entities:
        if entity.type in ["url", "text_link"]:
            with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
                options_chat = json.load(file)
            for item in options_chat:
                for link in item["allowed_links"]:
                    if link in message_text:
                        return False
            answer = await check_have_username(message) + " "
            answer += await answers_bot_for_client_in_chat("user_use_not_allowed_link")
            await bot.delete_message(message.chat.id, message.message_id)
            keyboard = InlineKeyboardMarkup()
            await link_rules_chat(message, answer, keyboard)
            return True
    return False


async def link_rules_chat(message, answer_begin: str, keyboard: InlineKeyboardMarkup):
    global path_for_chats_options
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    with open(path_to_chats_options_this_chat, "r", encoding='cp1251') as file:
        options_chat = json.load(file)
    if options_chat[0]["link_to_rules"] == "":
        pass
    else:
        button = InlineKeyboardButton('Правила чата', url=options_chat[0]["link_to_rules"],
                                      callback_data='client_open_rules_chat')
        keyboard.add(button)
    answer = answer_begin + "\n"
    answer += await answers_bot_for_client_in_chat("send_rules_chat")
    try:
        if options_chat[0]["link_to_rules"] != "":
            await delete_last_message_begin(await bot.send_message(message.chat.id,
                                                                   answer,
                                                                   parse_mode="Markdown", reply_markup=keyboard))
            await delete_last_message_begin(await bot.send_message(message.chat.id, " ", reply_markup=keyboard))
        else:
            await delete_last_message_begin(
                await bot.send_message(message.chat.id,
                                       answer +
                                       "\nК сожалению на данный момент, нет ссылки на правила чата",
                                       parse_mode="Markdown"))
    except:
        pass


async def check_have_username(message: types.Message):
    if str(message.from_user.username) == "None":
        if str(message.from_user.last_name) == "None" or str(message.from_user.first_name) == "None":
            return "Уважаемый подписчик,"
        else:
            return "Уважаемый(ая) " + str(message.from_user.last_name) + " " + str(message.from_user.first_name) + ","
    else:
        return "@" + str(message.from_user.username) + ","


async def accept_verification(callback: types.CallbackQuery):
    await check_verification(callback.message, True)
    await callback.answer()


async def add_allow_message_in_list_messages_user(message: types.Message):
    path_for_human_chats_option = path_for_people_chats + str(message.chat.id) + "/" + str(
        message.from_user.id) + ".json"
    with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
        option_this_human = json.load(file)
    option_this_human["messages_allowed_id"].append(message.message_id)
    option_this_human["messages_allowed_time"].append(str(datetime.datetime.now()))
    with open(path_for_human_chats_option, 'w', encoding='cp1251') as file:
        json.dump(option_this_human, file, ensure_ascii=False)


async def user_unsub_delete_messages_from_chats(message: types.Message):
    global path_for_people_chats
    name_folders = os.listdir(path_for_people_chats)
    for i in range(len(name_folders)):
        chat_id = name_folders[i]
        path_for_human_chats_option = path_for_people_chats + str(chat_id) + "/" + str(
            message.from_user.id) + ".json"
        try:
            with open(path_for_human_chats_option, "r", encoding='cp1251') as file:
                option_this_human = json.load(file)
        except FileNotFoundError:
            continue
        for j in option_this_human["messages_allowed_id"]:
            try:
                check_time_format = "%Y-%m-%dT%H:%M:%S.%f"
                time_in_option = datetime.datetime.strptime(
                    option_this_human["messages_allowed_time"][j], check_time_format)
            except ValueError:
                check_time_format = "%Y-%m-%dT%H:%M:%S"
                time_in_option = datetime.datetime.strptime(
                    option_this_human["messages_allowed_time"][j], check_time_format)
            delta_time = datetime.datetime.now() - time_in_option
            if delta_time.days < 4:
                await bot.delete_message(chat_id, option_this_human["messages_allowed_id"][j])
        option_this_human["messages_allowed_id"] = []
        option_this_human["messages_allowed_time"] = []
        with open(path_for_human_chats_option, 'w', encoding='cp1251') as file:
            json.dump(option_this_human, file, ensure_ascii=False)


async def delete_word_in_chat(message: types.Message):
    """
    if not await check_verification(message, False):
        await check_count_warning(message, True)
        await update_last_sms_human(message)
    """
    await admin.option_in_bot_after_add_chat(message)
    if await admin.check_user_for_admin(str(message.from_user.username), str(message.chat.id)):
        return
    if await check_ban_user(message):
        return
    elif not await check_channels_subscription(message):
        await check_count_warning(message, True)
        await update_last_sms_human(message)
    elif await check_chat_spam(message):
        await check_count_warning(message, True)
        await update_last_sms_human(message)
    elif await check_ban_words(message):
        await check_count_warning(message, True)
        await update_last_sms_human(message)
    elif await delete_link_in_chat(message):
        await check_count_warning(message, True)
        await update_last_sms_human(message)
    elif not await check_hashtag_without_photo_in_message(message):
        await check_count_warning(message, True)
        await update_last_sms_human(message)
    else:
        await update_last_sms_human(message)
        await check_count_warning(message, False)
        await add_allow_message_in_list_messages_user(message)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(check_hashtag_with_photo_in_message,
                                chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                                content_types=['photo'], commands=None, state=None)

    dp.register_callback_query_handler(accept_verification, chat_type=types.ChatType.PRIVATE,
                                       text='client_open_rules_chat')

    dp.register_message_handler(check_new_member, chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                                commands="reg", state=None)

    dp.register_message_handler(handler_new_member, content_types=types.ContentType.NEW_CHAT_MEMBERS)

    dp.register_message_handler(user_unsub_delete_messages_from_chats, content_types=types.ContentType.LEFT_CHAT_MEMBER)

    dp.register_message_handler(delete_word_in_chat,
                                chat_type=[types.ChatType.GROUP, types.ChatType.SUPERGROUP],
                                commands=None, state=None)
