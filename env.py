import random
import string

token = '7490801991:AAGVXjxQeKzbqxSWclKX1VGaM9bsKhxxHzM'
admins = ['natabut', 'froggy_riia']


def generate_promo_code(length=5):
    """Генерирует случайный промокод указанной длины"""
    characters = string.ascii_uppercase + string.digits
    promo_code = 'СКИДКА-10-' + ''.join(random.choice(characters) for _ in range(length))

    with open('promo_codes.txt', 'a') as file:
        file.write(f"{promo_code}\n")
    return promo_code

