import secrets
from app.models import Product, Checkout, Payment
from flask import render_template, url_for, flash, redirect, request, abort, Blueprint, session
from app import db, mail
from app.forms import CheckoutForm, ContactForm, PaymentForm
from app.models import User
from flask_login import current_user, login_required
from flask_mail import Message
from app.users.utils import save_picture

main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def index():
    product = Product.query.all()
    return render_template("index.html", product=product)


@main.route('/about', methods=['GET', 'POST'])
def about():
    return render_template("about.html")


@main.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('product.product'))
    form = CheckoutForm()
    if form.validate_on_submit():
        try:
            subtotal = 0
            grandtotal = 0
            invoice = secrets.token_hex(5)
            customer_id = current_user.id
            product = Checkout.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(
                Checkout.id.desc()).all()
            for key, product in session['shoppingcart'].items():
                discount = 0
                discount = (discount / 100) * float(product['price'].replace(',', ''))

                subtotal += float(product['price'].replace(',', ''))
                subtotal -= discount

                grandtotal = "{:,.2f}".format(subtotal)
                user = Checkout(productsname=(product['name']), grandtotal=grandtotal, customer_id=current_user.id,
                                orders=session['shoppingcart'], invoice=secrets.token_hex(5),
                                firstname=form.firstname.data, lastname=form.lastname.data, email=form.email.data,
                                phone=form.phone.data, country=form.country.data, city=form.city.data,
                                street=form.street.data, building=form.building.data, zip=form.zip.data,
                                date_created=form.date_created.data, description=form.description.data, )
            db.session.add(user)
            db.session.commit()
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('main.payment'))
        except Exception as e:
            print(e)
            flash('something went wrong while getting order', 'danger')
            return redirect(url_for('product.product'))

    subtotal = 0
    grandtotal = 0
    invoice = secrets.token_hex(5)
    customer_id = current_user.id
    customer = User.query.filter_by(id=customer_id).first()
    orders = Checkout.query.filter_by(customer_id=customer_id, invoice=invoice).order_by(
        Checkout.id.desc()).all()
    for key, product in session['shoppingcart'].items():
        discount = 0
        discount = (discount / 100) * float(product['price'].replace(',', ''))

        subtotal += float(product['price'].replace(',', ''))
        subtotal -= discount

        grandtotal = "{:,.2f}".format(subtotal)

    return render_template('checkout.html', title='Register', invoice=invoice, customer=customer, orders=orders,
                           form=form, grandtotal=grandtotal, product=product)


@main.route('/faq', methods=['GET', 'POST'])
@login_required
def faq():
    return render_template("faq.html")


@main.route('/returnpolicy', methods=['GET', 'POST'])
def returnpolicy():
    return render_template("return.html")


@main.route('/terms', methods=['GET', 'POST'])
def terms():
    return render_template("terms.html")


@main.route('/privacy', methods=['GET', 'POST'])
def privacy():
    return render_template("privacy.html")


@main.route('/contact', methods=['GET', 'POST'])
def contact():
    user = User
    form = ContactForm()
    if form.validate_on_submit():
        msg = Message(f'New Message from {current_user.username}', sender=f'{user.email}',
                      recipients=['emeraldinteriorservices@gmail.com'])
        msg.body = f"""
           Name :  {form.name.data}

           Email :  {form.contact_email.data}

           Subject :  {form.subject.data}

           Message :  {form.message.data}
           """
        mail.send(msg)
        flash('your message have been sent', 'success')
        return redirect(url_for('main.index'))
    return render_template('contact.html', title='contact Form', form=form)


@main.route('/payment', methods=['GET', 'POST'])
@login_required
def payment():
    global image_file
    if 'shoppingcart' not in session or len(session['shoppingcart']) <= 0:
        return redirect(url_for('product.product'))
    form = PaymentForm()
    if form.validate_on_submit():
        if form.image.data:
            picture_file = save_picture(form.image.data)
            image = picture_file
        description = form.description.data
        author = current_user
        product = Payment(image=image, description=description, author=author)
        db.session.add(product)
        db.session.commit()
        flash(
            'Your Payment proof has been uploaded successfully, Admin will get back to you whenever your payment is approved!',
            'success')
        return redirect(url_for('main.thanks'))
    elif request.method == 'GET':
        image_file = url_for('static', filename='img/' + current_user.image_file)

    subtotal = 0
    grandtotal = 0
    for key, product in session['shoppingcart'].items():
        discount = 0
        discount = (discount / 100) * float(product['price'].replace(',', ''))

        subtotal += float(product['price'].replace(',', ''))
        subtotal -= discount

        grandtotal = "{:,.2f}".format(subtotal)

    return render_template('payments.html', grandtotal=grandtotal, product=product, form=form, image_file=image_file)


@main.route('/proof')
@login_required
def proof():
    payment = Payment.query.all()
    return render_template('admin/proof.html', payment=payment)


@main.route("/delete_proof/<int:payment_id>/delete", methods=['GET', 'POST'])
def delete_proof(payment_id):
    product = Payment.query.get_or_404(payment_id)
    if current_user.email != 'emeraldinteriorservices@gmail.com':
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash("the product has been deleted successfully", 'success')
    return redirect(url_for('admin.home'))
    return render_template("admin/proof.html", product=product)


@main.route("/delete_prod/<int:prod_id>/delete", methods=['GET', 'POST'])
def delete_prod(prod_id):
    prod = Product.query.get_or_404(prod_id)
    if current_user.email != 'emeraldinteriorservices@gmail.com':
        abort(403)
    db.session.delete(prod)
    db.session.commit()
    flash("the product has been deleted successfully", 'success')
    return redirect(url_for('admin.home'))
    return render_template("admin/home.html", prod=prod)


@main.route('/thanks')
@login_required
def thanks():
    return render_template('thank.html')

