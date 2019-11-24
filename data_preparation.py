from hashlib import sha256

shop_id = '5'
secretKey = 'SecretKey01'
payway = 'payeer_rub'


def sign_creator(amount, currency, shop_id, shop_order_id, secretKey=secretKey):
    """
    for EUR(code 978) use protocol PAY (str. 3)
    """
    raw_data = '{}:{}:{}:{}{}'.format(amount, currency, shop_id,
                                      str(shop_order_id), secretKey)
    return sha256(raw_data.encode('utf-8')).hexdigest()


def sign_creator_bill(amount, currency, shop_id, shop_order_id,
                      secretKey=secretKey):
    """
    USD(code 643) use API payment (Bill method, page 4)
    """
    raw_data = '{}:{}:{}:{}:{}{}'.format(currency, amount, currency, shop_id,
                                         str(shop_order_id), secretKey)
    return sha256(raw_data.encode('utf-8')).hexdigest()


def sign_creator_invoice(amount, currency, payway, shop_id, shop_order_id,
                         secretKey=secretKey):
    """
    for RUB(code 643) use protocol invoice (str. 3)
    """
    raw_data = '{}:{}:{}:{}:{}{}'.format(amount, currency, payway, shop_id,
                                         str(shop_order_id), secretKey)
    return sha256(raw_data.encode('utf-8')).hexdigest()


def clear_number(number):
    """
    :param number: str with 0-2 number after '.'
    :return: str  as example 10.00
    """
    return format(float(number), '.2f')
