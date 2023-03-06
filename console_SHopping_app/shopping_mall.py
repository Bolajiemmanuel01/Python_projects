import os
import random


def load_stock() -> dict:
    stock = {}
    if os.path.isfile('./projects/shoplist.txt'):
        with open('./projects/shoplist.txt') as file:
            data = file.read()
            stock = eval(data)
    return stock


def save_stock(stock):
    with open('./projects/shoplist.txt', 'w') as file:
        i = len(stock) - 1
        j = 0
        for k, v in stock.items():
            if j == 0:
                stack = "{"f"'{k}':{v},\n"
            elif j < i:
                stack = f"'{k}':{v},\n"
            elif j == i:
                stack = f"'{k}':{v}""}"
            file.write(stack)
            j += 1


def order_ref():
    return random.randint(100, 999999)


def save_order(order):
    with open('./projects/receipt.txt', 'a') as file:
        ref_order = {}
        ref = order_ref()
        ref_order[ref] = order
        file.write("=" * 70)
        file.write(f"\n{'Reference no.'+ str(ref): >20}{'Item Id': >10}{'Item Name': >15}{'Qty': >4}{'Price': >10}\n")
        file.write("=" * 70)
        total_cost = 0
        for orders in ref_order.values():
            for Id, products in orders.items():
                total_cost += (products['price'] * products['qty'])
                file.write(f"\n{Id: >30}{products['name']: >15}{products['qty']: >4}{products['price']: >10}" +
                           f"{(products['price'] * products['qty']): >10}\n")
        file.write("=" * 70)
        file.write(f"\n{total_cost: > 70}\n")


print('Welcome to God is Good Mall...')
stock = load_stock()
if stock:
    cart = {}
    trial = 0
    while trial < 3:
        choice = input('[0]: Show Stock\n[1]: Add to cart\n[2]: Edit Cart \
                       \n[3]: Show Cart\n[4]: Checkout\n[#]: Exit\nEnter Option: ')

        if choice == '0':
            if stock:
                print(f'{"ID": <5}{"Name": <15}{"Price": >8}{"Qty": >5}')
                print('=' * 35)
                for key in stock:
                    item = stock[key]
                    print(f'{key: <5}{item["name"]: <15}{item["price"]: >8}{item["qty"]: >5}')
            else:
                print('Close shop...')
            print()

        elif choice == '1':
            key = input('Enter item id: ')
            if key in stock:
                if key not in cart:
                    item = stock[key]
                    qty = int(input('Enter qty: '))
                    if qty > 0:
                        if item['qty'] >= qty:
                            cart[key] = {'name': item['name'], 'price': item['price'], 'qty': qty}
                            print("Item added to cart.")
                        else:
                            print('out of stock')
                    else:
                        print('Invalid input')
                else:
                    print('item already in cart\nchoose edit option')
            else:
                print('Invalid item id')
                trial += 1
        elif choice == '2':
            if cart:
                print(f'{"ID": <5}{"Name": <15}{"Price": >8}{"Qty": >5}')
                print('=' * 35)
                for key in cart:
                    item = cart[key]
                    print(f'{key: <5}{item["name"]: <15}{item["price"]: >8}{item["qty"]: >5}')
                print()

                item_id = input('Enter item id: ')
                if item_id in cart:
                    new_qty = int(input('Enter new qty (to remove item, enter 0): '))
                    if new_qty >= 0:
                        if new_qty == 0:
                            del cart[item_id]
                        elif new_qty <= stock[item_id]['qty']:
                            cart[item_id]['qty'] = new_qty
                            print('item updated...')
                        else:
                            print('out of stock')
                    else:
                        print('Invalid input')
                else:
                    print('Invalid item id')
            else:
                print('Your cart is empty!!!')
        elif choice == '3':
            if cart:
                total = 0
                print(f'{"ID": <5}{"Name": <15}{"Price": >8}{" ":^3}{"Qty": >5}')
                print('=' * 50)
                for key in cart:
                    item = cart[key]
                    total += (item['price'] * item['qty'])
                    print(
                        f'{key: <5}{item["name"]: <15}{item["price"]: >8} {"*":^1}{item["qty"]: >5}{(item["price"] * item["qty"]): >10}')
                print('=' * 50)
                print(f'{total: >48}')
                print('=' * 50)
                print()
            else:
                print('Empty cart')
        elif choice == '4':
            if cart:
                total = 0
                print(f'{"ID": <5}{"Name": <15}{"Price": >8}{" ":^3}{"Qty": >5}')
                print('=' * 50)
                for key in cart:
                    item = cart[key]
                    total += (item['price'] * item['qty'])
                    print(
                        f'{key: <5}{item["name"]: <15}{item["price"]: >8} {"*":^1}{item["qty"]: >5}{(item["price"] * item["qty"]): >10}')
                print('=' * 50)
                print(f'{total: >48}')
                print('=' * 50)
                print()

                option = input('[1]: Proceed\n[2]: Cancel\n[#]: Previous Menu\n \
                            Enter option: ')
                if option == '1':
                    pymnt = float(input('Make payment: '))
                    if pymnt >= total:
                        if pymnt > total:
                            balance = pymnt - total
                            print(f'Take your change: {balance}')
                        for key in cart:
                            if key in stock:
                                stock[key]['qty'] -= cart[key]['qty']
                        save_stock(stock)
                        save_order(cart)
                        cart.clear()
                        print('Thanks for shopping')
                    else:
                        print('Insufficient Fund')
                        continue
                elif option == '2':
                    if input('Are you sure? Y/N').upper() == 'Y':
                        cart.clear()
                        print('Cart has been cleared')
                elif option == '#':
                    continue
            else:
                print('Empty cart')

        elif choice == '#':
            break
        else:
            print('Invalid option')
            trial += 1
else:
    print('Shop closed!')