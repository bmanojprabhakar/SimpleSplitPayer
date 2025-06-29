import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database configuration with environment variable support
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Handle PostgreSQL URL format for production
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Default to SQLite for local development
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
    try:
        if request.content_type != 'application/json':
            return jsonify({'success': False, 'error': 'Content-Type must be application/json'}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['date', 'description', 'total_amount', 'paid_by', 'person1_share', 'person2_share']
        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            return jsonify({'success': False, 'error': error_msg}), 400
        
        try:
            # Parse and validate data
            date_obj = datetime.strptime(str(data['date']), '%Y-%m-%d').date()
            total_amount = float(data['total_amount'])
            person1_share = float(data['person1_share'])
            person2_share = float(data['person2_share'])
            paid_by = str(data['paid_by'])
            
            # Validate paid_by value
            if paid_by not in ['person1', 'person2']:
                return jsonify({'success': False, 'error': 'paid_by must be either person1 or person2'}), 400
            
            # Validate amounts are positive
            if total_amount <= 0 or person1_share < 0 or person2_share < 0:
                return jsonify({'success': False, 'error': 'Amounts must be positive'}), 400
            
            expense = Expense(
                date=date_obj,
                description=str(data['description']).strip(),
                category=str(data.get('category', '')).strip(),
                payment_mode=str(data.get('payment_mode', '')).strip(),
                total_amount=total_amount,
                paid_by=paid_by,
                person1_share=person1_share,
                person2_share=person2_share,
                balance=0,
                running_total=0
            )
            
            db.session.add(expense)
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
            
        except ValueError as e:
            error_msg = f'Invalid data format: {str(e)}'
            db.session.rollback()
            return jsonify({'success': False, 'error': error_msg}), 400
            
    except Exception as e:
        error_msg = f'Unexpected error: {str(e)}'
        app.logger.error(f"Error in add_expense: {error_msg}")
        db.session.rollback()
        return jsonify({'success': False, 'error': error_msg}), 500

@app.route('/edit_expense/<int:expense_id>', methods=['POST', 'PUT'])
def edit_expense(expense_id):
    try:
        data = request.get_json()
        expense = Expense.query.get_or_404(expense_id)
        
        # Validate and update expense
        expense.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        expense.description = str(data['description']).strip()
        expense.category = str(data.get('category', '')).strip()
        expense.payment_mode = str(data.get('payment_mode', '')).strip()
        expense.total_amount = float(data['total_amount'])
        expense.paid_by = str(data['paid_by'])
        expense.person1_share = float(data.get('person1_share', 0))
        expense.person2_share = float(data.get('person2_share', 0))
        expense.balance = 0
        expense.running_total = 0
        
        # Validate paid_by value
        if expense.paid_by not in ['person1', 'person2']:
            return jsonify({'success': False, 'error': 'paid_by must be either person1 or person2'}), 400
        
        # Validate amounts are positive
        if expense.total_amount <= 0 or expense.person1_share < 0 or expense.person2_share < 0:
            return jsonify({'success': False, 'error': 'Amounts must be positive'}), 400
        
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
        app.logger.error(f"Error in edit_expense: {str(e)}")
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
        app.logger.error(f"Error in delete_expense: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)