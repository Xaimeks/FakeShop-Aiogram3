import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from .db import get_db_connection
import app.keyboards as kb

router = Router()

connection = get_db_connection()
cursor = connection.cursor()

class Buying(StatesGroup):
    city = State()
    product = State()
    number = State()

class Register(StatesGroup):
    nickname = State()

def get_products():
    if not connection:
        logging.error("Не удалось подключиться к базе данных")
        return []
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, product_name, price, store_name, city FROM catalog")
            products = cursor.fetchall()
            return products
        
    except Exception as e:
        logging.error(f"Ошибка при выполнении запроса: {e}")
        return []
    
    finally:
        connection.close()

@router.message(F.text == "Работа")
async def work(message: types.Message):
    await message.answer("""
                         😉МЫ ГАРАНТИРУЕМ ВАМ БЕЗОПАСНОСТЬ И ОТКРЫТОСТЬ\n❤️ДАЖЕ В КРАЙНЕМ СЛУЧАЕ НЕ УГРОЖАЕМ РАСПРАВОЙ\n\nСТРОГО 17+ КУРАТОР @hkurator
                         """)
    
@router.message(F.text == "Города")
async def cities(message: types.Message):
    # PEP8 
    cities_list = "🏙️Доступные города:\n\nМосква\nПитер\nНовосибирск\nКазань\nЕкб\nУфа\nВолгоград\nВолжский\nСочи\nВоронеж\nПермь\nНижний Новгород\nЧелябинск\nКрасноярск"
    await message.answer(cities_list)

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    try:
        await state.set_state(Register.nickname)
        user_id = message.from_user.id
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id, ))
        result = cursor.fetchone()

        if result is None:
            await message.answer("Введите произвольное имя")
        else:
            await message.answer("⏬", reply_markup=kb.main)

    except Exception as e:
        await message.answer(f"Произошла ошибка {e}")

    finally:
        if cursor:
            cursor.close()

@router.message(Register.nickname)
async def handle_nickname_set(message: Message, state: FSMContext):
    try:

        await state.update_data(user_nickname=message.text)
        data = await state.get_data()
        user_nickname = data["user_nickname"]
        user_id = message.from_user.id
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id, ))
        result = cursor.fetchone()

        if result is None:
            cursor.execute('INSERT INTO users (id, name) VALUES (%s, %s)', (user_id, user_nickname, ))
            connection.commit()

            await message.answer("⏬", reply_markup=kb.main)
        else:
            await message.answer("Вы уже вводили имя", reply_markup=kb.main)

        await state.clear()
        
    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

    finally:
        if cursor:
            cursor.close()

@router.message(F.text == "Каталог")
async def select_city(message: Message, state: FSMContext):
    await state.set_state(Buying.city)
    await message.answer("Введите свой город:")

@router.message(Buying.city)
async def handle_city_input(message: Message, state: FSMContext):

    await state.update_data(city=message.text)
    data = await state.get_data()
    selected_city = data["city"]

    await message.answer(f"Вы выбрали город {selected_city}", reply_markup=None)

    await state.set_state(Buying.product)
    await message.answer("Выберите товар", reply_markup=kb.catalog)

@router.message(Buying.product)
async def select_product_handler(message: Message, state: FSMContext):
    await state.update_data(product=message.text)
    data = await state.get_data()
    product = data["product"]
    selected_city = data["city"]
    await message.answer(f"Вы выбрали товар: {product}")

    products = get_products()

    if products:
        found_products = False 
        for id, product_name, price, store_name, city in products:
            if city == selected_city:
                if product in product_name:
                    found_products = True 
                    product_info = (f"Номер товара {id}:\n"
                                    f"Название {product_name}\n"
                                    f"Цена {price}₽\n"
                                    f"Магазин {store_name}\n"
                                    f"Город {city}\n")
                    await message.answer(product_info, reply_markup=None)
                    await message.answer("Не употребляйте наркотики!")

                    await state.update_data(selected_product_name = product_name)
                    await state.update_data(selected_product_price = price)
                    await state.update_data(selected_product_store = store_name)

        if not found_products:
            await message.answer("В вашем городе нет товара.")
    else:
        await message.answer("Список пуст.")

    """ await state.set_state(Buying.number)
    if found_products:
        await message.answer("Выберите номер товара")

@router.message(Buying.number)
async def select_number_handler(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    data = await state.get_data()
    
    number = data["number"]
    selected_product_name = data["selected_product_name"]
    selected_product_price = data["selected_product_price"]
    selected_product_store = data["selected_product_store"]

    products = get_products()
    product_found = False

    if number.isdigit():
        number = int(number)
        for id, product_name, price, store_name, city in products:
            if id == number:
                if selected_product_name == product_name:
                    product_found = True
                    await message.answer(
                        f"Вы выбрали товар под номером: {number}\n"
                        f"Название: {selected_product_name}\n" 
                        f"Цена: {selected_product_price}₽\n" 
                        f"Магазин: {selected_product_store}"
                    )
                    await message.answer("Не употребляйте наркотики!")
                    break
    if not product_found:
        await message.answer("Товар с таким номером не найден.") """
