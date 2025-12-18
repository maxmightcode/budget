# FILE NAME - anything_goes.py
# NAME: Max Perrin
# DATE: 12/12/25 - Originally put in wrong git account since I was on my desktop couldn't figure out why I couldn't see it on my laptop at first haha.
# BRIEF DESCRIPTION:
# Budget Buddy is a simple menu-driven budget tracker. It manages expenses by letting the user add transactions, 
# view/edit/delete them, set budgets by category, checks if there over budget and export a report to a text file. 
# Data is saved using files so it stays between runs.

# 1. (AI assistance): https://chat.openai.com/
# Used for brainstorming program structure (menu + features/layout) and for ideas on input validation while I wrote the code.

# 2. Python datetime docs (used to confirm date formatting with strftime / parsing)
#    https://docs.python.org/3/library/datetime.html

# 3. Python csv module docs (used to confirm DictReader usage)
#    https://docs.python.org/3/library/csv.html

import csv
import json
from datetime import datetime

TRANSACTIONS_FILE = "transactions.csv"
BUDGETS_FILE = "budgets.json"



def ensure_files_exist():
    #Create the data files if they do not exist

    try:
        with open(TRANSACTIONS_FILE, "r", encoding="utf-8"):
            pass
    except FileNotFoundError:
        with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "type", "category", "amount", "note"])  # header row

    try:
        with open(BUDGETS_FILE, "r", encoding="utf-8"):
            pass
    except FileNotFoundError:
        save_budgets({})


def load_transactions():
    #Read CSV into a list of dictionaries

    transactions = []
    with open(TRANSACTIONS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row["amount"] = float(row["amount"])
            except (ValueError, TypeError):
                row["amount"] = 0.0
            transactions.append(row)  # list append
    return transactions


def save_all_transactions(transactions):
    #Rewrite the full CSV after edit/delete.

    with open(TRANSACTIONS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "type", "category", "amount", "note"])
        for tx in transactions:
            writer.writerow([tx["date"], tx["type"], tx["category"], tx["amount"], tx["note"]])


