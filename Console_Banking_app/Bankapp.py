import random
import os


def open_account(account_name, balance, _pin: str, _account_type="Savings") -> dict:
    full_details = {}
    account_num = account_num_gen()
    full_details[account_num] = {"Account_name": account_name, "Account_Type": _account_type,
                                 "Available_Balance": balance, "Pin": _pin}
    print(f"{' '.join(i for i in account_name.split('_'))}, you just opened a {_account_type} with Jagunlabi "
          f"Microfinance Bank.")
    print(f"Your account number is {account_num}")
    return full_details


def add_account(details: dict):
    get_details = details
    with open("All_accounts.txt", "a") as file:
        for i, j in get_details.items():
            a = f"{str(i): >8}{j['Account_name']: >30}{j['Account_Type']: >10}{j['Available_Balance']: >10}" \
                f"{str(j['Pin']): >10}\n"
            file.write(a)


def is_file_here():
    if os.path.isfile("C:/Users/a/OneDrive/Desktop/projects/All_accounts.txt") and os.stat("C:/Users/a/OneDrive/"
                                                                                           "Desktop/projects/"
                                                                                           "All_accounts.txt")\
            .st_size != 0:
        return True
    else:
        return False


def load_accounts():
    all_details = {}
    with open("All_accounts.txt", "r") as file:
        while True:
            details = file.readline()
            if details != "":
                details = details.split()
                all_details[int(details[0])] = {"Account_name": details[1], "Account_Type": details[2],
                                                "Available_Balance": details[3], "Pin": details[4]}
            else:
                break
    return all_details


def update_account(all_details: dict):
    with open("All_accounts.txt", "w") as file:
        i = len(all_details) - 1
        j = 0
        for k, v in all_details.items():
            if j == 0:
                stack = f"{str(k): >8}{v['Account_name']: >30}{v['Account_Type']: >10}{v['Available_Balance']: >10}" \
                        f"{str(v['Pin']): >10}\n"
            elif j < i:
                stack = f"{str(k): >8}{v['Account_name']: >30}{v['Account_Type']: >10}{v['Available_Balance']: >10}" \
                        f"{str(v['Pin']): >10}\n"
            elif j == i:
                stack = f"{str(k): >8}{v['Account_name']: >30}{v['Account_Type']: >10}{v['Available_Balance']: >10}" \
                        f"{str(v['Pin']): >10}\n"
            file.write(stack)
            j += 1


def prompt():
    _answer = input(
        """Good Day, Welcome to Jagunlabi Microfinance Bank.
        What Do you want to do today?
        [1] Open an Account
        [2] Check Balance
        [3] Withdraw
        [4] Transfer
        [5] Change pin
        [#] Exit
        Enter your Option here...... """
    )
    return _answer


def check(_account: int, all_account: dict, _pin: str) -> bool:
    if _account in all_account.keys():
        a = all_account[_account]
        i = 2
        while _pin != a['Pin'] and 0 <= i <= 3:
            _pin = input("Invalid pin, PLease Enter your pin again: ")
            i += 1
        if _pin != a['Pin']:
            print('Pin limit Exceeded')
            return False
        else:
            print("Account Number and Pin correct")
            return True
    else:
        print("Account Number Does not exit")
        return False


def account_num_gen():
    return random.randint(11111, 99999)


def account_type():
    mind = input(
        """What Type of account do you want to open?
        [1] Savings
        [2] Current
        Enter your Option......"""
    )
    if mind == "1":
        return "Savings"
    elif mind == "2":
        return "Current"
    else:
        print("Invalid Option, Savings was chosen for you by default")
        return "Savings"


def deposit():
    while True:
        mind = input(
            """Do you want to Deposit?
            [1] Yes
            [2] No
            Enter your Option......"""
        )
        if mind == "1":
            amount_deposited = int(input("Enter How much do you want to deposit."))
            print("Balance Updated!")
            return amount_deposited
        elif mind == "2":
            amount_deposited = 0
            return amount_deposited
        else:
            print("Enter the right option")


def get_pin():
    i = 1
    while 0 <= i <= 3:
        try:
            __pin = input("Enter your Pin: ")
            lenght = len(__pin)
            __a = int(__pin)
            if lenght == 4:
                return str(__pin)
            else:
                print(f"{2 - (i - 1)} chances remaining")
                i += 1
                print("Pin must be 4 digits")
        except (ValueError, TypeError):
            print(f"{2 - (i - 1)} chances remaining")
            i += 1
            print(f"Please enter digits")
    i += 1
    print("Limit Exceeded")
    return "Limit exceeded"


def check_sender(sender, alldetails: dict) -> bool:
    if sender in alldetails.keys():
        return True
    else:
        print("Sender's details not correct!")
        return False


