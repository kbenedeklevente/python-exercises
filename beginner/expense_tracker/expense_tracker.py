import os
import argparse
from datetime import datetime
import json
import shlex
from calendar import month_name

class ExpenseTracker():
    def __init__(self):
        self.file_path = './expenses.json'
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as file:
                self.expenses = {}
                json.dump(self.expenses, file)
        else:
            with open(self.file_path, 'r') as file:
                self.expenses = {int(k): v for k, v in json.load(file).items()}
    
    def __save_expenses(self):
        with open(self.file_path, 'w') as file:
            json.dump(self.expenses, file)

    def add(self, description, amount):
        next_id = max(self.expenses.keys(), default=0) + 1
        current_date = datetime.today().strftime("%Y-%m-%d")
        data = {
            "date": current_date,
            "description": description,
            "amount": amount
        }
        self.expenses[next_id] = data
        print(f"{description} succesfully added.")
        self.__save_expenses()

    def delete(self, id):
        if id in self.expenses:
            del self.expenses[id]
            print(f"Expense {id} succesfully deleted.")
            self.__save_expenses()
        else:
            print("Id not found. Please try again.")

    def list(self):
        return self.expenses

    def summary(self, month=None):
        if month:
            current_year = datetime.now().year
            filtered_data = {k: v for k,v in self.expenses.items()
                             if (datetime.strptime(v['date'], "%Y-%m-%d").month == month 
                                 and datetime.strptime(v['date'], "%Y-%m-%d").year == current_year)}
            return sum(v["amount"] for k, v in filtered_data.items())
        else:
            return sum(v["amount"] for k, v in self.expenses.items()) 

def format_expenses_list(expenses_json):
    for k, v in expenses_json.items():
        print(f"{k}  {v['date']}  {v['description']}  ${v['amount']}")


def __main__():
    expense_tracker = ExpenseTracker()
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    add_parser = subparsers.add_parser('add', help="Add a new expense with a description.")    
    add_parser.add_argument('--description', type=str, required=True, help="Description of expense.")
    add_parser.add_argument('--amount', type=int, required=True, help="Expense amount.")

    delete_parser = subparsers.add_parser('delete', help="Delete expense by ID.")
    delete_parser.add_argument('--id', type=int, help="ID of expense to be deleted.")

    list_parser = subparsers.add_parser('list', help="List all expenses.")

    summary_parser = subparsers.add_parser('summary', help="Get a summary of expenses.")
    summary_parser.add_argument('--month', type=int, help="Specify a month of the current year to filter the summary for that month.")

    while True:
        command = input("expernse-tracker ").strip()

        if command.lower() == 'quit':
            print('Exiting.')
            break

        try:
            args = parser.parse_args(shlex.split(command))
            if args.command == 'add':
                expense_tracker.add(args.description, args.amount)
            if args.command == 'delete':
                expense_tracker.delete(args.id)
            if args.command == 'list':
                format_expenses_list(expense_tracker.list())
            if args.command == 'summary':
                if args.month is not None:
                    if args.month not in range(1, 13):
                        print("Month doesn't exist. Please try again.")
                        continue
                    summary = expense_tracker.summary(args.month)
                    print(f"Total expenses for {month_name[args.month]}: ${summary}")
                else:
                    summary = expense_tracker.summary()
                    print(f"Total expenses: ${summary}")

        except SystemExit:
            continue

if __name__ == '__main__':
   __main__()