# -*- coding:utf -8 -*-
import json
import os
from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import CantParseEntities, CantInitiateConversation

from create_bot import bot
from keyboard import admin_kb

cb_chats = CallbackData('post', 'msg_text')
cb_texts = CallbackData('post', 'msg_text')
cb_channels = CallbackData('post', 'msg_text')


class FSMAdmin(StatesGroup):
    begin_state = State()
    chapter_words_state = State()
    add_ban_word_state = State()
    delete_ban_word_state = State()
    chapter_links_state = State()
    add_link_state_state = State()
    delete_link_state_state = State()
    chapter_bans_state = State()
    change_option_for_ban_state = State()
    add_time_to_ban_state = State()
    reduce_time_to_ban_state = State()
    chapter_hashtag_state = State()
    chapter_hashtag_without_photo_state = State()
    add_hashtag_without_photo_state = State()
    delete_hashtag_without_photo_state = State()
    chapter_hashtag_with_photo_state = State()
    add_hashtag_with_photo_state = State()
    delete_hashtag_with_photo_state = State()
    chapter_texts_state = State()
    text_viewing_state = State()
    text_change_state = State()
    text_change_begin_state = State()
    chapter_subscription_state = State()
    add_link_subscription_state = State()
    delete_link_subscription_state = State()
    chapter_rules_state = State()
    add_change_link_rules_chat_state = State()


path_json_for_bot_texts = os.getcwd() + "/" + "json/option_for_bot/texts.json"
path_for_chats_options = os.getcwd() + "/" + "json/chats/options/"
path_for_admins_options = os.getcwd() + "/" + "json/admins/options/"
path_for_people_chats = os.getcwd() + "/" + "json/people/chats/"
link_begin_str = "https://t.me/"


async def option_in_bot_after_add_chat(message: types.Message):
    global path_for_chats_options, path_for_people_chats
    path_to_chats_options_this_chat = path_for_chats_options + str(message.chat.id) + "/options.json"
    path_for_people_current_chat = path_for_people_chats + str(message.chat.id)
    name_chat = str(message.chat.title)
    try:
        with open(path_to_chats_options_this_chat, 'r', encoding='cp1251') as file:
            array_chats = json.load(file)
        for item in array_chats:
            if item["name"] == name_chat:
                return True
    except FileNotFoundError:
        try:
            os.mkdir(path_for_chats_options + str(message.chat.id))
        except FileExistsError:
            pass
        try:
            os.mkdir(path_for_people_current_chat)
        except FileExistsError:
            pass
        array_chats = []
        with open(path_to_chats_options_this_chat, 'w', encoding='cp1251') as file:
            options_for_chat_add = {"id": message.chat.id, "name": name_chat, "words_ban": [], "allowed_links": [],
                                    "humans_ban": [], "allow_hashtag_with_photo": [],
                                    "allow_hashtag_without_photo": [],
                                    "need_channels_subscription": [],
                                    "admins": ["albaufa", "tamerlan_elladov"],
                                    "link_to_rules": ""
                                    }
            array_chats.append(options_for_chat_add)
            json.dump(array_chats, file, ensure_ascii=False)
        return False


async def check_user_for_admin(message_from_user_username: str, message_chat_id: str):
    global path_for_chats_options
    path_to_chats_options_this_chat = path_for_chats_options + message_chat_id + "/options.json"
    with open(path_to_chats_options_this_chat, 'r', encoding='cp1251') as file:
        option_chat = json.load(file)
    username_in_message = message_from_user_username.replace(' ', '')
    for item in option_chat:
        for admin_in_chat in item["admins"]:
            if admin_in_chat == username_in_message:
                return True
    return False


async def command_start_type_message(message: types.Message):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_start(answer_kb)
    await bot.send_message(message.from_user.id, 'Выбирайте чат', reply_markup=answer_kb)


