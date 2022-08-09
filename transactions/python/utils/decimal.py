from decimal import Decimal
import json

def two_decimal(number):
    TWOPLACES = Decimal(10) ** -2
    d = number
    return Decimal(d).quantize(TWOPLACES)

def default(obj):
    if isinstance(obj, Decimal):
        return str(obj)