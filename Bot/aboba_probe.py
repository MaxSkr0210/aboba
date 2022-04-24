import wikipedia
import logging
from pathlib import Path
import speech_recognition as speech_recog
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
import pymongo
import enchant
from pymongo import MongoClient
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "5167446576:AAE2mSCcMiIGItHVw89WTbZAPxJOmNtYN8A"
PATH_TO_FILES = "C:\\Users\\ily02\\Desktop\\ABOBA\\"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.DEBUG)
wikipedia.set_lang("ru")

client = MongoClient("mongodb+srv://Aboba:aboba777@cluster0.ts9bv.mongodb.net/dictionary?retryWrites=true&w=majority")
db = client.dictionary

language_english = KeyboardButton('Перевод с Английского!🏴󠁧󠁢󠁥󠁮󠁧󠁿󠁧󠁢')
language_russian = KeyboardButton('Перевод с Русского!🇷🇺')
language_latin = KeyboardButton('Перевод с Латыни!❤️')
frazadnya = KeyboardButton('Фраза дня 🧐')
language_key = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
language_key.add(language_russian)
language_key.add(language_english)
language_key.add(language_latin)
language_key.add(frazadnya)

class Mydialog(StatesGroup):
    otvet = State()
    latin = State()
    english = State()


def log(message):
    print("------")
    #current_date = datetime.datetime.today()
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

@dp.message_handler(content_types=['voice'])
async def voice_message_handler(msg: types.Message):
    voice = await msg.voice.get_file()
    await handle_file(file=voice, file_name=f"{voice.file_id}.ogg", path=PATH_TO_FILES + "\\voices\\")

@dp.message_handler(content_types=['text'])
async def process_find_command(msg: types.Message):
        if (msg.text == 'Перевод с Латыни!❤️'):
            await Mydialog.otvet.set()
            user_message = await msg.answer("Введите, пожалуйста, текст для перевода")
        elif(msg.text == 'Перевод с Русского!🇷🇺'):
            await Mydialog.latin.set()
            user_message = await msg.answer("Введите, пожалуйста, текст для перевода")
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


@dp.message_handler(state=Mydialog.otvet)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answear = client.dictionary.latinTest.find_one({'word': message.text })
        if (answear == None):
            await message.reply("Слово не найдено")
        else:
            await message.reply("Перевод на русский: " + answear["translate"], reply_markup=language_key)
            await message.reply(getwiki(answear["translate"]), reply_markup=language_key)
        log(message)
    await state.finish()

@dp.message_handler(state=Mydialog.latin)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answear = client.dictionary.latinTest.find_one({'translate': message.text})

        if (answear == None):
            await message.reply("Слово не найдено")
        else:
            await message.reply("Перевод на латынь: " + answear["word"], reply_markup=language_key)
            await message.answer(getwiki(message.text))
        log(message)
    await state.finish()

@dp.message_handler(state=Mydialog.english)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        answear = client.dictionary.latinTest.find_one({'translate': message.text})

        if (answear == None):
            await message.reply("Слово не найдено")
        else:
            await message.reply("Перевод на латынь: " + answear["word"], reply_markup=language_key)
            await message.answer(getwiki(message.text))
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
