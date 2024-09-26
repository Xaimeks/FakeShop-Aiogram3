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

@router.message(F.text == "Работа")
async def work(message: types.Message):
    await message.answer("""😉МЫ ГАРАНТИРУЕМ ВАМ БЕЗОПАСНОСТЬ И ОТКРЫТОСТЬ\n❤️ДАЖЕ В КРАЙНЕМ СЛУЧАЕ НЕ УГРОЖАЕМ РАСПРАВОЙ\n\nСТРОГО 17+ КУРАТОР @hkurator""")

@router.message(F.text == "Города")
async def cities(message: types.Message):
    cities_list = "🏙️Доступные города:\n\nМосква\nПитер\nНовосибирск\nКазань\nЕкб\nУфа\nВолгоград\nВолжский\nСочи\nВоронеж\nПермь\nНижний Новгород\nЧелябинск\nКрасноярск"
    await message.answer(cities_list)

@router.message(CommandStart())
async def command_start(message: Message, state: FSMContext):
    try:
        await state.set_state(Register.nickname)
        user_id = message.from_user.id
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()

        if result is None:
            await message.answer("Введите произвольное имя")
        else:
            await message.answer("⏬", reply_markup=kb.main)

    except Exception as e:
        await message.answer(f"Произошла ошибка {e}")

@router.message(Register.nickname)
async def handle_nickname_set(message: Message, state: FSMContext):
    try:
        await state.update_data(user_nickname=message.text)
        data = await state.get_data()
        user_nickname = data["user_nickname"]
        user_id = message.from_user.id
        cursor = connection.cursor()
        cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
        result = cursor.fetchone()

        if result is None:
            cursor.execute('INSERT INTO users (id, name) VALUES (%s, %s)', (user_id, user_nickname))
            connection.commit()
            await message.answer("⏬", reply_markup=kb.main)
            await state.set_state(Buying.city)
            await message.answer("Введите свой город:")
        else:
            await message.answer("Вы уже зарегистрированы. Пожалуйста, выберите город:")
            await state.set_state(Buying.city)
            await message.answer("Введите свой город:")

    except Exception as e:
        await message.answer(f"Произошла ошибка: {e}")

@router.message(Buying.city)
async def handle_city_input(message: Message, state: FSMContext):
    await state.update_data(city=message.text.strip())
    data = await state.get_data()
    selected_city = data["city"]

    await message.answer(f"Вы выбрали город {selected_city}", reply_markup=None)
    await state.set_state(Buying.product)
    await message.answer("Выберите товар", reply_markup=kb.catalog)

@router.message(Buying.product)
async def select_product_handler(message: Message, state: FSMContext):
    await state.update_data(product=message.text.strip())  # Убираем лишние пробелы
    data = await state.get_data()
    product = data["product"]
    selected_city = data["city"]

    products = get_products()
    found_products = False 

    if products:
        for id, product_name, price, store_name, city in products:
            if city == selected_city and product.lower() in product_name.lower(): 
                found_products = True 
                product_info = (f"Номер товара {id}:\n"
                                f"Название {product_name}\n"
                                f"Цена {price}₽\n"
                                f"Магазин {store_name}\n"
                                f"Город {city}\n")
                await message.answer(product_info, reply_markup=None)
                await message.answer("Не употребляйте наркотики!")

                # Сохраняем информацию о выбранном продукте
                await state.update_data(selected_product_name=product_name)
                await state.update_data(selected_product_price=price)
                await state.update_data(selected_product_store=store_name)

                # Переход к следующему состоянию для ввода номера товара
                await state.set_state(Buying.number)
                await message.answer("Введите номер товара:")

        if not found_products:
            await message.answer("Зачем тебе это?")
    else:
        await message.answer("Наркотики зло!")

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
        await message.answer("Товар с таким номером не найден.")



# Не вставлено в финальную версию
"""
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
        await message.answer("Товар с таким номером не найден.")
"""