async def command_start_if_back(callback: types.CallbackQuery):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_start(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выбирайте чат', reply_markup=answer_kb)


async def cansel_handler_callback(callback: types.CallbackQuery, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await callback.answer("Возврат в начальное меню")
    await command_start_if_back(callback)


async def cansel_handler_message(message: types.Message, state: FSMContext):
    if state is None:
        return
    await state.finish()
    await command_start_type_message(message)


"""

async def default_message_handler(message: types.Message, state: FSMContext):
    pass
    
"""


async def chose_chat(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    chat_name_button_text = callback_data['msg_text']
    for filename in os.listdir(path_for_chats_options):
        with open(os.path.join(path_for_chats_options, filename) + "/options.json", 'r', encoding='cp1251') as file:
            option_for_chat = json.load(file)
        for item in option_for_chat:
            if item["name"] == chat_name_button_text:
                if await check_user_for_admin(str(callback.from_user.username), str(item["id"])):
                    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
                    with open(path_for_current_admin_options, 'w', encoding='cp1251') as file:
                        current_admin_option = {"admin_id": callback.from_user.id, "chat_option_id": item["id"],
                                                "current_user_change_ban": "", "current_user_change_ban_id": 0,
                                                "current_page_to_texts": 0, "current_value_for_key_texts": ""}
                        json.dump(current_admin_option, file, ensure_ascii=False)
                    answer_kb = InlineKeyboardMarkup()
                    answer_kb = await admin_kb.answer_after_choose_chat(answer_kb)
                    await bot.send_message(callback.from_user.id, 'Выберите раздел', reply_markup=answer_kb)
                    await callback.answer()
                    await FSMAdmin.begin_state.set()
                    return
    await callback.answer("У вас нет доступа")
    await cansel_handler_callback(callback, state)


async def answer_chapter_rules(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_rules(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_rules_state.set()


async def check_link_rules_chat(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            await bot.send_message(callback.from_user.id, "Текущая ссылка:\n" + item["link_to_rules"])
            await cansel_handler_callback(callback, state)
            await callback.answer()
            break
    await callback.answer()


async def change_link_rules_chat_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id,
                           "Отправьте ссылку на сообщение из чата, чтобы кнопка ссылалась на него")
    await FSMAdmin.add_change_link_rules_chat_state.set()
    await callback.answer()


async def change_link_rules_chat_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    new_link_rules_chat = message.text
    new_link_rules_chat.replace(' ', '')
    new_link_rules_chat = new_link_rules_chat.lower()
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            item["link_to_rules"] = new_link_rules_chat
            with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                json.dump(option_for_chat, file, ensure_ascii=False)
            await bot.send_message(message.from_user.id, "Ссылка на правила чата обновлена")
            await cansel_handler_message(message, state)
            return


async def answer_chapter_subscription(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_subscription(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_subscription_state.set()


async def answer_list_subscription(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if len(item["need_channels_subscription"]) < 1:
            await bot.send_message(callback.from_user.id, "Ссылок нет")
            await cansel_handler_callback(callback, state)
            await callback.answer()
        else:
            list_channels_str = ""
            for channel in item["need_channels_subscription"]:
                list_channels_str += str(channel) + "\n"
            await bot.send_message(callback.from_user.id, "Ссылки для подписки:\n" + list_channels_str)
            await cansel_handler_callback(callback, state)
            await callback.answer()
            break
    await callback.answer()


async def add_link_subscription_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id,
                           "Пришлите ссылку на канал, который добавляем для подписки, пример:\nhttps://t.me/marketplaceone")
    await FSMAdmin.add_link_subscription_state.set()
    await callback.answer()


async def add_link_subscription_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    new_ban_word = message.text
    new_ban_word.replace(' ', '')
    new_ban_word = new_ban_word.lower()
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        item["need_channels_subscription"].append(new_ban_word)
        with open(path_current_chat_options, 'w', encoding='cp1251') as file:
            json.dump(option_for_chat, file, ensure_ascii=False)
        await bot.send_message(message.from_user.id, "Данный канал добавлен в подписки")
        await cansel_handler_message(message, state)
        return


async def delete_link_subscription_begin(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_delete_subscription(answer_kb, current_admin_option["chat_option_id"])
    await bot.send_message(callback.from_user.id, "Выберите канал, который нужно удалить ниже", reply_markup=answer_kb)
    await FSMAdmin.delete_link_subscription_state.set()
    await callback.answer()


async def delete_link_subscription_end(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    global path_for_admins_options, link_begin_str
    channel = link_begin_str + str(callback_data['msg_text'])
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        item["need_channels_subscription"].remove(channel)
        with open(path_current_chat_options, 'w', encoding='cp1251') as file:
            json.dump(option_for_chat, file, ensure_ascii=False)
        await bot.send_message(callback.from_user.id, "Данный канал удален из подписок")
        await cansel_handler_callback(callback, state)
        await callback.answer()
        return


async def answer_chapter_texts(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_texts(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_texts_state.set()


async def answer_viewing_text(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options
    answer_kb = InlineKeyboardMarkup()
    if callback.data == "kb_admin_change_send_texts":
        await FSMAdmin.text_change_state.set()
    else:
        await FSMAdmin.text_viewing_state.set()
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_options = json.load(file)
    answer_kb = await admin_kb.answer_viewing_text(answer_kb, current_admin_options["current_page_to_texts"])
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()


async def answer_next_viewing_text(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options
    answer_kb = InlineKeyboardMarkup()
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_options = json.load(file)
    current_admin_options["current_page_to_texts"] += 1
    with open(path_for_current_admin_options, 'w', encoding='cp1251') as file:
        json.dump(current_admin_options, file, ensure_ascii=False)
    answer_kb = await admin_kb.answer_viewing_text(answer_kb, current_admin_options["current_page_to_texts"])
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()


async def answer_back_viewing_text(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options
    answer_kb = InlineKeyboardMarkup()
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_options = json.load(file)
    current_admin_options["current_page_to_texts"] -= 1
    with open(path_for_current_admin_options, 'w', encoding='cp1251') as file:
        json.dump(current_admin_options, file, ensure_ascii=False)
    answer_kb = await admin_kb.answer_viewing_text(answer_kb, current_admin_options["current_page_to_texts"])
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()


async def answer_viewing_chose_text(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    global path_json_for_bot_texts
    with open(path_json_for_bot_texts, 'r', encoding='cp1251') as file:
        current_texts_for_bot = json.load(file)
    value_for_key_texts = callback_data['msg_text']
    answer = str(current_texts_for_bot[value_for_key_texts])
    try:
        await bot.send_message(callback.from_user.id, answer, parse_mode="Markdown")
    except CantParseEntities:
        await bot.send_message(callback.from_user.id, answer)
    except CantInitiateConversation:
        await bot.send_message(callback.from_user.id, answer)
    await callback.answer()
    await cansel_handler_callback(callback, state)


async def answer_change_chose_text_begin(callback: types.CallbackQuery, callback_data: dict, state: FSMContext):
    global path_for_admins_options
    value_for_key_texts = callback_data['msg_text']
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_options = json.load(file)
    current_admin_options["current_value_for_key_texts"] = value_for_key_texts
    with open(path_for_current_admin_options, 'w', encoding='cp1251') as file:
        json.dump(current_admin_options, file, ensure_ascii=False)
    await FSMAdmin.text_change_begin_state.set()
    await bot.send_message(callback.from_user.id, "Введите новый текст:")
    await callback.answer()


async def answer_change_chose_text_end(message: types.Message, state: FSMContext):
    global path_json_for_bot_texts, path_for_admins_options
    new_text = message.text
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_options = json.load(file)
    with open(path_json_for_bot_texts, 'r', encoding='cp1251') as file:
        current_texts_for_bot = json.load(file)
    current_texts_for_bot[current_admin_options["current_value_for_key_texts"]] = new_text
    with open(path_json_for_bot_texts, 'w', encoding='cp1251') as file:
        json.dump(current_texts_for_bot, file, ensure_ascii=False)
    await bot.send_message(message.from_user.id, "Текст изменен")
    await cansel_handler_message(message, state)


async def answer_chapter_words(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_words(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_words_state.set()


async def answer_chapter_links(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_links(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_links_state.set()


async def answer_chapter_bans(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_bans(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_bans_state.set()


async def answer_chapter_hashtags(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_hashtags(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_hashtag_state.set()


async def answer_chapter_hashtags_without_photo(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_hashtags_without_photo(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_hashtag_without_photo_state.set()


async def answer_chapter_hashtags_with_photo(callback: types.CallbackQuery, state: FSMContext):
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_chapter_hashtags_with_photo(answer_kb)
    await bot.send_message(callback.from_user.id, 'Выберите опцию', reply_markup=answer_kb)
    await callback.answer()
    await FSMAdmin.chapter_hashtag_with_photo_state.set()


async def list_ban_words(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            await bot.send_message(callback.from_user.id, "Запрещенные слова: " + str(item["words_ban"]))
            await cansel_handler_callback(callback, state)
            await callback.answer()
            break
    await callback.answer()


async def add_ban_word_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите слово которое нужно добавить в запрещенное")
    await FSMAdmin.add_ban_word_state.set()
    await callback.answer()


async def add_ban_word_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    new_ban_word = message.text
    new_ban_word.replace(' ', '')
    new_ban_word = new_ban_word.lower()
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            item["words_ban"].append(new_ban_word)
            with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                json.dump(option_for_chat, file, ensure_ascii=False)
            await bot.send_message(message.from_user.id, "Данное слово добавлено в запрещенные")
            await cansel_handler_message(message, state)
            return


async def delete_ban_word_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите слово которое нужно удалить из запрещенных")
    await FSMAdmin.delete_ban_word_state.set()
    await callback.answer()


async def delete_ban_word_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    delete_ban_word = message.text
    delete_ban_word.replace(' ', '')
    delete_ban_word = delete_ban_word.lower()
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            for word in item["words_ban"]:
                if word == delete_ban_word:
                    item["words_ban"].remove(word)
                    with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                        json.dump(option_for_chat, file, ensure_ascii=False)
                    await bot.send_message(message.from_user.id, "Данное слово удаленно из запрещенных")
                    await cansel_handler_message(message, state)
                    return
    await bot.send_message(message.from_user.id, "Данного слова нет в списке")
    await cansel_handler_message(message, state)


async def list_allowed_links(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            await bot.send_message(callback.from_user.id, "Разрешенные ссылки: " + str(item["allowed_links"]))
            await cansel_handler_callback(callback, state)
            await callback.answer()
            return
    await callback.answer()
    await cansel_handler_callback(callback, state)


async def add_link_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите ссылку которую нужно разрешить, " +
                           "без www и прочего, к примеру ya.ru, google.com")
    await FSMAdmin.add_link_state_state.set()
    await callback.answer()


async def add_link_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    new_link = message.text
    new_link.replace(' ', '')
    new_link = new_link.lower()
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            item["allowed_links"].append(new_link)
            with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                json.dump(option_for_chat, file, ensure_ascii=False)
            await bot.send_message(message.from_user.id, "Ссылка разрешена")
            await cansel_handler_message(message, state)
            return
    await cansel_handler_message(message, state)


async def delete_link_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите ссылку, которую хотите убрать из разрешенных,"
                                                  " без www и прочего, к примеру ya.ru, google.com")
    await FSMAdmin.delete_link_state_state.set()
    await callback.answer()


async def delete_link_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    delete_link = message.text
    delete_link.replace(' ', '')
    delete_link = delete_link.lower()
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            for link in item["allowed_links"]:
                if link == delete_link:
                    item["allowed_links"].remove(link)
                    with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                        json.dump(option_for_chat, file, ensure_ascii=False)
                    await bot.send_message(message.from_user.id, "Ссылка удалена из разрешенных")
                    await cansel_handler_message(message, state)
                    return
    await bot.send_message(message.from_user.id, "Данной ссылки нет в списке")
    await cansel_handler_message(message, state)


async def list_allowed_hashtag_without_photo(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            await bot.send_message(callback.from_user.id, "Разрешенные хэштеги без фото: " +
                                   str(item["allow_hashtag_without_photo"]))
            await cansel_handler_callback(callback, state)
            await callback.answer()
            return
    await cansel_handler_callback(callback, state)
    await callback.answer()


async def add_hashtag_without_photo_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите хэштег (без фото) который хотите разрешить")
    await FSMAdmin.add_hashtag_without_photo_state.set()
    await callback.answer()


async def add_hashtag_without_photo_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    new_hashtag = message.text
    new_hashtag = new_hashtag.replace(' ', '')
    new_hashtag = new_hashtag.lower()
    new_hashtag = new_hashtag.replace('#', '')
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            item["allow_hashtag_without_photo"].append(new_hashtag)
            with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                json.dump(option_for_chat, file, ensure_ascii=False)
            await bot.send_message(message.from_user.id, "Хэштег добавлен")
            await cansel_handler_message(message, state)
            return
    await cansel_handler_message(message, state)


async def delete_hashtag_without_photo_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите хэштег (без фото), который хотите убрать из разрешенных")
    await FSMAdmin.delete_hashtag_without_photo_state.set()
    await callback.answer()


async def delete_hashtag_without_photo_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    delete_hashtag = message.text
    delete_hashtag = delete_hashtag.replace(' ', '')
    delete_hashtag = delete_hashtag.lower()
    delete_hashtag = delete_hashtag.replace('#', '')
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            for hashtag in item["allow_hashtag_without_photo"]:
                if hashtag == delete_hashtag:
                    item["allow_hashtag_without_photo"].remove(hashtag)
                    with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                        json.dump(option_for_chat, file, ensure_ascii=False)
                    await bot.send_message(message.from_user.id, "Хэштег удален из разрешенных")
                    await cansel_handler_message(message, state)
                    return
    await bot.send_message(message.from_user.id, "Данного хештега нет в списке")
    await cansel_handler_message(message, state)


async def list_allowed_hashtag_with_photo(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            await bot.send_message(callback.from_user.id, "Разрешенные хэштеги без фото: " +
                                   str(item["allow_hashtag_with_photo"]))
            await cansel_handler_callback(callback, state)
            await callback.answer()
            return
    await cansel_handler_callback(callback, state)
    await callback.answer()


async def add_hashtag_with_photo_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите хэштег (для фото) который хотите разрешить")
    await FSMAdmin.add_hashtag_with_photo_state.set()
    await callback.answer()


async def add_hashtag_with_photo_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    new_hashtag = message.text
    new_hashtag = new_hashtag.replace(' ', '')
    new_hashtag = new_hashtag.lower()
    new_hashtag = new_hashtag.replace('#', '')
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            item["allow_hashtag_with_photo"].append(new_hashtag)
            with open(path_current_chat_options, 'w', encoding='cp1251') as file:
                json.dump(option_for_chat, file, ensure_ascii=False)
            await bot.send_message(message.from_user.id, "Хэштег добавлен")
            await cansel_handler_message(message, state)
            return
    await cansel_handler_message(message, state)


async def delete_hashtag_with_photo_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите хэштег (для фото), который хотите убрать из разрешенных")
    await FSMAdmin.delete_hashtag_with_photo_state.set()
    await callback.answer()


async def delete_hashtag_with_photo_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    delete_hashtag = message.text
    delete_hashtag = delete_hashtag.replace(' ', '')
    delete_hashtag = delete_hashtag.lower()
    delete_hashtag = delete_hashtag.replace('#', '')
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            for hashtag in item["allow_hashtag_with_photo"]:
                if hashtag == delete_hashtag:
                    item["allow_hashtag_with_photo"].remove(hashtag)
                    with open(path_current_chat_options, encoding='cp1251') as file:
                        json.dump(option_for_chat, file, ensure_ascii=False)
                    await bot.send_message(message.from_user.id, "Хэштег удален из разрешенных")
                    await cansel_handler_message(message, state)
                    return
    await bot.send_message(message.from_user.id, "Данного хештега нет в списке")
    await cansel_handler_message(message, state)


async def list_ban_users_in_chat(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options, path_for_people_chats
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        option_for_chat = json.load(file)
    for item in option_for_chat:
        if item["id"] == current_admin_option["chat_option_id"]:
            all_users_at_ban = ""
            for user in item["humans_ban"]:
                path_for_current_human_option = path_for_people_chats + str(item["id"])
                path_for_current_human_option += "/" + str(user["id_user"]) + ".json"
                with open(path_for_current_human_option, 'r', encoding='cp1251') as file:
                    current_human_option = json.load(file)
                time_to_ban_str = str(current_human_option["Time_to_ban_in_minutes"])
                all_users_at_ban += user["username"] + " на " + time_to_ban_str + "мин\n"
            await bot.send_message(callback.from_user.id, "Пользователи в бане: " + all_users_at_ban)
            await cansel_handler_callback(callback, state)
            await callback.answer()
            return
    await cansel_handler_callback(callback, state)
    await callback.answer()


async def change_time_to_ban_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите ник пользователя")
    await FSMAdmin.change_option_for_ban_state.set()
    await callback.answer()


async def change_time_to_ban_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    current_user_for_change_ban = message.text
    current_user_for_change_ban = current_user_for_change_ban.replace(' ', '')
    current_user_for_change_ban = current_user_for_change_ban.lower()
    current_user_for_change_ban = current_user_for_change_ban.replace('@', '')
    current_admin_option["current_user_change_ban"] = current_user_for_change_ban
    with open(path_for_current_admin_options, 'w', encoding='cp1251') as file:
        json.dump(current_admin_option, file, ensure_ascii=False)
    answer_kb = InlineKeyboardMarkup()
    answer_kb = await admin_kb.answer_choose_user_for_change_time_to_ban(answer_kb)
    await bot.send_message(message.from_user.id, 'Выберите опцию', reply_markup=answer_kb)


async def add_time_to_ban_user_begin_callback(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите сколько минут прибавить к текущему бану")
    await FSMAdmin.add_time_to_ban_state.set()
    await callback.answer()


async def add_time_to_ban_user_begin_message(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Напишите сколько минут прибавить к текущему бану")
    await FSMAdmin.add_time_to_ban_state.set()


async def add_time_to_ban_user_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options, path_for_people_chats
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    add_time_str = message.text
    add_time_str.replace(' ', '')
    add_time_int = 0
    try:
        add_time_int = int(add_time_str)
    except TypeError:
        await bot.send_message(message.from_user.id, "Введите целое число")
        await add_time_to_ban_user_begin_message(message, state)
        return
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        current_chat_option = json.load(file)
    for item in current_chat_option:
        if item["id"] == current_admin_option["chat_option_id"]:
            for human_ban_in_list in item["humans_ban"]:
                if human_ban_in_list["username"] == current_admin_option["current_user_change_ban"]:
                    path_for_current_human_option = path_for_people_chats + str(item["id"])
                    path_for_current_human_option += "/" + str(human_ban_in_list["id_user"]) + ".json"
                    with open(path_for_current_human_option, 'r', encoding='cp1251') as file:
                        current_human_option = json.load(file)
                    current_human_option["Time_to_ban_in_minutes"] += add_time_int
                    with open(path_for_current_human_option, 'w', encoding='cp1251') as file:
                        json.dump(current_human_option, file, ensure_ascii=False)
                    await bot.send_message(message.from_user.id, "Время обновлено")
                    await cansel_handler_message(message, state)
                    return
    await bot.send_message(message.from_user.id, "Пользователь не найден")
    await cansel_handler_message(message, state)


async def reduce_time_to_ban_user_begin(callback: types.CallbackQuery, state: FSMContext):
    await bot.send_message(callback.from_user.id, "Напишите сколько минут убрать из текущего бана")
    await FSMAdmin.reduce_time_to_ban_state.set()
    await callback.answer()


async def reduce_time_to_ban_user_end(message: types.Message, state: FSMContext):
    global path_for_admins_options, path_for_chats_options, path_for_people_chats
    path_for_current_admin_options = path_for_admins_options + str(message.from_user.id) + ".json"
    add_time_str = message.text
    add_time_str.replace(' ', '')
    add_time_int = 0
    try:
        add_time_int = int(add_time_str)
    except TypeError:
        print("error add_time_to_ban_user_end")
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        current_chat_option = json.load(file)
    for item in current_chat_option:
        if item["id"] == current_admin_option["chat_option_id"]:
            for human_ban_in_list in item["humans_ban"]:
                if human_ban_in_list["username"] == current_admin_option["current_user_change_ban"]:
                    path_for_current_human_option = path_for_people_chats + str(item["id"])
                    path_for_current_human_option += "/" + str(human_ban_in_list["id_user"]) + ".json"
                    with open(path_for_current_human_option, 'r', encoding='cp1251') as file:
                        current_human_option = json.load(file)
                    current_human_option["Time_to_ban_in_minutes"] -= add_time_int
                    with open(path_for_current_human_option, 'w', encoding='cp1251') as file:
                        json.dump(current_human_option, file, ensure_ascii=False)
                    await bot.send_message(message.from_user.id, "Время обновлено")
                    await cansel_handler_message(message, state)
                    return
    await bot.send_message(message.from_user.id, "Пользователь не найден")
    await cansel_handler_message(message, state)


async def drop_ban_user(callback: types.CallbackQuery, state: FSMContext):
    global path_for_admins_options, path_for_chats_options, path_for_people_chats
    path_for_current_admin_options = path_for_admins_options + str(callback.from_user.id) + ".json"
    with open(path_for_current_admin_options, 'r', encoding='cp1251') as file:
        current_admin_option = json.load(file)
    path_current_chat_options = path_for_chats_options + str(current_admin_option["chat_option_id"]) + "/options.json"
    with open(path_current_chat_options, 'r', encoding='cp1251') as file:
        current_chat_option = json.load(file)
    for item in current_chat_option:
        if item["id"] == current_admin_option["chat_option_id"]:
            for human_ban_in_list in item["humans_ban"]:
                if human_ban_in_list["username"] == current_admin_option["current_user_change_ban"]:
                    path_for_current_human_option = path_for_people_chats + str(item["id"])
                    path_for_current_human_option += "/" + str(human_ban_in_list["id_user"]) + ".json"
                    with open(path_for_current_human_option, 'r', encoding='cp1251') as file:
                        current_human_option = json.load(file)
                    current_human_option["Time_to_ban_in_minutes"] = 0
                    with open(path_for_current_human_option, 'w', encoding='cp1251') as file:
                        json.dump(current_human_option, file, ensure_ascii=False)
                    await bot.send_message(callback.from_user.id, "Пользователь больше не в бане")
                    await cansel_handler_callback(callback, state)
                    await callback.answer()
                    return
    await callback.answer("Пользователь не найден")
    await cansel_handler_callback(callback, state)


def register_handlers_client(dp: Dispatcher):
    dp.register_callback_query_handler(cansel_handler_callback, chat_type=types.ChatType.PRIVATE, text='cansel',
                                       state="*")

    dp.register_message_handler(command_start_type_message, chat_type=types.ChatType.PRIVATE, commands='start')

    dp.register_callback_query_handler(chose_chat, cb_chats.filter(), chat_type=types.ChatType.PRIVATE, state=None)

    # Начальное меню

    dp.register_callback_query_handler(answer_chapter_words, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_words',
                                       state=FSMAdmin.begin_state)

    dp.register_callback_query_handler(answer_chapter_links, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_links',
                                       state=FSMAdmin.begin_state)

    dp.register_callback_query_handler(answer_chapter_bans, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_bans',
                                       state=FSMAdmin.begin_state)

    dp.register_callback_query_handler(answer_chapter_hashtags, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_hashtags',
                                       state=FSMAdmin.begin_state)

    dp.register_callback_query_handler(answer_chapter_texts, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_texts',
                                       state=FSMAdmin.begin_state)

    dp.register_callback_query_handler(answer_chapter_subscription, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_subscription',
                                       state=FSMAdmin.begin_state)

    dp.register_callback_query_handler(answer_chapter_rules, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_rules',
                                       state=FSMAdmin.begin_state)

    # Работа с ссылкой на правила чата

    dp.register_callback_query_handler(check_link_rules_chat, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_check_link_rules_chat',
                                       state=FSMAdmin.chapter_rules_state)

    dp.register_callback_query_handler(change_link_rules_chat_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_change_link_rules_chat', state=FSMAdmin.chapter_rules_state)

    dp.register_message_handler(change_link_rules_chat_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_change_link_rules_chat_state)

    # Работа с подписками

    dp.register_callback_query_handler(answer_list_subscription, chat_type=types.ChatType.PRIVATE,
                                       text="kb_admin_list_links_subscription",
                                       state=FSMAdmin.chapter_subscription_state)

    dp.register_callback_query_handler(add_link_subscription_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_add_link_subscription', state=FSMAdmin.chapter_subscription_state)

    dp.register_message_handler(add_link_subscription_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_link_subscription_state)

    dp.register_callback_query_handler(delete_link_subscription_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_delete_link_subscription',
                                       state=FSMAdmin.chapter_subscription_state)

    dp.register_callback_query_handler(delete_link_subscription_end, cb_channels.filter(),
                                       chat_type=types.ChatType.PRIVATE,
                                       state=FSMAdmin.delete_link_subscription_state)

    # Работа с текстом ответа от бота

    dp.register_callback_query_handler(answer_viewing_text, chat_type=types.ChatType.PRIVATE,
                                       text=['kb_admin_viewing_send_texts', "kb_admin_change_send_texts"],
                                       state=FSMAdmin.chapter_texts_state)

    dp.register_callback_query_handler(answer_next_viewing_text, chat_type=types.ChatType.PRIVATE,
                                       text='next_viewing_text',
                                       state=[FSMAdmin.text_viewing_state, FSMAdmin.text_change_state])

    dp.register_callback_query_handler(answer_back_viewing_text, chat_type=types.ChatType.PRIVATE,
                                       text='back_viewing_text',
                                       state=[FSMAdmin.text_viewing_state, FSMAdmin.text_change_state])

    dp.register_callback_query_handler(answer_viewing_chose_text, cb_texts.filter(), chat_type=types.ChatType.PRIVATE,
                                       state=FSMAdmin.text_viewing_state)

    dp.register_callback_query_handler(answer_change_chose_text_begin, cb_texts.filter(),
                                       chat_type=types.ChatType.PRIVATE,
                                       state=FSMAdmin.text_change_state)

    dp.register_message_handler(answer_change_chose_text_end, chat_type=types.ChatType.PRIVATE,
                                state=FSMAdmin.text_change_begin_state, commands=None)

    # Запрещенные слова

    dp.register_callback_query_handler(list_ban_words, chat_type=types.ChatType.PRIVATE, text='kb_admin_list_ban_words',
                                       state=FSMAdmin.chapter_words_state)

    dp.register_callback_query_handler(add_ban_word_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_add_ban_word', state=FSMAdmin.chapter_words_state)

    dp.register_message_handler(add_ban_word_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_ban_word_state)

    dp.register_callback_query_handler(delete_ban_word_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_delete_ban_word', state=FSMAdmin.chapter_words_state)

    dp.register_message_handler(delete_ban_word_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.delete_ban_word_state)
    # Разрешенные ссылки
    dp.register_callback_query_handler(list_allowed_links, chat_type=types.ChatType.PRIVATE, text='kb_admin_list_links',
                                       state=FSMAdmin.chapter_links_state)

    dp.register_callback_query_handler(add_link_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_add_link', state=FSMAdmin.chapter_links_state)

    dp.register_message_handler(add_link_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_link_state_state)

    dp.register_callback_query_handler(delete_link_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_delete_link', state=FSMAdmin.chapter_links_state)

    dp.register_message_handler(delete_link_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.delete_link_state_state)

    # Доп меню хештегов
    dp.register_callback_query_handler(answer_chapter_hashtags_without_photo, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_hashtags_without_photo',
                                       state=FSMAdmin.chapter_hashtag_state)

    dp.register_callback_query_handler(answer_chapter_hashtags_with_photo, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_menu_hashtags_with_photo',
                                       state=FSMAdmin.chapter_hashtag_state)
    # Разрешенные хештеги с фото

    dp.register_callback_query_handler(list_allowed_hashtag_with_photo, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_list_hashtag_with_photo',
                                       state=FSMAdmin.chapter_hashtag_with_photo_state)

    dp.register_callback_query_handler(add_hashtag_with_photo_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_add_hashtag_with_photo',
                                       state=FSMAdmin.chapter_hashtag_with_photo_state)

    dp.register_message_handler(add_hashtag_with_photo_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_hashtag_with_photo_state)

    dp.register_callback_query_handler(delete_hashtag_with_photo_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_remove_hashtag_with_photo',
                                       state=FSMAdmin.chapter_hashtag_with_photo_state)

    dp.register_message_handler(delete_hashtag_with_photo_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.delete_hashtag_with_photo_state)

    # Разрешенные хештеги без фото

    dp.register_callback_query_handler(list_allowed_hashtag_without_photo, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_list_hashtag_without_photo',
                                       state=FSMAdmin.chapter_hashtag_without_photo_state)

    dp.register_callback_query_handler(add_hashtag_without_photo_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_add_hashtag_without_photo',
                                       state=FSMAdmin.chapter_hashtag_without_photo_state)

    dp.register_message_handler(add_hashtag_without_photo_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_hashtag_without_photo_state)

    dp.register_callback_query_handler(delete_hashtag_without_photo_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_remove_hashtag_without_photo',
                                       state=FSMAdmin.chapter_hashtag_without_photo_state)

    dp.register_message_handler(delete_hashtag_without_photo_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.delete_hashtag_without_photo_state)

    # бан

    dp.register_callback_query_handler(list_ban_users_in_chat, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_list_time_to_ban_human',
                                       state=FSMAdmin.chapter_bans_state)
    dp.register_callback_query_handler(change_time_to_ban_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_change_time_to_ban_human', state=FSMAdmin.chapter_bans_state)
    dp.register_message_handler(change_time_to_ban_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.change_option_for_ban_state)

    dp.register_callback_query_handler(add_time_to_ban_user_begin_callback, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_add_time_to_ban', state=FSMAdmin.change_option_for_ban_state)
    dp.register_message_handler(add_time_to_ban_user_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.add_time_to_ban_state)

    dp.register_callback_query_handler(reduce_time_to_ban_user_begin, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_reduce_time_to_ban', state=FSMAdmin.change_option_for_ban_state)
    dp.register_message_handler(reduce_time_to_ban_user_end, chat_type=types.ChatType.PRIVATE, commands=None,
                                state=FSMAdmin.reduce_time_to_ban_state)

    dp.register_callback_query_handler(drop_ban_user, chat_type=types.ChatType.PRIVATE,
                                       text='kb_admin_unban', state=FSMAdmin.change_option_for_ban_state)

    # пустой ввод

    # dp.register_message_handler(default_message_handler, chat_type=types.ChatType.PRIVATE, commands=None, state=None)
