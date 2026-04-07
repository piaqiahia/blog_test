from decimal import Decimal

def isEmpty(s:str)->bool:
    if not s:
        return True
    if len(s) > 0:
        return False
    else:
        return True
    
def to_str(d : Decimal, format:str = '0.00')->str:
    return str(Decimal(d).quantize(Decimal(format)))