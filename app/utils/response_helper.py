# API文件中定義的回傳格式
def resp(errMsg, data=None):
    resp = {"code": "0", "error": ""}

    if errMsg is not None:
        resp["code"] = "1"
        resp["error"] = errMsg
    else:
        resp["data"] = data

    return resp