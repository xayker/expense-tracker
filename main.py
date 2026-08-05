import tkinter as tk
import os
import csv
from tkinter import ttk
import requests

exchange_rates = {"TRY": 1}
FILENAME = "expenses.csv"
expenses = []

def fetch_exchange_rates():
    try:
        response = requests.get("https://api.frankfurter.app/latest?from=TRY")
        data = response.json()
        exchange_rates.update(data["rates"])
    except Exception as e:
        print("Could not fetch exchange rates", e)


def refresh_display():
    currency = currency_dropdown.get()
    rate = exchange_rates.get(currency,1)

    expense_listbox.delete(0, tk.END)
    for category, cost_in_TL in expenses:
        converted = cost_in_TL * rate
        expense_listbox.insert(tk.END, f"Category: {category} - {converted:.2f} {currency}")

    total_in_try = sum (cost for _, cost in expenses)
    total_converted = total_in_try * rate
    total_label.config(text=f"Total Expenses: {total_converted:.2f} {currency}")


def add_expense():
    category = category_input.get()
    currency = currency_dropdown.get()
    try:
        raw_cost = float(cost_input.get())
        warning_label.config(text=f"")
    except ValueError:
        warning_label.config(text="Please enter a numeric value")
        return

    cost_in_TL = raw_cost / exchange_rates.get(currency,1)
    expenses.append([category, cost_in_TL])

    category_input.delete(0, tk.END)
    cost_input.delete(0, tk.END)
    refresh_display()
    save_expenses()


def delete_expense():
    selected = expense_listbox.curselection()
    if not selected:
        return

    index = int(selected[0])
    expense_listbox.delete(index)
    del expenses[index]
    refresh_display()
    save_expenses()


def save_expenses():
    with open(FILENAME, "w") as f:
        writer = csv.writer(f)
        writer.writerows(expenses)


def load_expenses():
    if not os.path.exists(FILENAME):
        return

    with open(FILENAME, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            category = row[0]
            cost = float(row[1])
            expenses.append([category, cost])


if __name__ == '__main__':
    window = tk.Tk()
    window.title("Budget")
    window.geometry("500x500")

    tk.Label(window, text="Category:").pack(pady=5)
    category_input = tk.Entry(window)
    category_input.pack()

    tk.Label(window, text="Cost:").pack(pady=5)
    cost_input = tk.Entry(window)
    cost_input.pack()

    tk.Label(window, text="Currency:").pack(pady=5)
    currency_options = ["TRY", "USD", "EUR", "GBP"]
    currency_dropdown = ttk.Combobox(window, values=currency_options, state="readonly")
    currency_dropdown.current(0)
    currency_dropdown.pack()
    currency_dropdown.bind("<<ComboboxSelected>>", lambda e: refresh_display())

    add_expense_button = tk.Button(window, text="Add", command=add_expense)
    add_expense_button.pack(pady=10)

    expense_listbox = tk.Listbox(window, width = 40)
    expense_listbox.pack(pady=10)

    warning_label = tk.Label(window, text="", fg="red")
    warning_label.pack()

    total_label = tk.Label(window, text="Total: 0", font=("Arial", 12, "bold"))
    total_label.pack(pady=10)

    delete_button = tk.Button(window, text="Delete",command=delete_expense)
    delete_button.pack(pady=5)

    fetch_exchange_rates()
    load_expenses()
    refresh_display()
    window.mainloop()