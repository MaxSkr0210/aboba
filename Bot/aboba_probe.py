import wikipedia
import logging
import re
from pathlib import Path
import speech_recognition as speech_recog
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
import pymongo
import enchant
from translate import Translator
from pymongo import MongoClient
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "5376194597:AAGAP5Th807HYN_Pldg4L7ad6A308OvVJDc"
PATH_TO_FILES = "C:\\Users\\ily02\\Desktop\\ABOBA\\"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
wikipedia.set_lang("ru")

client = MongoClient("mongodb+srv://Aboba:aboba777@cluster0.ts9bv.mongodb.net/dictionary?retryWrites=true&w=majority")
db = client.dictionary

language_english = KeyboardButton('🏴󠁧󠁢󠁥󠁮󠁧󠁿 -> 󠁧󠁢󠁥󠁮󠁧󠁿󠁧󠁢🇷🇺')
language_russian = KeyboardButton('🇷🇺 -> 🏴󠁧󠁢󠁥󠁮󠁧󠁿')
language_latin = KeyboardButton('Латынь -> 🇷🇺')
latin_to_russian = KeyboardButton('🇷🇺 -> Латынь')
frazadnya = KeyboardButton('Фраза дня 🧐')
language_key = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
language_key.add(language_russian)
language_key.add(language_english)
language_key.add(language_latin)
language_key.add(latin_to_russian)
language_key.add(frazadnya)


class Mydialog(StatesGroup):
    otvet = State()
    latin = State()
    english_to_russian = State()
    russian_to_english = State()

def my_dist(a, b):
    def recursive(i, j):
        if i == 0 or j == 0:
            # если одна из строк пустая, то расстояние до другой строки - ее длина
            # т.е. n вставок
            return max(i, j)
        elif a[i - 1] == b[j - 1]:
            # если оба последних символов одинаковые, то съедаем их оба, не меняя расстояние
            return recursive(i - 1, j - 1)
        else:
            # иначе выбираем минимальный вариант из трех
            return 1 + min(
                recursive(i, j - 1),  # удаление
                recursive(i - 1, j),   # вставка
                recursive(i - 1, j - 1)  # замена
            )
    return recursive(len(a), len(b))




def log(message):
    print("------")
    # current_date = datetime.datetime.today()
    current_date = 10
    print(current_date)

    if message.from_user.last_name is None:
        print("Сообщение от {0} (id = {1}) \n Текст сообщения:{2}".format(message.from_user.first_name,
                                                                          str(message.from_user.id), message.text))
    else:
        print("Сообщение от {0} {1} (id = {2}) \n Текст сообщения:{3}".format(message.from_user.first_name,
                                                                              message.from_user.last_name,
                                                                              str(message.from_user.id), message.text))


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await msg.answer("Привет! Я бот-словарь, венец творения ABOBA Inc.\n", reply_markup=language_key)
    log(msg)


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    await msg.answer(f'Как пользоваться? \n')
    log(msg)


async def handle_file(file: str, file_name: str, path: str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)

    await bot.download_file(file_path=file.file_path, destination=f"{path}/{file_name}")

#

@dp.message_handler(content_types=['voice'])
async def voice_message_handler(msg: types.Message):
    voice = await msg.voice.get_file()
    await handle_file(file=voice, file_name=f"{voice.file_id}.ogg", path=PATH_TO_FILES + "\\voices\\")


@dp.message_handler(content_types=['text'])
async def process_find_command(msg: types.Message):
    if msg.text == 'Латынь -> 🇷🇺':
        await Mydialog.otvet.set()
        await msg.answer("Введите, пожалуйста, текст для перевода")
    elif msg.text == '🇷🇺 -> Латынь':
        await Mydialog.latin.set()
        await msg.answer("Введите, пожалуйста, текст для перевода")
    elif msg.text == '🏴󠁧󠁢󠁥󠁮󠁧󠁿 -> 󠁧󠁢󠁥󠁮󠁧󠁿󠁧󠁢🇷🇺':
        await Mydialog.english_to_russian.set()
        await msg.answer("Введите, пожалуйста, текст для перевода")
    elif msg.text == '🇷🇺 -> 🏴󠁧󠁢󠁥󠁮󠁧󠁿':
        await Mydialog.russian_to_english.set()
        await msg.answer("Введите, пожалуйста, текст для перевода")
    else:
        await msg.answer("Command not found")
    log(msg)


@dp.message_handler(commands=['find'])
async def process_find_command(msg: types.Message):
    await Mydialog.otvet.set()
    user_message = await msg.answer("Введите, пожалуйста, текст для поиска в википедии")
    answear = client.dictionary.latinTest.find_one({'translate', f'{user_message}'})
    await msg.answer(answear)
    log(msg)

aboba_list = []
mydict = {}
# С русского на латынь
@dp.message_handler(state=Mydialog.otvet)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy():
        answear = client.dictionary.latinTest.find({'word': message.text})
        min = 0
        for i in answear:
            min = my_dist(i["word"], message.text)
            mydict[min] = i

        #log(answear)
        if answear == None:
            regx = re.compile(message.text[0] + r"\w*" + message.text[len(message.text) - 1], re.IGNORECASE)
            answear = client.dictionary.latinTest.find({'word': regx})
            print(regx)
            min = 0
            for i in answear:
                min = my_dist(i["word"], message.text)
                mydict[min] = i
            await message.reply(mydict[min])
        else:
            await message.reply("Перевод на русский: " + mydict[min]["translate"], reply_markup=language_key)
            await message.reply(getwiki(answear["translate"]), reply_markup=language_key)
        log(message)
    await state.finish()


# Перевод на латынь
@dp.message_handler(state=Mydialog.latin)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy():
        answear = client.dictionary.latinTest.find_one({'translate': message.text})

        if (answear == None):
            await message.reply("Слово не найдено")
        else:
            await message.reply("Перевод на латынь: " + answear["word"], reply_markup=language_key)
            await message.answer(getwiki(message.text))
        log(message)
    await state.finish()


# С англиского на русский
@dp.message_handler(state=Mydialog.english_to_russian)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy():
        answear = client.dictionary.English.find_one({'word': message.text})

        if (answear == None):
            await message.reply("Слово не найдено")
        else:
            await message.reply("Перевод на английский: " + answear["translate"], reply_markup=language_key)
        log(message)
    await state.finish()


# с русского на английский
@dp.message_handler(state=Mydialog.russian_to_english)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy():
        answear = client.dictionary.English.find_one({'translate': message.text})

        if (answear == None):
            await message.reply("Слово не найдено")
        else:
            await message.reply("Перевод на на английский: " + answear["word"], reply_markup=language_key)
        log(message)
    await state.finish()


def getwiki(s):
    try:
        ny = wikipedia.page(s)
        wikitext = ny.content[:1000]
        wikimas = wikitext.split('.')
        wikimas = wikimas[:-1]
        wikitext2 = ''
        for x in wikimas:
            if not ('==' in x):
                if len((x.strip())) > 3:
                    wikitext2 = wikitext2 + x + '.'
            else:
                break
        return wikitext2
    except Exception as e:
        return 'В энциклопедии нет информации об этом'


if __name__ == "__main__":
    executor.start_polling(dp)
