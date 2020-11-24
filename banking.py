import random
import sqlite3
conn = sqlite3.connect('card.s3db')
c = conn.cursor()

c.execute('DROP TABLE IF EXISTS card')
conn.commit()
c.execute('''CREATE TABLE IF NOT EXISTS card(
    id INTEGER PRIMARY KEY,
    number TEXT,
    pin TEXT,
    balance INTEGER DEFAULT 0
);''')
conn.commit()


class BankAccount:
    def __init__(self):
        self.credit_card = str(400000000000000 + random.randint(000000000, 999999999))
        cc_array = [int(x) for x in self.credit_card]
        counter = 0
        total = 0
        for digit in cc_array:
            if counter % 2 == 0:
                digit *= 2
            counter += 1
            if digit > 9:
                digit = digit - 9
            total += digit
        total *= 9
        checksum = total % 10
        self.credit_card += str(checksum)
        self.pin_number = str(random.randint(0000, 9999)).zfill(4)
        self.balance = 0

    def get_credit_card(self):
        return self.credit_card

    def get_pin_number(self):
        return self.pin_number

    def get_balance(self):
        return self.balance


def menu():
    choice = input('''
1. Create an account
2. Log into account
0. Exit
''')

    if choice == '1':
        account = BankAccount()
        current_account = (account.get_credit_card(), account.get_pin_number(), account.get_balance())
        c.execute('INSERT INTO card(number, pin, balance) VALUES (?, ?, ?)', current_account)
        conn.commit()
        print('Your card has been created')
        print('Your card number:')
        print(account.get_credit_card())
        print('Your card PIN:')
        print(account.get_pin_number())
        menu()
    elif choice == '2':
        card_number = input('Enter your card number:\n')
        card_pin = input('Enter your PIN:\n')
        card_tuple = (card_number, card_pin)
        c.execute('SELECT * FROM card WHERE number=? AND pin=?', card_tuple)
        conn.commit()
        current_account = c.fetchone()
        if current_account:
            print('You have successfully logged in!')

            def sub_menu():
                print('1. Balance')
                print('2. Add income')
                print('3. Do transfer')
                print('4. Close account')
                print('5. Log out')
                print('0. Exit')
                sub_choice = input()
                if sub_choice == '1':
                    c.execute('SELECT balance FROM card WHERE number=? AND pin=?', card_tuple)
                    conn.commit()
                    current_balance = c.fetchone()[0]
                    print('Balance:', current_balance)
                    sub_menu()
                elif sub_choice == '2':
                    income = int(input('Enter income\n'))
                    income_tuple = (income,)
                    income_tuple += card_tuple
                    c.execute('UPDATE card SET balance=balance+? WHERE number=? AND pin=?', income_tuple)
                    conn.commit()
                    print('Income was added!')
                    sub_menu()
                elif sub_choice == '3':
                    print('Transfer')
                    print('Enter card number:')
                    transfer_card = input()
                    transfer_card_array = [int(x) for x in transfer_card]
                    transfer_card_array = transfer_card_array[:-1]
                    counter = 0
                    total = 0
                    for digit in transfer_card_array:
                        if counter % 2 == 0:
                            digit *= 2
                        counter += 1
                        if digit > 9:
                            digit = digit - 9
                        total += digit
                    total *= 9
                    checksum = total % 10
                    if int(transfer_card[-1]) != checksum:
                        print('Probably you made a mistake in the card number. Please try again!')
                        sub_menu()
                    transfer_card_tuple = (transfer_card,)
                    c.execute('SELECT * FROM card WHERE number=?', transfer_card_tuple)
                    conn.commit()
                    transfer_account = c.fetchone()
                    if transfer_account == current_account:
                        print("You can't transfer money to the same account!")
                        sub_menu()
                    elif transfer_account:
                        print('Enter how much money you want to transfer:')
                        transfer_amount = int(input())
                        c.execute('SELECT * FROM card WHERE number=? AND pin=?', card_tuple)
                        conn.commit()
                        transfer_origin_account = c.fetchone()
                        print(transfer_origin_account)
                        if transfer_amount > transfer_origin_account[3]:
                            print('Not enough money!')
                        else:
                            transfer_tuple = (transfer_amount,)
                            transfer_tuple += card_tuple
                            c.execute('UPDATE card SET balance=balance-? WHERE number=? AND pin=?', transfer_tuple)
                            conn.commit()
                            transfer_to_tuple = (transfer_amount,)
                            transfer_to_tuple += transfer_card_tuple
                            c.execute('UPDATE card SET balance=balance+? WHERE number=?', transfer_to_tuple)
                            conn.commit()
                            print('Success!')
                            sub_menu()
                    else:
                        print('Such a card does not exist')
                        sub_menu()
                elif sub_choice == '4':
                    c.execute('DELETE FROM card where number=? AND pin=?', card_tuple)
                    conn.commit()
                    print('The account has been closed!')
                    menu()
                elif sub_choice == '5':
                    print('You have successfully logged out!')
                    menu()
                elif sub_choice == '0':
                    print('Bye!')

            sub_menu()
        else:
            print('Wrong card number or PIN!')
            menu()
    elif choice == '0':
        print('Bye!')
        conn.close()


menu()
