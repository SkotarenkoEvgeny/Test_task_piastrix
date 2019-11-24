from flask import Flask, render_template, request, redirect

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import requests
import datetime

from data_preparation import sign_creator, clear_number, sign_creator_bill, \
    sign_creator_invoice
from database_setup import Base, Log_table

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def log_writer(amount, currency, payment_id, description):
    """
    write the log to database
    """
    new_pay = Log_table(amount=amount,
                        currency=currency,
                        send_time=datetime.datetime.now().strftime(
                            "%d-%m-%Y %H:%M"),
                        payment_id=payment_id,
                        description=description)
    session.add(new_pay)
    session.commit()


@app.route('/')
def index_page():
    return render_template('index.html')


@app.route('/currency_choice', methods=['POST'])
def currency_choice():
    # read the posted values from the UI
    if request.method == 'POST':

        raw_currency = request.form.get("currency")
        raw_amount = request.form.get("amount")
        amount = clear_number(raw_amount)
        raw_description = request.form.get("description")
        if raw_currency == "978":
            """
            If currency = EUR(code 643) use protocol PAY (str. 3)
            """
            """
            my assumption is that when a client logs in,
            he has "shop_id", "shop_order_id"
            """
            shop_id = "5"
            shop_order_id = 101

            sign = sign_creator(amount=amount,
                                currency=raw_currency,
                                shop_id=shop_id,
                                shop_order_id=shop_order_id)
            form_data = {
                "amount": amount,
                "currency": raw_currency,
                "shop_id": shop_id,
                "sign": sign,
                "shop_order_id": shop_order_id,
                "description": raw_description
            }
            log_writer(amount=amount, currency=raw_currency,
                       payment_id='EUR_PAY', description=raw_description)
            return render_template('pay_form.html', form_data=form_data)

        if raw_currency == "840":
            """
            If currency = USD(code 840) use API payment (Bill method, page 4) in Piastrix currency
            """
            """
            my assumption is that when a client logs in,
            he has "shop_id", "shop_order_id"
            """
            shop_id = "5"
            shop_order_id = 123456

            sign = sign_creator_bill(amount=amount,
                                     currency=raw_currency,
                                     shop_id=shop_id,
                                     shop_order_id=shop_order_id)

            form_data = {"payer_currency": raw_currency,
                         "shop_amount": amount,
                         "shop_currency": raw_currency,
                         "shop_id": shop_id,
                         "shop_order_id": shop_order_id,
                         "sign": sign}
            url = "https://core.piastrix.com/bill/create"
            response = requests.post(url, headers={
                'Content-Type': 'application/json'},
                                     json=form_data)

            raw_json_response = response.json()
            error_code = raw_json_response['error_code']
            if error_code == 0:
                log_writer(amount=amount, currency=raw_currency,
                           payment_id='USD_Bill', description=raw_description)
                return redirect(raw_json_response['data']['url'], code=307)
            else:
                return "<h1>Error: {}</h1>".format(raw_json_response['message'])

        if raw_currency == "643":
            """
            If currency = RUB(code 643) use API payment (invoice method, page 6) in Piastrix currency
            """
            """
            my assumption is that when a client logs in,
            he has "shop_id", "shop_order_id"
            """
            shop_id = "5"
            shop_order_id = 123456
            payway = "payeer_rub"

            sign = sign_creator_invoice(amount=amount,
                                        currency=raw_currency,
                                        shop_id=shop_id,
                                        shop_order_id=shop_order_id,
                                        payway=payway)

            form_data = {"amount": amount,
                         "currency": raw_currency,
                         "payway": payway,
                         "shop_id": shop_id,
                         "shop_order_id": shop_order_id,
                         "sign": sign}
            url = "https://core.piastrix.com/invoice/create"
            response = requests.post(url, headers={
                'Content-Type': 'application/json'},
                                     json=form_data)
            raw_json_response = response.json()
            error_code = raw_json_response['error_code']
            if error_code == 0:
                form_data = {"method": raw_json_response['data']['method'],
                             "url": raw_json_response['data']['url'],
                             "lang": raw_json_response['data']['data']['lang'],
                             "m_curorderid": raw_json_response['data']['data'][
                                 'm_curorderid'],
                             "m_historyid": raw_json_response['data']['data'][
                                 'm_historyid'],
                             "m_historytm": raw_json_response['data']['data'][
                                 'm_historytm'],
                             "referer": raw_json_response['data']['data'][
                                 'referer']}
                log_writer(amount=amount, currency=raw_currency,
                           payment_id='RUB_invoice',
                           description=raw_description)
                return render_template('invoice_form.html', form_data=form_data)
            else:
                return "<h1>Error: {}</h1>".format(raw_json_response['message'])


if __name__ == '__main__':
    # app.run()
    app.run(debug=True)
