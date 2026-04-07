from typing import Any


from flask import jsonify
class R():
    def __init__(self) -> None:
        pass

    @classmethod
    def success(self, data = [], msg = '操作成功', code = 0) -> Any:
        return jsonify(code = code, msg = msg, data = data)

    @classmethod
    def error(self, data = [], msg = '操作失败', code = 500) -> Any:
        return jsonify(code = code, msg = msg, data = data)