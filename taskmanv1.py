import pandas as pd 
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter.ttk import Treeview

class Transaction:
    def __init__(self, amount, category, transac_type='expense', date=None):
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number")

        valid_types = ['expense', 'income']
        if transac_type.lower() not in valid_types:
            raise ValueError("Transaction type must be either 'expense' or 'income'")

        if date is None:
            date = datetime.now()

        self.amount = float(amount)
        self.category = category
        self.type = transac_type.lower()
        self.date = date

    def __str__(self):
        return f"{self.type.capitalize()}: ${self.amount} for {self.category} on {self.date.strftime('%Y-%m-%d')}"

class FinanceManager:
    def __init__(self):
        self.transactions = []
        self.init_database()
    
    def init_database(self):
        with sqlite3.connect('finance.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY,
                    amount REAL,
                    category TEXT,
                    type TEXT,
                    date TEXT
                )
            ''')
            conn.commit()
            self.load_transactions()
    
    def load_transactions(self):
        with sqlite3.connect('finance.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT amount, category, type, date FROM transactions')
            rows = cursor.fetchall()
            for row in rows:
                amount, category, trans_type, date = row
                date = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
                transaction = Transaction(amount, category, trans_type, date)
                self.transactions.append(transaction)
    
    def add_transaction(self, amount, category, trans_type='expense', date=None):
        try:
            transaction = Transaction(amount, category, trans_type, date)
            self.transactions.append(transaction)
            
            # Save to database
            with sqlite3.connect('finance.db') as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO transactions (amount, category, type, date)
                    VALUES (?, ?, ?, ?)
                ''', (transaction.amount, transaction.category, 
                     transaction.type, transaction.date.strftime('%Y-%m-%d %H:%M:%S')))
                conn.commit()
            return True
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return False
    
    def get_total_income(self):
        return sum(t.amount for t in self.transactions if t.type == 'income')
    
    def get_total_expenses(self):
        return sum(t.amount for t in self.transactions if t.type == 'expense')
    
    def get_balance(self):
        return self.get_total_income() - self.get_total_expenses()
    
    def get_transactions_by_category(self, category=None):
        if category:
            return [t for t in self.transactions if t.category.lower() == category.lower()]
        return self.transactions
    
    def show_summary(self):
        print("\n=== Financial Summary ===")
        print(f"Total Income: ${self.get_total_income():.2f}")
        print(f"Total Expenses: ${self.get_total_expenses():.2f}")
        print(f"Current Balance: ${self.get_balance():.2f}")
        print("\n=== Recent Transactions ===")
        for transaction in self.transactions[-5:]:  # Show last 5 transactions
            print(transaction)
        print("=====================")
    
    def get_category_totals(self):
        expense_categories = {}
        income_categories = {}
        for t in self.transactions:
            if t.type == 'expense':
                expense_categories[t.category] = expense_categories.get(t.category, 0) + t.amount
            else:
                income_categories[t.category] = income_categories.get(t.category, 0) + t.amount
        return expense_categories, income_categories
    
    def delete_transaction(self, transaction_id):
        with sqlite3.connect('finance.db') as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
        self.load_transactions()

class FinanceTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1000x600")  # Increased width for side panel
        self.manager = FinanceManager()
        self.setup_gui()
    
    def setup_gui(self):
        # Create main container
        main_container = ttk.Frame(self.root)
        main_container.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create left panel for notebook
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side='left', fill='both', expand=True)
        
        # Create right panel for summary
        right_panel = ttk.LabelFrame(main_container, text="Financial Summary", padding="10")
        right_panel.pack(side='right', fill='y', padx=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(left_panel)
        self.notebook.pack(expand=True, fill='both')
        
        # Create tabs
        self.transactions_tab = ttk.Frame(self.notebook)
        self.analysis_tab = ttk.Frame(self.notebook)
        self.budget_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.transactions_tab, text='Transactions')
        self.notebook.add(self.analysis_tab, text='Analysis')
        self.notebook.add(self.budget_tab, text='Budget')
        
        # Setup summary panel first
        self.setup_summary_panel(right_panel)
        
        # Then setup other tabs
        self.setup_transactions_tab()
        self.setup_analysis_tab()
        self.setup_budget_tab()
        
        # Update the summary panel immediately
        self.update_summary_panel()
    
    def setup_summary_panel(self, parent):
        # Total Income
        ttk.Label(parent, text="Total Income:", font=('Helvetica', 12, 'bold')).pack(pady=5)
        self.total_income_label = ttk.Label(parent, text="$0.00", font=('Helvetica', 11))
        self.total_income_label.pack(pady=5)
        
        # Total Expenses
        ttk.Label(parent, text="Total Expenses:", font=('Helvetica', 12, 'bold')).pack(pady=5)
        self.total_expenses_label = ttk.Label(parent, text="$0.00", font=('Helvetica', 11))
        self.total_expenses_label.pack(pady=5)
        
        # Remaining Balance
        ttk.Label(parent, text="Remaining Balance:", font=('Helvetica', 12, 'bold')).pack(pady=5)
        self.balance_label = ttk.Label(parent, text="$0.00", font=('Helvetica', 11))
        self.balance_label.pack(pady=5)
        
        # Add separator
        ttk.Separator(parent, orient='horizontal').pack(fill='x', pady=10)
        
        # This Month's Summary
        ttk.Label(parent, text="This Month", font=('Helvetica', 12, 'bold')).pack(pady=5)
        self.month_income_label = ttk.Label(parent, text="Income: $0.00", font=('Helvetica', 11))
        self.month_income_label.pack(pady=2)
        self.month_expenses_label = ttk.Label(parent, text="Expenses: $0.00", font=('Helvetica', 11))
        self.month_expenses_label.pack(pady=2)
        self.month_balance_label = ttk.Label(parent, text="Balance: $0.00", font=('Helvetica', 11))
        self.month_balance_label.pack(pady=2)
    
    def update_summary_panel(self):
        # Update total amounts
        total_income = self.manager.get_total_income()
        total_expenses = self.manager.get_total_expenses()
        balance = total_income - total_expenses
        
        self.total_income_label.config(text=f"${total_income:.2f}")
        self.total_expenses_label.config(text=f"${total_expenses:.2f}")
        self.balance_label.config(text=f"${balance:.2f}")
        
        # Calculate this month's totals
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        month_income = sum(t.amount for t in self.manager.transactions 
                         if t.type == 'income' and t.date.month == current_month 
                         and t.date.year == current_year)
        month_expenses = sum(t.amount for t in self.manager.transactions 
                           if t.type == 'expense' and t.date.month == current_month 
                           and t.date.year == current_year)
        month_balance = month_income - month_expenses
        
        self.month_income_label.config(text=f"Income: ${month_income:.2f}")
        self.month_expenses_label.config(text=f"Expenses: ${month_expenses:.2f}")
        self.month_balance_label.config(text=f"Balance: ${month_balance:.2f}")

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get())
            category = self.category_entry.get()
            trans_type = self.trans_type.get()
            date = self.date_entry.get_date()
            
            if not category:
                messagebox.showerror("Error", "Please enter a category")
                return
                
            if self.manager.add_transaction(amount, category, trans_type, date):
                self.amount_entry.delete(0, tk.END)
                self.category_entry.delete(0, tk.END)
                self.update_transaction_table()
                self.update_charts()
                self.update_summary_panel()  # Add this line
                messagebox.showinfo("Success", "Transaction added successfully!")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def delete_selected_transaction(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a transaction to delete")
            return
            
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?"):
            selected_item = selected_items[0]
            try:
                self.manager.delete_transaction(selected_item)
                self.update_transaction_table()
                self.update_charts()
                self.update_summary_panel()  # Add this line
                messagebox.showinfo("Success", "Transaction deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete transaction: {str(e)}")

    def setup_transactions_tab(self):
        # Transaction Entry Frame
        entry_frame = ttk.LabelFrame(self.transactions_tab, text="Add Transaction", padding="10")
        entry_frame.pack(fill='x', padx=10, pady=5)
        
        # Amount Entry
        ttk.Label(entry_frame, text="Amount:").grid(row=0, column=0, sticky="w")
        self.amount_entry = ttk.Entry(entry_frame)
        self.amount_entry.grid(row=0, column=1, padx=5)
        
        # Category Entry with Combobox
        ttk.Label(entry_frame, text="Category:").grid(row=1, column=0, sticky="w")
        self.category_entry = ttk.Combobox(entry_frame)
        self.category_entry['values'] = ('Salary', 'Rent', 'Food', 'Transportation', 'Entertainment', 'Utilities')
        self.category_entry.grid(row=1, column=1, padx=5)
        
        # Date Entry
        ttk.Label(entry_frame, text="Date:").grid(row=0, column=2, sticky="w")
        self.date_entry = DateEntry(entry_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.date_entry.grid(row=0, column=3, padx=5)
        
        # Transaction Type
        self.trans_type = tk.StringVar(value="expense")
        ttk.Radiobutton(entry_frame, text="Expense", variable=self.trans_type, 
                       value="expense").grid(row=2, column=0)
        ttk.Radiobutton(entry_frame, text="Income", variable=self.trans_type, 
                       value="income").grid(row=2, column=1)
        
        # Add Transaction Button
        ttk.Button(entry_frame, text="Add Transaction", 
                  command=self.add_transaction).grid(row=3, column=0, columnspan=4, pady=10)
        
        # Transactions Table
        table_frame = ttk.LabelFrame(self.transactions_tab, text="Transaction History", padding="10")
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.tree = Treeview(table_frame, columns=('Date', 'Type', 'Category', 'Amount'), 
                            show='headings')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Type', text='Type')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Amount', text='Amount')
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Right-click menu for delete
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete_selected_transaction)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        self.update_transaction_table()
    
    def setup_analysis_tab(self):
        # Create frame for charts
        charts_frame = ttk.Frame(self.analysis_tab)
        charts_frame.pack(fill='both', expand=True)
        
        # Create and pack the figure
        self.fig = plt.Figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=charts_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Add refresh button
        ttk.Button(charts_frame, text="Refresh Charts", 
                  command=self.update_charts).pack(pady=5)
        
        self.update_charts()
    
    def update_charts(self):
        # Clear the figure
        self.fig.clear()
        
        # Get category totals
        expense_categories, income_categories = self.manager.get_category_totals()
        
        # Create subplots
        expense_ax = self.fig.add_subplot(121)
        income_ax = self.fig.add_subplot(122)
        
        # Plot expense pie chart if there are expenses
        if expense_categories:
            expense_ax.pie(expense_categories.values(), labels=expense_categories.keys(), autopct='%1.1f%%')
            expense_ax.set_title('Expenses by Category')
        else:
            expense_ax.text(0.5, 0.5, 'No Expenses', horizontalalignment='center', verticalalignment='center')
        
        # Plot income pie chart if there are incomes
        if income_categories:
            income_ax.pie(income_categories.values(), labels=income_categories.keys(), autopct='%1.1f%%')
            income_ax.set_title('Income by Category')
        else:
            income_ax.text(0.5, 0.5, 'No Income', horizontalalignment='center', verticalalignment='center')
        
        # Adjust layout and redraw
        self.fig.tight_layout()
        self.canvas.draw()
    
    def setup_budget_tab(self):
        budget_frame = ttk.LabelFrame(self.budget_tab, text="Budget Settings", padding="10")
        budget_frame.pack(fill='x', padx=10, pady=5)
        
        # Add budget settings (placeholder for future implementation)
        ttk.Label(budget_frame, text="Budget features coming soon!").pack()
    
    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def update_transaction_table(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Add all transactions to the table
        for t in self.manager.transactions:
            self.tree.insert('', 'end', values=(
                t.date.strftime('%Y-%m-%d'),
                t.type.capitalize(),
                t.category,
                f"${t.amount:.2f}"
            ))

def main():
    try:
        root = tk.Tk()
        app = FinanceTrackerGUI(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()