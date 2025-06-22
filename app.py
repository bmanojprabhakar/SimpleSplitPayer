from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pandas as pd
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50))
    payment_mode = db.Column(db.String(50))
    total_amount = db.Column(db.Float, nullable=False)
    paid_by = db.Column(db.String(50), nullable=False)  # 'person1' or 'person2'
    person1_share = db.Column(db.Float, nullable=False)
    person2_share = db.Column(db.Float, nullable=False)
    balance = db.Column(db.Float, nullable=False)
    running_total = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    expenses = Expense.query.order_by(Expense.date).all()
    
    # Calculate summary data
    total_amount = sum(expense.total_amount for expense in expenses)
    person1_total = sum(expense.person1_share for expense in expenses)
    person2_total = sum(expense.person2_share for expense in expenses)
    
    # Calculate total spends (who actually paid)
    person1_spent = sum(expense.total_amount for expense in expenses if expense.paid_by == 'person1')
    person2_spent = sum(expense.total_amount for expense in expenses if expense.paid_by == 'person2')
    
    return render_template('index.html',
                         expenses=expenses,
                         total_amount=total_amount,
                         person1_total=person1_total,
                         person2_total=person2_total,
                         person1_spent=person1_spent,
                         person2_spent=person2_spent)

@app.route('/add_expense', methods=['POST'])
def add_expense():
    print("\n=== New Expense Request ===")
    print(f"Request headers: {request.headers}")
    print(f"Content-Type: {request.content_type}")
    
    try:
        if request.content_type != 'application/json':
            print("Invalid content type. Expected application/json")
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        print(f"Received JSON data: {data}")
        
        if not data:
            print("No JSON data received")
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['date', 'description', 'total_amount', 'paid_by', 'person1_share', 'person2_share']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            print(f"Validation error: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 400
        
        try:
            # Parse the date string into a date object
            date_obj = datetime.strptime(str(data['date']), '%Y-%m-%d').date()
            total_amount = float(data['total_amount'])
            person1_share = float(data['person1_share'])
            person2_share = float(data['person2_share'])
            paid_by = str(data['paid_by'])
            
            print(f"Parsed values - date: {date_obj}, total: {total_amount}, "
                  f"p1_share: {person1_share}, p2_share: {person2_share}, paid_by: {paid_by}")
            
            expense = Expense(
                date=date_obj,
                description=str(data['description']),
                category=str(data.get('category', '')),
                payment_mode=str(data.get('payment_mode', '')),
                total_amount=total_amount,
                paid_by=paid_by,
                person1_share=person1_share,
                person2_share=person2_share,
                balance=0,
                running_total=0
            )
            
            print("Adding expense to database...")
            db.session.add(expense)
            db.session.commit()
            print("Expense added successfully!")
            
            return jsonify({
                'success': True,
                'expense': {
                    'id': expense.id,
                    'date': expense.date.strftime('%Y-%m-%d'),
                    'description': expense.description,
                    'category': expense.category,
                    'payment_mode': expense.payment_mode,
                    'total_amount': expense.total_amount,
                    'paid_by': expense.paid_by,
                    'person1_share': expense.person1_share,
                    'person2_share': expense.person2_share,
                    'balance': expense.balance,
                    'running_total': expense.running_total
                }
            })
            
        except ValueError as e:
            error_msg = f'Invalid data format: {str(e)}'
            print(f"Data validation error: {error_msg}")
            db.session.rollback()
            return jsonify({'success': False, 'error': error_msg}), 400
            
    except Exception as e:
        error_msg = f'Unexpected error: {str(e)}'
        print(f"Unexpected error: {error_msg}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/edit_expense/<int:expense_id>', methods=['POST', 'PUT'])
def edit_expense(expense_id):
    try:
        data = request.get_json()
        expense = Expense.query.get_or_404(expense_id)
        
        # Update expense
        expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        expense.description = data['description']
        expense.category = data.get('category', '')
        expense.payment_mode = data.get('payment_mode', '')
        expense.total_amount = float(data['total_amount'])
        expense.paid_by = data['paid_by']
        expense.person1_share = float(data.get('person1_share', 0))
        expense.person2_share = float(data.get('person2_share', 0))
        expense.balance = 0
        expense.running_total = 0
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'expense': {
                'id': expense.id,
                'date': expense.date.strftime('%Y-%m-%d'),
                'description': expense.description,
                'category': expense.category,
                'payment_mode': expense.payment_mode,
                'total_amount': expense.total_amount,
                'paid_by': expense.paid_by,
                'person1_share': expense.person1_share,
                'person2_share': expense.person2_share,
                'balance': expense.balance,
                'running_total': expense.running_total
            }
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        db.session.delete(expense)
        db.session.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

# Removed recalculate_running_totals function and its route as they're no longer needed

if __name__ == '__main__':
    app.run(debug=True, port=5002)
