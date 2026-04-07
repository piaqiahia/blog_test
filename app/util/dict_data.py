from app.model import DictData

def get_dict_data(dict_type):
    """根据字典类型获取字典数据"""
    list = DictData.query.filter(DictData.dict_type == dict_type, DictData.status == 0).\
        order_by(DictData.sort.asc()).all()
    return list

def get_label_by_value(dict_datas, value):
    """根据字典列表获取字典label"""
    for d in dict_datas:
        if str(d.value) == str(value):
            return d.label
    return ''