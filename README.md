# Trip Expense Tracker

A simple web application to track shared expenses between two people, with automatic balance calculation and running totals.

## Features

- Add new expenses with details like date, description, category, and payment mode
- Automatic calculation of equal shares (customizable)
- Track running balance between two people
- View all expenses in a sortable table
- Responsive design that works on mobile and desktop
- Import existing expenses from CSV

## Setup

1. Make sure you have Python 3.8+ installed
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python app.py
   ```
4. Open your browser and go to `http://localhost:5000`

## Usage

1. **Adding an Expense**:

   - Click the "Add Expense" button
   - Fill in the expense details
   - The shares will be automatically calculated equally, but you can modify them
   - Click "Save Expense" to add it to the list

2. **Viewing Expenses**:

   - All expenses are displayed in a table
   - The current balance is shown at the top
   - Negative amounts in red indicate who owes money
   - Positive amounts in green indicate who is owed money

3. **Importing from CSV**:
   - Place your CSV file in the project directory
   - Make sure it has the required columns
   - The application will automatically import the data on first run

## Data Structure

The application uses SQLite to store expenses in a file called `expenses.db` in the project directory.