while True:
    answer = prompt()
    if answer == "1":
        f_name = str(input("Please Enter your First Name: "))
        l_name = str(input("Please Enter your Last Name: "))
        full_name = f_name + "_" + l_name
        account = account_type()
        dep = deposit()
        _pin = get_pin()
        if _pin == "Limit exceeded":
            break
        else:
            here = open_account(full_name, dep, _pin, account)
            add_account(here)
            print("Your Account has been created!")
    elif answer == "2":
        if is_file_here():
            all_accounts = load_accounts()
            try:
                account_no = int(input("Please Enter Your Account Number: "))
                pin = get_pin()
                if pin != "Limit exceeded":
                    let_check = check(account_no, all_accounts, pin)
                    if let_check:
                        the_account = all_accounts[account_no]
                        print(f"Your account balance is: {the_account['Available_Balance']}")
                        continue
                    else:
                        print("The details you entered are incorrect!")
                    break
                else:
                    print("You exceeded your limit")
                    break
            except (ValueError, TypeError):
                print("Account Number must be Digits")
        else:
            print("No account in the database please create an account")
    elif answer == "3":
        if is_file_here():
            all_accounts = load_accounts()
            try:
                account_no = int(input("Please Enter Your Account Number: "))
                pin = get_pin()
                if pin != "Limit exceeded":
                    let_check = check(account_no, all_accounts, pin)
                    if let_check:
                        the_account = all_accounts[account_no]
                        amount = int(input("Enter Amount you want to withdraw: "))
                        balance = int(the_account['Available_Balance'])
                        if amount <= balance:
                            balance = balance - amount
                            balance = str(balance)
                            print(f"{amount} withdrawn from your account, and your remaining balance is: {balance}")
                            the_account['Available_Balance'] = balance
                            update_account(all_accounts)
                            continue
                        else:
                            print("Insufficient Balance!")
                            continue
                    else:
                        print("The details you entered are incorrect!")
                    continue
                else:
                    print("You exceeded your limit")
                    break
            except (ValueError, TypeError):
                print("Account Number must be Digits")
        else:
            print("No account in the database please create an account")
    elif answer == "4":
        if is_file_here():
            all_accounts = load_accounts()
            try:
                account_no = int(input("Please Enter Your Account Number: "))
                receiver = int(input("Enter Recipients Account Number: "))
                pin = get_pin()
                if pin != "Limit exceeded":
                    let_check = check(account_no, all_accounts, pin)
                    checksender = check_sender(receiver, all_accounts)
                    if let_check and checksender:
                        the_account_sender = all_accounts[account_no]
                        the_account_receiver = all_accounts[receiver]
                        amount = int(input("Enter Amount you want to Transfer: "))
                        balance = int(the_account_sender['Available_Balance'])
                        sender_balance = int(the_account_receiver['Available_Balance'])
                        print(f"""You are about to Transfer {amount} to: 
                                {' '.join(i for i in the_account_receiver['Account_name'].split('_'))}""")
                        final = input("""Are you sure you want to make this Transfer?
                                            [1] Yes
                                            [2] No
                                            Enter Option......... """)
                        if final == "1":
                            if amount <= balance:
                                balance -= amount
                                sender_balance += amount
                                balance = str(balance)
                                sender_balance = str(sender_balance)
                                print(f"{amount} debited from your account, and your remaining balance is: {balance}")
                                the_account_sender['Available_Balance'] = balance
                                the_account_receiver['Available_Balance'] = sender_balance
                                update_account(all_accounts)
                                continue
                            else:
                                print("Insufficient Balance!")
                                continue
                        elif final == "2":
                            continue
                        else:
                            print("You Entered Wrong input!! Try again")
                            continue
                    else:
                        print("The details you entered are incorrect!")
                    continue
                else:
                    print("You exceeded your limit")
                    break
            except (ValueError, TypeError):
                print("Account Number must be Digits")
        else:
            print("No account in the database please create an account")
    elif answer == "5":
        if is_file_here():
            all_accounts = load_accounts()
            try:
                account_no = int(input("Please Enter Your Account Number: "))
                pin = get_pin()
                if pin != "Limit exceeded":
                    let_check = check(account_no, all_accounts, pin)
                    if let_check:
                        the_account = all_accounts[account_no]
                        print("Please enter New pin")
                        new_pin = get_pin()
                        print("Please enter enter your New pin again to confirm New pin: ")
                        confirm_new_pin = get_pin()
                        if new_pin == confirm_new_pin:
                            the_account['Pin'] = confirm_new_pin
                            update_account(all_accounts)
                        else:
                            print("Both pin entries doesn't match!")
                            continue
                    else:
                        print("The details you entered are incorrect!")
                    continue
                else:
                    print("You exceeded your limit")
                    break
            except (ValueError, TypeError):
                print("Account Number must be Digits")
        else:
            print("No account in the database please create an account")
    elif answer == "#":
        print("Thank you for banking with us!!!!")
        break
    else:
        print("Invalid Option, Enter correct Option (1, 2, 3, 4, 5, and #)")
