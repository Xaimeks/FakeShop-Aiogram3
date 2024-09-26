from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Каталог"),
                                     KeyboardButton(text="Работа")],
                                     [KeyboardButton(text="Города")]],
                                     resize_keyboard=True,
                                     input_field_placeholder="Выберите пункт меню...")


catalog = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Бошки"), KeyboardButton(text="Мефедрон")],
        [KeyboardButton(text="Экстази"), KeyboardButton(text="Кокаин")],
        [KeyboardButton(text="Alpha-PVP"), KeyboardButton(text="Гашиш")],
        [KeyboardButton(text="Амфетамин"), KeyboardButton(text="Героин")],
        [KeyboardButton(text="Мухоморы"), KeyboardButton(text="ЛСД")],
        [KeyboardButton(text="Лирика")]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите товар..."
)
