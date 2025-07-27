import mysql.connector
import random
import string
from datetime import date
from prettytable import PrettyTable

def connection():
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS _fooditems (item_id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), price DECIMAL(10, 2))")
    cursor.execute("CREATE TABLE IF NOT EXISTS _order (custname VARCHAR(255), custph BIGINT, order_id INT AUTO_INCREMENT PRIMARY KEY, item_id INT, quantity INT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS _sales (date DATE, bill_no VARCHAR(10), net_amount DECIMAL(10, 2), gst DECIMAL(10, 2), gross_amount DECIMAL(10, 2))")

def create_sales_table():
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()

    cursor.execute("CREATE TABLE IF NOT EXISTS _sales (date DATE, bill_no VARCHAR(10), net_amount DECIMAL(10, 2), gst DECIMAL(10, 2), gross_amount DECIMAL(10, 2))")

def generate_bill_no():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def fooditemto_menu(name, price):
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()

    query = "INSERT INTO _fooditems (name, price) VALUES (%s, %s)"
    data = (name, price)
    cursor.execute(query, data)
    con.commit()
    print("ADDED DISH:", name, "PRICE ₹", price)

def display_menu():
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()
    global menu
    menu = []

    cursor.execute("SELECT * FROM _fooditems")
    data = cursor.fetchall()
    for i in data:
        food_item = (i[0], i[1], i[2])
        print("  ", i[0], "  ", i[1], " ", i[2], "(₹)/per plate")
        menu.append(food_item)

def take_orders():
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()
    display_menu()
    
    custname = input("Enter your name: ")
    custph = int(input("Enter phone number: "))
    item_id = int(input("Enter the item ID to order: "))
    quantity = int(input("Enter the quantity: "))

    if item_id < 1 or item_id > len(menu):
        print("Invalid item ID.")
        return

    query = "INSERT INTO _order (custname, custph, item_id, quantity) VALUES (%s, %s, %s, %s)"
    data = (custname, custph, item_id, quantity)
    cursor.execute(query, data)
    con.commit()

    cursor.execute("SELECT LAST_INSERT_ID()")
    order_id = cursor.fetchone()[0]

    print("== Ordered Successfully ==")
    print("Please wait. Your order ID is:", order_id)

def _totalcost():
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()

    print("== BILLING ==")
    userid = int(input("Enter your order ID: "))

    cursor.execute("SELECT item_id, quantity FROM _order WHERE order_id = %s", (userid,))
    order = cursor.fetchone()

    if not order:
        print("Order not found!")
        return

    item_id, quantity = order

    cursor.execute("SELECT price FROM _fooditems WHERE item_id = %s", (item_id,))
    price_data = cursor.fetchone()

    if not price_data:
        print("Item not found in menu!")
        return

    price = price_data[0]
    gst = 0.09
    net = quantity * price
    gross = net + net * gst

    bill_no = generate_bill_no()
    today = date.today()
    cursor.execute("INSERT INTO _sales (date, bill_no, net_amount, gst, gross_amount) VALUES (%s, %s, %s, %s, %s)", 
                   (today, bill_no, net, net * gst, gross))
    con.commit()

    print("You have to pay ₹", round(gross, 2), "including 9% GST")
    print("======= HAVE A NICE DAY! =======")

def orderhistory():
    passcode = input("Enter admin passcode: ")
    if passcode == "dav":
        con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
        cursor = con.cursor()

        cursor.execute("SELECT * FROM _order")
        data = cursor.fetchall()
        count = 1
        for j in data:
            custname, custph, order_id, item_id, quantity = j
            print("===== Customer", count, "=====")
            print("Name:", custname)
            print("Phone:", custph)
            print("Order ID:", order_id)
            print("Item ID:", item_id)
            print("Quantity:", quantity)
            count += 1
    else:
        print("Unauthorized access!")

def display_total_sales_from_db():
    con = mysql.connector.connect(host="localhost", user="root", password="1234", database="indian_restruant")
    cursor = con.cursor()

    cursor.execute("SELECT * FROM _sales")
    data = cursor.fetchall()

    if not data:
        print("No sales data available.")
        return

    table = PrettyTable()
    table.field_names = ["Date", "Bill No", "Net Amount", "GST", "Gross Amount"]
    for sale in data:
        table.add_row(sale)

    print(table)

# Initial setup and loop
create_sales_table()
connection()

while True:
    print("\n=== Online Food Order System Menu ===")
    print("1. Add Food Item to Menu")
    print("2. Display Menu")
    print("3. Take Order")
    print("4. Calculate Total Cost")
    print("5. Display Order History")
    print("6. Display Total Sales")
    print("7. Quit")

    choice = input("Enter your choice: ")

    if choice == "1":
        passcode = input("Enter admin passcode: ")
        if passcode == "dav":
            name = input("Enter food item name: ")
            price = float(input("Enter food item price: "))
            fooditemto_menu(name, price)
        else:
            print("Unauthorized access!")

    elif choice == "2":
        display_menu()

    elif choice == "3":
        take_orders()

    elif choice == "4":
        _totalcost()

    elif choice == "5":
        orderhistory()

    elif choice == "6":
        display_total_sales_from_db()

    elif choice == "7":
        print("Exiting... Goodbye!")
        break

    else:
        print("Invalid choice. Please try again.")
