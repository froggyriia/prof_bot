from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

create_dispatch = KeyboardButton(text='Создать рассылку')
check_promo = KeyboardButton(text='Проверить наличие промокода в используемых')

admin_keyboard = [[create_dispatch], [check_promo]]
admin_keyboard_markup = ReplyKeyboardMarkup(keyboard=admin_keyboard, resize_keyboard=True)

edit_text = KeyboardButton(text='текст рассылки')

edit_text_for_button = KeyboardButton(text='название кнопки')
edit_link = KeyboardButton(text='ссылку')
mail_keyboard = [[edit_text], [edit_text_for_button], [edit_link]]
mail_keyboard_markup = ReplyKeyboardMarkup(keyboard=mail_keyboard, resize_keyboard=True)

yes = KeyboardButton(text='yes')
no = KeyboardButton(text='no')
yonkb = [[yes, no]]
yonkb_markup = ReplyKeyboardMarkup(keyboard=yonkb, resize_keyboard=True)