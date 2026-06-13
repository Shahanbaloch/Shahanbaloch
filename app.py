from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = 'barretts-secret-key-2025'

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'barretts123'

orders = []

MENU = {
    "starters": [
        {"id": "s1", "name": "Soup of the Day", "price": 6.50},
        {"id": "s2", "name": "Prawn Cocktail", "price": 8.00},
        {"id": "s3", "name": "Mushrooms on Toast", "price": 7.50},
        {"id": "s4", "name": "Chicken Liver Pâté", "price": 8.50},
    ],
    "mains": [
        {"id": "m1", "name": "Fish & Chips", "price": 16.00},
        {"id": "m2", "name": "Sunday Roast", "price": 18.00},
        {"id": "m3", "name": "Beef Burger", "price": 15.00},
        {"id": "m4", "name": "Pie of the Day", "price": 15.50},
        {"id": "m5", "name": "Veggie Wellington", "price": 14.00},
        {"id": "m6", "name": "Grilled Salmon", "price": 17.50},
    ],
    "desserts": [
        {"id": "d1", "name": "Sticky Toffee Pudding", "price": 7.00},
        {"id": "d2", "name": "Eton Mess", "price": 6.50},
        {"id": "d3", "name": "Cheese Board", "price": 9.00},
        {"id": "d4", "name": "Chocolate Brownie", "price": 6.50},
    ],
    "drinks": [
        {"id": "dr1", "name": "Real Ale (pint)", "price": 4.50},
        {"id": "dr2", "name": "Craft Lager (pint)", "price": 5.00},
        {"id": "dr3", "name": "House Wine (175ml)", "price": 6.00},
        {"id": "dr4", "name": "Soft Drink", "price": 2.50},
    ]
}

@app.route('/')
def index():
    return render_template('index.html', menu=MENU)

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == ADMIN_USERNAME and request.form['password'] == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        error = 'Invalid username or password.'
    return render_template('admin_login.html', error=error)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/api/orders', methods=['GET'])
def get_orders():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify(orders)

@app.route('/api/orders', methods=['POST'])
def place_order():
    data = request.json
    if not data.get('customer_name') or not data.get('items'):
        return jsonify({'error': 'Name and items are required'}), 400

    order = {
        'id': str(uuid.uuid4())[:8].upper(),
        'customer_name': data['customer_name'],
        'table': data.get('table', 'Takeaway'),
        'items': data['items'],
        'total': round(sum(i['price'] * i['qty'] for i in data['items']), 2),
        'notes': data.get('notes', ''),
        'status': 'pending',
        'time': datetime.now().strftime('%H:%M:%S')
    }
    orders.append(order)
    return jsonify({'success': True, 'order_id': order['id'], 'total': order['total']}), 201

@app.route('/api/orders/<order_id>', methods=['PATCH'])
def update_order(order_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.json
    new_status = data.get('status')
    if new_status not in ('accepted', 'rejected', 'completed'):
        return jsonify({'error': 'Invalid status'}), 400

    for order in orders:
        if order['id'] == order_id:
            order['status'] = new_status
            return jsonify({'success': True})

    return jsonify({'error': 'Order not found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
