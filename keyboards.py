from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

btn1 = KeyboardButton('Регистрация') # для всех
btn2 = KeyboardButton('Вход') # для всех
btn3 = KeyboardButton('Выход') # для авторизованных
btn4 = KeyboardButton('Случайный пост') # для всех
btn5 = KeyboardButton('Отмена') # для авторизованных
btn6 = KeyboardButton('Новые посты') # для авторизованных
btn7 = KeyboardButton('Добавить пост') # для авторизованных

keyboard_isnt_login = ReplyKeyboardMarkup()
keyboard_isnt_login.row(btn1)
keyboard_isnt_login.row(btn2)
keyboard_isnt_login.row(btn4)

keyboard_is_login = ReplyKeyboardMarkup()
keyboard_is_login.row(btn7)
keyboard_is_login.row(btn6)
keyboard_is_login.row(btn4)
keyboard_is_login.row(btn3)

keyboard_cancel = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
keyboard_cancel.row(btn5)
