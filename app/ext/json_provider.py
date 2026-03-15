import datetime
from flask.json.provider import DefaultJSONProvider
from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.ext.declarative import DeclarativeMeta
import decimal
import typing as t
import uuid
import dataclasses

def _default(obj: t.Any) -> t.Any:
    if isinstance(obj, (decimal.Decimal, uuid.UUID)):
        return str(obj)

    if dataclasses and dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)  # type: ignore[arg-type]

    if hasattr(obj, "__html__"):
        return str(obj.__html__())

    if isinstance(obj, datetime.datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')

    if isinstance(obj, datetime.date):
        return obj.strftime('%Y-%m-%d')

    if isinstance(obj, datetime.time):
        return obj.isoformat()
    
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if hasattr(obj, 'to_dict'):
        return _default(obj.to_dict())
    if isinstance(obj.__class__, DeclarativeMeta):
        return _default({i.name: getattr(obj, i.name) for i in obj.__table__.columns})
    if isinstance(obj, dict):
        for k in obj:
            try:
                if isinstance(obj[k], (datetime.datetime, datetime.date, DeclarativeMeta)):
                    obj[k] = _default(obj[k])
                else:
                    obj[k] = obj[k]
            except TypeError:
                obj[k] = None
        return obj
    if isinstance(obj, Pagination):
        data = {'total': obj.total,'rows': obj.items, 'code':0, 'msg': ''}
        return _default(data)
    if hasattr(obj, 'total') and hasattr(obj, 'items') and hasattr(obj, 'page') and hasattr(obj, 'per_page'):
        data = {'total': obj.total,'rows': obj.items, 'code':0, 'msg': ''}
        return _default(data)

    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

class CustomJSONProvider(DefaultJSONProvider):
    default = staticmethod(_default)