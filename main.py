import requests
import xml.etree.ElementTree as ET
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
from aiogram import F
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

# Токен вашего бота (получите его у @BotFather)
BOT_TOKEN = "7942383998:AAG-ltaXmaVbtYdQAXknlwEFW42Dt1gDjqM"

# URL Центробанка РФ для получения курсов валют
CBR_URL = "https://www.cbr.ru/scripts/XML_daily.asp"

# Создаем Bot и Dispatcher
bot = Bot(BOT_TOKEN)
dp = Dispatcher()

# Функция для получения данных о курсе валют
def get_currency_data():
    response = requests.get(CBR_URL)
    if response.status_code != 200:
        return {"error": "Ошибка при подключении к Центробанку"}

    # Парсим XML-документ
    tree = ET.ElementTree(ET.fromstring(response.content))
    root = tree.getroot()

    # Словарь для хранения данных
    currencies = {}
    for currency in root.findall("Valute"):
        char_code = currency.find("CharCode").text
        name = currency.find("Name").text
        value = currency.find("Value").text.replace(",", ".")
        currencies[char_code] = {"name": name, "value": float(value)}

    return currencies


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.reply(
        "Привет! Я бот для получения курсов валют Центробанка РФ.\n"
        "Введите команду /rates, чтобы узнать текущие курсы валют."
    )


# Команда /rates — выводит список валют с курсами в виде кнопок
@dp.message(Command("rates"))
async def rates_command(message: Message):
    data = get_currency_data()
    if "error" in data:  # Если произошла ошибка
        await message.reply(data["error"])
        return

    # Создаем кнопки для каждой валюты
    keyboard = InlineKeyboardBuilder()
    for char_code, info in data.items():
        button = InlineKeyboardButton(
            text=f"{char_code} ({info['name']})",
            callback_data=char_code  # Передаем код валюты как callback_data
        )
        keyboard.add(button)

    await message.reply("Выберите валюту из списка ниже:", reply_markup=keyboard.as_markup())


# Обработчик нажатий на кнопки inline
@dp.callback_query()
async def handle_currency_callback(callback: CallbackQuery):
    data = get_currency_data()
    if "error" in data:
        await callback.message.reply(data["error"])
        return

    char_code = callback.data  # Получаем код валюты из callback_data

    if char_code in data:  # Если валюта есть в данных
        currency_info = data[char_code]
        await callback.message.reply(
            f"Курс {currency_info['name']} ({char_code}) составляет {currency_info['value']} руб."
        )
    else:  # Если код валюты не найден
        await callback.message.reply("К сожалению, данные об этой валюте недоступны.")

    # Уведомим Telegram, что callback был обработан
    await callback.answer()


# Обработчик неизвестных команд
@dp.message(F.text)
async def unknown_message(message: Message):
    await message.reply("Я не понимаю вашу команду. Используйте /start или /rates.")


# Асинхронная точка входа
async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)


# Запускаем бота
if __name__ == "__main__":
    asyncio.run(main())