def add_transaction_to_file(tx):
    #Append one transaction to the CSV

    with open(TRANSACTIONS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([tx["date"], tx["type"], tx["category"], tx["amount"], tx["note"]])


def load_budgets():
    #Load budgets from JSON
    try:
        with open(BUDGETS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Convert values to float safely
    budgets = {}
    for cat, val in data.items():
        try:
            budgets[cat] = float(val)
        except (ValueError, TypeError):
            budgets[cat] = 0.0
    return budgets


def save_budgets(budgets):
    #Save budgets to JSON file (file output)

    with open(BUDGETS_FILE, "w", encoding="utf-8") as f:
        json.dump(budgets, f, indent=2)



def prompt_date():
    #Ask the user for a date. If blank, use today's date.

    while True:
        raw = input("Date (YYYY-MM-DD) or Enter for today: ").strip()
        if raw == "":
            return datetime.now().strftime("%Y-%m-%d")
        try:
            datetime.strptime(raw, "%Y-%m-%d")
            return raw
        except ValueError:
            print("Invalid date. Example: 2025-12-15")


def prompt_type():
    #Ask for income or expense.

    while True:
        raw = input("Type (E)xpense or (I)ncome: ").strip().lower()
        if raw in ["e", "expense"]:
            return "expense"
        if raw in ["i", "income"]:
            return "income"
        print("Please enter E or I.")


def prompt_amount():
    #Ask for a positive number

    while True:
        raw = input("Amount (example: 12.50): ").strip()
        try:
            amt = float(raw)
            if amt > 0:
                return amt
            print("Amount must be > 0.")
        except ValueError:
            print("Please enter a valid number.")


def prompt_text(label, allow_blank=False):
    #Ask for text input.

    while True:
        val = input(label + ": ").strip()
        if val == "" and not allow_blank:
            print("Please enter something (not blank).")
        else:
            return val


def prompt_index(max_num):
    ##Choose a transaction number 

    while True:
        raw = input(f"Transaction number (1-{max_num}): ").strip()
        if raw.isdigit():
            num = int(raw)
            if 1 <= num <= max_num:
                return num - 1
        print("Invalid number. Try again.")



def add_transaction():
    print("\n--- Add Transaction ---")
    date_str = prompt_date()
    tx_type = prompt_type()
    category = prompt_text("Category (ex: Food, Gas, Work)")
    amount = prompt_amount()
    note = prompt_text("Note (optional)", allow_blank=True)

    tx = {
        "date": date_str,
        "type": tx_type,
        "category": category,
        "amount": amount,
        "note": note
    }

    add_transaction_to_file(tx)
    print("Saved!\n")


def view_transactions(transactions):
    print("\n--- View Transactions ---")
    if len(transactions) == 0:
        print("No transactions yet.\n")
        return

    for i, tx in enumerate(transactions, start=1):
        sign = "-" if tx["type"] == "expense" else "+"
        print(f"{i:>3}. {tx['date']} | {tx['type']:<7} | {tx['category']:<12} | {sign}${tx['amount']:.2f} | {tx['note']}")
    print()


def edit_transaction(transactions):
    print("\n--- Edit Transaction ---")
    if len(transactions) == 0:
        print("No transactions to edit.\n")
        return

    view_transactions(transactions)
    idx = prompt_index(len(transactions))
    tx = transactions[idx]

    print("\nPress Enter to keep the current value.\n")

    new_date = input(f"Date [{tx['date']}]: ").strip()
    new_type = input(f"Type expense/income [{tx['type']}]: ").strip().lower()
    new_cat = input(f"Category [{tx['category']}]: ").strip()
    new_amt = input(f"Amount [{tx['amount']}]: ").strip()
    new_note = input(f"Note [{tx['note']}]: ").strip()

    # Conditionals and validation
    if new_date != "":
        try:
            datetime.strptime(new_date, "%Y-%m-%d")
            tx["date"] = new_date
        except ValueError:
            print("Invalid date. Keeping old date.")

    if new_type != "":
        if new_type in ["expense", "e"]:
            tx["type"] = "expense"
        elif new_type in ["income", "i"]:
            tx["type"] = "income"
        else:
            print("Invalid type. Keeping old type.")

    if new_cat != "":
        tx["category"] = new_cat

    if new_amt != "":
        try:
            amt_val = float(new_amt)
            if amt_val > 0:
                tx["amount"] = amt_val
            else:
                print("Amount must be > 0. Keeping old amount.")
        except ValueError:
            print("Invalid amount. Keeping old amount.")

    if new_note != "":
        tx["note"] = new_note

    transactions[idx] = tx  # list
    save_all_transactions(transactions)
    print("Transaction updated!\n")


def delete_transaction(transactions):
    print("\n--- Delete Transaction ---")
    if len(transactions) == 0:
        print("No transactions to delete.\n")
        return

    view_transactions(transactions)
    idx = prompt_index(len(transactions))

    print("\nSelected:")
    print(transactions[idx])

    confirm = input("Delete this transaction? (y/n): ").strip().lower()
    if confirm == "y":
        transactions.pop(idx)  
        save_all_transactions(transactions)
        print("Deleted!\n")
    else:
        print("Delete canceled.\n")


def summary(transactions):
    print("\n--- Summary ---")
    if len(transactions) == 0:
        print("No transactions to summarize.\n")
        return

    income_total = 0.0
    expense_total = 0.0
    category_spend = {}  # dictionary used for totals

    for tx in transactions:  # loop
        if tx["type"] == "income":
            income_total += tx["amount"]
        else:
            expense_total += tx["amount"]
            cat = tx["category"]
            category_spend[cat] = category_spend.get(cat, 0.0) + tx["amount"]

    net = income_total - expense_total

    print(f"Total income : ${income_total:.2f}")
    print(f"Total expense: ${expense_total:.2f}")
    print(f"Net          : ${net:.2f}\n")

    if len(category_spend) > 0:
        print("Spending by category:")
        for cat, total in sorted(category_spend.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat:<12} ${total:.2f}")
    print()


def set_budget():
    print("\n--- Set Category Budget ---")
    budgets = load_budgets()

    category = prompt_text("Category to budget")
    amount = prompt_amount()

    budgets[category] = amount
    save_budgets(budgets)
    print(f"Budget set: {category} -> ${amount:.2f}\n")


def check_budgets(transactions):
    print("\n--- Budget Check ---")
    budgets = load_budgets()
    if len(budgets) == 0:
        print("No budgets set yet. Choose 'Set Category Budget' first.\n")
        return

    spent = {}
    for tx in transactions:
        if tx["type"] == "expense":
            cat = tx["category"]
            spent[cat] = spent.get(cat, 0.0) + tx["amount"]

    for cat, limit in budgets.items():
        used = spent.get(cat, 0.0)
        remaining = limit - used

        if used == 0:
            status = "No spending yet"
        elif remaining > 0:
            status = f"OK (${remaining:.2f} left)"
        elif remaining == 0:
            status = "Exactly at budget"
        else:
            status = f"OVER by ${abs(remaining):.2f} !!!"

        print(f"{cat:<12} Budget ${limit:.2f} | Spent ${used:.2f} | {status}")
    print()


def export_report(transactions):
    print("\n--- Export Report ---")
    if len(transactions) == 0:
        print("No transactions to export.\n")
        return

    filename = prompt_text("Report filename (example: report.txt)")
    income_total = sum(tx["amount"] for tx in transactions if tx["type"] == "income")
    expense_total = sum(tx["amount"] for tx in transactions if tx["type"] == "expense")
    net = income_total - expense_total

    lines = []  # list creation
    lines.append("BUDGET BUDDY REPORT")
    lines.append("-" * 45)
    lines.append("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("")
    lines.append(f"Total income : ${income_total:.2f}")
    lines.append(f"Total expense: ${expense_total:.2f}")
    lines.append(f"Net          : ${net:.2f}")
    lines.append("")
    lines.append("Transactions:")
    lines.append("-" * 45)

    for tx in transactions:
        sign = "-" if tx["type"] == "expense" else "+"
        lines.append(f"{tx['date']} | {tx['type']:<7} | {tx['category']:<12} | {sign}${tx['amount']:.2f} | {tx['note']}")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("Exported report to:", filename, "\n")



def print_menu():
    print("=== Budget Buddy ===")
    print("1) Add transaction")
    print("2) View transactions")
    print("3) Edit transaction")
    print("4) Delete transaction")
    print("5) Summary")
    print("6) Set category budget")
    print("7) Check budgets")
    print("8) Export report to file")
    print("9) Quit")


def main():
    ensure_files_exist()

    while True:  # loop requirement
        transactions = load_transactions()

        print_menu()
        choice = input("Choose an option (1-9): ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions(transactions)
        elif choice == "3":
            edit_transaction(transactions)
        elif choice == "4":
            delete_transaction(transactions)
        elif choice == "5":
            summary(transactions)
        elif choice == "6":
            set_budget()
        elif choice == "7":
            check_budgets(transactions)
        elif choice == "8":
            export_report(transactions)
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please type 1-9.\n")


if __name__ == "__main__":
    main()


########################################
#          REFLECTION QUESTIONS
########################################

'''
Remember to cite any sources you used to help you complete this project.
You can do that here in this section or cite as comments throughout your code.

1. How did you choose the goal of your program?
I chose a budget tracker because I have multiple income streams and I wanted one place to record
both income and expenses. This idea felt realistic and useful, and it also fit the project requirements while I was planning to make one anyway.

2. What part of this project challenged you the most? How did you work through that challenge?
The hardest part was saving and loading data correctly so it would still be there after the program closed.
I solved it by using a CSV file for transactions and a JSON file for budgets. I also tested the program
with different inputs (blank input, wrong numbers, etc.) and added checks/try-except to prevent crashes.

3. If you had 10 more hours to improve or expand your program, what would you change? Why?
I would add searching and filtering (like showing only one month or one category), and I would add a
simple chart output (like a text-based bar chart) to make spending patterns easier to understand.
I would also add an option to sort transactions by date.

Just to end off I hope you enjoyed what I did with the project and how it turned out, Even though we only exchanged a few emails I appreciated your feedback and material and I wish you all the best
'''









########################################
#          REFLECTION QUESTIONS
########################################

'''

Remember to cite any sources you used to help you complete this project.
You can do that here in this section or cite as comments throughout your code.

 1. How did you choose the goal of your program?
 I chose a budget tracker because I have multiple income streams and I wanted one place to record
 both income and expenses. This idea felt realistic and useful, and it also fit the project requirements.

 2. What part of this project challenged you the most? How did you work through that challenge?
 The hardest part was saving and loading data correctly so it would still be there after the program closed.
 I solved it by using a CSV file for transactions and a JSON file for budgets. I also tested the program
 with different inputs (blank input, wrong numbers, etc.) and added checks/try except to prevent crashings.

 3. If you had 10 more hours to improve or expand your program, what would you change? Why?
 I would add searching and filtering (like showing only one month or one category), and I would add a
 simple chart output (like a text-based bar chart) to make spending patterns easier to understand.
 I would also add an option to sort transactions by date.

'''









