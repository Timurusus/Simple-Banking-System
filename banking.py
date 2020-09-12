import random
import sqlite3

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("""
            create table if not exists card (
            id INTEGER PRIMARY KEY,
            number TEXT,
            pin TEXT,
            balance INTEGER DEFAULT 0
            )
            """)


main_menu_str = "1. Create an account\n2. Log into account\n0. Exit"
user_menu_str = "1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5. Log out\n0. Exit"
INN = '400000'


def get_checksum(user_card_number_without_checksum):
    card_list = [int(i) for i in user_card_number_without_checksum]
    card_list_mul = []
    for i in range(len(card_list)):
        if i % 2 == 0:
            card_list_mul.append(card_list[i] * 2)
        else:
            card_list_mul.append(card_list[i])
    card_list_substr_9 = []
    for i in card_list_mul:
        if i > 9:
            card_list_substr_9.append(i - 9)
        else:
            card_list_substr_9.append(i)
    sum_of_digits = sum(card_list_substr_9)
    checksum = str(10 - sum_of_digits % 10)
    return int(checksum[-1])


def check_checksum(transfer_to_card_input):
    card_list = [int(i) for i in transfer_to_card_input[:-1]]
    card_list_mul = []
    for i in range(len(card_list)):
        if i % 2 == 0:
            card_list_mul.append(card_list[i] * 2)
        else:
            card_list_mul.append(card_list[i])
    card_list_substr_9 = []
    for i in card_list_mul:
        if i > 9:
            card_list_substr_9.append(i - 9)
        else:
            card_list_substr_9.append(i)
    sum_of_digits = sum(card_list_substr_9)
    checksum = str(10 - sum_of_digits % 10)
    return checksum[-1] == transfer_to_card_input[-1]


def user_menu(sql_query_card_fetch):
    print()
    print(user_menu_str)
    user_menu_input = int(input())
    if user_menu_input == 1:
        print(f"Balance: {sql_query_card_fetch[2]}")
        print()
        user_menu(sql_query_card_fetch)
    elif user_menu_input == 2:
        print()
        print("Enter income:")
        input_income = int(input())
        cur.execute(f"UPDATE card SET balance = balance + {input_income} WHERE number = {sql_query_card_fetch[0]}")
        conn.commit()
        print("Income was added!")
        user_menu(sql_query_card_fetch)
    elif user_menu_input == 3:
        print()
        print("Transfer")
        print("Enter card number:")
        transfer_to_card_input = input()
        if transfer_to_card_input == sql_query_card_fetch[0]:
            print("You can't transfer money to the same account!")
            user_menu(sql_query_card_fetch)
        else:

            if check_checksum(transfer_to_card_input):

                cur.execute(f"SELECT number FROM card WHERE number = {transfer_to_card_input}")
                transfer_to_card = cur.fetchone()
                if transfer_to_card:
                    print("Enter how much money you want to transfer:")
                    money_to_input = int(input())
                    cur.execute(f"SELECT balance FROM card WHERE number = {sql_query_card_fetch[0]}")
                    current_balance = cur.fetchone()
                    if money_to_input > current_balance[0]:
                        print("Not enough money!")
                        user_menu(sql_query_card_fetch)
                    else:
                        cur.execute(f"UPDATE card SET balance = balance + {money_to_input} WHERE number = {transfer_to_card[0]}")
                        cur.execute(f"UPDATE card SET balance = balance - {money_to_input} WHERE number = {sql_query_card_fetch[0]}")
                        conn.commit()
                        print("Success!")
                        user_menu(sql_query_card_fetch)
                else:
                    print("Such a card does not exist.")
                    user_menu(sql_query_card_fetch)
            else:
                print("Probably you made a mistake in the card number.")
                print("Please try again!")
                user_menu(sql_query_card_fetch)
    elif user_menu_input == 4:
        print()
        cur.execute(f"DELETE FROM card WHERE number = {sql_query_card_fetch[0]}")
        conn.commit()
        print("The account has been closed!")
        user_menu(sql_query_card_fetch)
    elif user_menu_input == 5:
        print()
        print("You have successfully logged out!")
        print()
        main_menu()
    elif user_menu_input == 0:
        print()
        print("Bye!")


def main_menu():
    print(main_menu_str)
    user_input = int(input())
    if user_input == 1:
        customer_account_number = ""
        for i in range(9):
            customer_account_number += str(random.randint(0, 9))
        user_pin_code = ""
        for i in range(4):
            user_pin_code += str(random.randint(0, 9))
        user_card_number_without_checksum = INN + customer_account_number
        user_checksum = get_checksum(user_card_number_without_checksum)
        user_card_number = user_card_number_without_checksum + str(user_checksum)
        cur.execute(f"INSERT INTO card(number,pin) VALUES ({user_card_number}, {user_pin_code})")
        conn.commit()
        print("Your card has been created")
        print("Your card number:")
        print(user_card_number)
        print("Your card PIN:")
        print(user_pin_code)
        print()
        main_menu()
    elif user_input == 2:
        print("Enter your card number:")
        user_input_log_in = input()
        print("Enter your PIN:")
        user_input_pin = input()
        cur.execute(f"SELECT number, pin, balance from card WHERE number = {user_input_log_in} AND pin = {user_input_pin}")
        sql_query_card_fetch = cur.fetchone()
        if sql_query_card_fetch:
            #if (user_input_log_in == sql_query_card_fetch[0]) and (user_input_pin == sql_query_card_fetch[1]):
            print("You have successfully logged in!")
            user_menu(sql_query_card_fetch)
        else:
            print()
            print("Wrong card number or PIN!")
            main_menu()
    elif user_input == 0:
        print()
        print("Bye!")


if __name__ == '__main__':
    main_menu()
    conn.close()
