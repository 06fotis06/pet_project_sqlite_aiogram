import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from main import new_user, add_items
import logging
import uuid
from time import sleep
from yookassa import Configuration, Payment



Configuration.account_id = '322515'
Configuration.secret_key = 'test_whyO7kq8q_wHG2Lh6MN-B2xzoi1l5c5nRQ1I75FmUYs'

def gen_link(about):
    payment = Payment.create({
        "amount": {
            "value": about,
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.example.com/return_url"
        },
        "capture": True,
        "description": "Заказ №2"
    }, uuid.uuid4())
    print(payment.confirmation.confirmation_url)
    payment_id = payment.id
    return [payment.confirmation.confirmation_url, payment_id, payment]


def chek(payment_id, pay):
    payment = Payment.find_one(payment_id)
    payment.status
    payment_id = payment.id
    if payment.status == 'succeeded':
        return True



API_TOKEN = '6052307193:AAEGqIyhbzSx0L1_G6twalTI-PqLNLqwGVI'

# Configure logging
logging.basicConfig(level=logging.INFO)
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Пример списка товаров (можете получить его из базы данных)
products = [
    {"id": 1, "name": "Товар 1", "price": 100},
    {"id": 2, "name": "Товар 2", "price": 200},
    {"id": 12423432, "name": "clear"},
    {"id":321312, "name":"pay"}
]

# Создание клавиатуры с кнопками товаров
product_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
for product in products:
    if product['id'] != 12423432 and product['id'] != 321312:
        button_text = f"{product['name']} - {product['price']} руб."
        product_keyboard.add(KeyboardButton(f'/buy{product["id"]} | {button_text} '))
    elif product['id'] == 321312:
        product_keyboard.add(KeyboardButton(f'/pay'))

    else:
        product_keyboard.add(KeyboardButton(f'/clear_basket'))
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['pay'])
async def pay(message: types.Message):
    with sqlite3.connect('database.db') as con:
        cursor = con.cursor()
        cursor.execute(f'SELECT basket FROM users WHERE telegram_id = {message.from_user.id}')
        try:
            basket = str(cursor.fetchone()[0]).split('0')
            basket_set = set(basket)
            price = 0
            for i in basket_set:
                price += int(products[int(i) - 1]["price"])*basket.count(i)
            await message.answer(f'сумма {price}руб.')
            a = gen_link(str(price) + '.00')
            await message.answer(f'{a[0]}')
            for i in range(600):
                if chek(a[1], a[2]) == True:
                    await message.answer(f'товары оплачены')
                    cursor.execute(f'''UPDATE users SET basket =  0 WHERE telegram_id = {message.from_user.id}''')

                    break
        except:
            try :
                basket = str(cursor.fetchone()[0]).split('0')
                await message.answer('Зарегайся')
            except:
                await message.answer('Корзина пуста')

@dp.message_handler(commands=['clear_basket'])
async def buy_1(message: types.Message):
    with sqlite3.connect('database.db') as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT basket FROM users WHERE telegram_id = {message.from_user.id}")
        basket = cursor.fetchone()
        print(basket)
        cursor.execute(f'''UPDATE users SET basket =  0 WHERE telegram_id = {message.from_user.id}''')

@dp.message_handler(commands=['buy1'])
async def buy_1(message: types.Message):
    add_items(1, message.from_user.id)
    await message.answer('товар добавлен в корзину')

@dp.message_handler(commands=['buy2'])
async def buy_2(message: types.Message):
    add_items(2, message.from_user.id)
    await message.answer('товар добавлен в корзину')


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('/login | вход\n/login <name> | регистрация')

@dp.message_handler(commands=['basket'])
async def basket(message: types.Message):
    #product_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    #product_keyboard.add(KeyboardButton('/clear_basket'))
    with sqlite3.connect('database.db') as con:
        cursor = con.cursor()
        cursor.execute(f'SELECT basket FROM users WHERE telegram_id = {message.from_user.id}')
        try:
            basket = str(cursor.fetchone()[0]).split('0')
            basket_set = set(basket)
            mess = ''
            for i in basket_set:
                mess += (f'{products[int(i) - 1]["name"]} x {products[int(i) - 1]["price"]}$ x {basket.count(i)}\n')
            await message.answer(mess)
        except:
            try :
                basket = str(cursor.fetchone()[0]).split('0')
                await message.answer('Зарегайся')
            except:
                await message.answer('Корзина пуста')


@dp.message_handler(commands=['products'])
async def produc(message: types.Message):
    await message.answer('список товаров',reply_markup=product_keyboard)

@dp.message_handler(commands=['login'])
async def alarm(message: types.Message):
    with sqlite3.connect('database.db') as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT telegram_id FROM users WHERE telegram_id = {message.from_user.id}")
        t_id = cursor.fetchone()
        if str(t_id) == "None":
            new_user(message.from_user.id,message.text.split()[1])
            cursor.execute(f"SELECT name FROM users WHERE telegram_id = {message.from_user.id}")
            name = cursor.fetchone()[0]
            await message.answer(f'создан новый аккаунт | {name}')
        elif len(message.text.split()) == 2 and str(t_id) != "None":
            await message.answer('вы уже зарегистрированы')
        elif len(message.text.split()) == 1 and str(t_id) != "None":
            cursor.execute(f"SELECT name FROM users WHERE telegram_id = {message.from_user.id}")
            name = cursor.fetchone()[0]
            await message.answer(f'добро пожаловать {name}')



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)