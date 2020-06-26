from random import random, seed, randint
import sqlite3


# first level menu (возвращает пункт меню)
def first_menu():
    print('1. Create an account')
    print('2. Log into account')
    print('0. Exit')
    return int(input())


# second level menu (возвращает пункт меню)
def second_menu():
    print('1. Balance')
    print('2. Add income')
    print('3. Do transfer')
    print('4. Close account')
    print('5. Log out')
    print('0. Exit')
    return int(input())


# создает новые card и pin (возвращает новые card и pin)
def create_account():
    seed()
    print('Your card has been created')
    start_card = str(randint(0, 999999999))
    new_card = '400000' + '0' * (9 - len(start_card)) + start_card
    new_pin = str(randint(1000, 9999))

    luhn_card = list(new_card)
    new_card = new_card + check_luhn(luhn_card)

    print('Your card number:', new_card, sep='\n')
    print('Your card PIN:', new_pin, sep='\n', end='\n')
    return new_card, new_pin


# проверяет card и pin (возвращает номер текущей card)
def log_in():
    print('Enter your card number:')
    card_user = input()
    print('Enter your PIN:')
    pin_user = input()
    print()

    c.execute(f'select pin from card where number={card_user}')
    pin_from_db = c.fetchone()
    if pin_from_db is not None and pin_from_db[0] == pin_user:
        print('You have successfully logged in!', end='\n\n')
        return card_user
    else:
        print('Wrong card number or PIN!', end='\n\n')


# получение 16ой цифры по 15ти цифрам в списке (возвращает последний символ карты по алгоритму Luhn)
def check_luhn(luhn_card):
    sum_n = 0
    for i in range(len(luhn_card)):
        if i % 2 == 0:
            el = int(luhn_card[i]) * 2
            if el > 9:
                el = el % 10 + el // 10
        else:
            el = int(luhn_card[i])
        sum_n += el
    if sum_n % 10 == 0:
        return '0'
    return str(10 - sum_n % 10)


# действия доступные после login
def action_after_login(current_card):
    second_action = second_menu()
    print()
    if second_action == 1:
        print_balance(current_card)
    elif second_action == 2:
        add_income(current_card)
    elif second_action == 3:
        do_transfer(current_card)
    elif second_action == 4:
        close_account(current_card)
        return 4
    elif second_action == 5:
        print('You have successfully logged out!', end='\n\n')
        return 5
    elif second_action == 0:
        return 0


# добавление card и pin в базу
def add_entry(card_insert, pin_insert):
    c.execute(f"""insert into card (number,pin) values ({card_insert}, {pin_insert});""")
    conn.commit()


# пополнение текущей карты
def add_income(card_current):
    amount_income = int(input("Enter income:\n"))
    c.execute(f'update card set balance=balance+{amount_income} where number={card_current}')
    conn.commit()
    print('Income was added!', end='\n\n')


# увеличение баланса в базе по одной карте и уменьшение по другой
def transfer(card_from, card_to, transfer_amount):
    c.execute(f'update card set balance=balance+{transfer_amount} where number={card_to}')
    c.execute(f'update card set balance=balance-{transfer_amount} where number={card_from}')
    conn.commit()
    print('Success!', end='\n\n')


# логика для перевода между картами
def do_transfer(current_card):
    print('Transfer')
    card_transfer = input('Enter card number:\n')
    if not check_card_by_luhn(card_transfer):
        print('Probably you made mistake in the card number. Please try again!', end='\n\n')
    elif check_card_exist(card_transfer):
        if current_card != card_transfer:
            amount_transfer = int(input('Enter how much money you want to transfer:\n'))
            if check_balance(current_card) > amount_transfer:
                transfer(current_card, card_transfer, amount_transfer)
            else:
                print('Not enough money!\n')
        else:
            print("You can't transfer money to the same account!", end='\n\n')
    else:
        print('Such a card does not exist.', end='\n\n')


# валидация карты по Luhn алгоритму (возвращает True)
def check_card_by_luhn(current_card):
    if check_luhn(list(current_card[:-1])) == current_card[-1]:
        return True
    return False


# проверка существования карты (возвращает True)
def check_card_exist(current_card):
    c.execute(f'select * from card where number={current_card}')
    # pin_from_db = c.fetchone()
    return c.fetchone() is not None


# проверка баланса (print result)
def print_balance(current_card):
    print(f'Balance: {check_balance(current_card)}', end='\n\n')


# проверка баланса (возвращает значение)
def check_balance(current_card):
    c.execute(f'select balance from card where number={current_card}')
    return c.fetchone()[0]


# удаляет данные о карте
def close_account(current_card):
    c.execute(f'delete from card where number={current_card}')
    print('The account has been closed!', end='\n\n')
    conn.commit()


conn = sqlite3.connect('card.s3db')
c = conn.cursor()
c.execute("""create table IF NOT EXISTS card 
            (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)""")

login_dict = {}
while True:
    action = first_menu()
    print()
    if action == 1:
        card, pin = create_account()
        # print(card, pin)
        add_entry(card, pin)
        print()
    elif action == 2:
        user_card = log_in()
        if user_card is not None:
            while True:
                action = action_after_login(user_card)
                if action in (4, 5, 0):
                    break

    if action == 0:
        break

print('Bye!')

conn.close()
