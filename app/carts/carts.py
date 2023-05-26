# from crypt import methods
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, session, current_app
from flask_login import current_user, login_required
from app import db
from app.models import Product
import json

carts = Blueprint('carts', __name__)


def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


@carts.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = request.form.get('quantity')
        prod = Product.query.filter_by(id=product_id).first()

        if product_id and quantity and request.method == "POST":
            DictItems = {product_id: {'name': prod.name, 'price': prod.price, 'discount': prod.discount,
                                      'category': prod.category, 'image': prod.image}}
            if 'shoppingcart' in session:
                print(session['shoppingcart'])
                if product_id in session['shoppingcart']:
                    for key, item in session['shoppingcart'].items():
                        if int(key) == int(product_id):
                            session.modified = True
                            item['quantity'] += 1
                    flash("This product is already in your cart", 'warning')
                else:
                    session['shoppingcart'] = MagerDicts(session['shoppingcart'], DictItems)
                    return redirect(request.referrer)
            else:
                session['shoppingcart'] = DictItems
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@carts.route('/cart', methods=['GET', 'POST'])
@login_required
def cart():
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        flash(f'please {current_user.username} Your cart is empty, add product to your cart to access this page...',
              'warning')
        return redirect(url_for('product.product'))

    subtotal = 0
    grandtotal = 0

    for key, product in session['shoppingcart'].items():
        discount = 0
        discount = (discount / 100) * float(product['price'].replace(',', ''))  # Remove the comma and convert to float
        subtotal += float(product['price'].replace(',', ''))  # Remove the comma and convert to float
        subtotal -= discount

    grandtotal = "{:,.2f}".format(subtotal)  # Format the grand total with comma as a thousand separator

    return render_template('cart.html', grandtotal=grandtotal)





@carts.route('/updatecart/<int:code>', methods=['GET', 'POST'])
def updatecart(code):
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('main.index'))
    if request.method == 'POST':
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    flash('Item is Updated!')
                    return redirect(url_for('carts,cart'))
        except Exception as e:
            print(e)
            return redirect(url_for('carts.cart'))


@carts.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('main.index'))
    try:
        session.modified = True
        for key, item in session['shoppingcart'].items():
            if int(key) == id:
                session['shoppingcart'].pop(key, None)
                return redirect(url_for('carts.cart'))
    except Exception as e:
        print(e)
        return redirect(url_for('carts.cart'))


@carts.route('/clearcart')
def clearcart():
    try:
        session.pop('shoppingcart', None)
        return redirect(url_for('main.index'))
    except Exception as e:
        print(e)
