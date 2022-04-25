from datetime import date


def pars_user_data(user_data: str) -> dict:
    cur_date = date.today().strftime("%d.%m.%Y")
    obj = {'sum': None, 'date': cur_date}
    user_data = user_data.strip().split(' ')
    if len(user_data) > 2 or len(user_data) < 1:
        return obj
    if not user_data[0].isdigit():
        return obj
    for index, key in enumerate(obj.keys()):
        data = None
        try:
            data = user_data[index]
        except IndexError:
            pass
        if data:
            obj[key] = user_data[index]
    return obj

