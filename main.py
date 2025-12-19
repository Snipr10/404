import execjs
import requests
import datetime
import hashlib
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
import pymysql
DB_CONFIG = {
    "host": "192.168.5.27",
    "port": 3306,
    "user": "parser",
    "password": "9ExtUS8uRyF9FSDf",
    "database": "parser",
    "charset": "utf8mb4",
    "autocommit": False,
}




def save_neterr_events(events):
    sql = """
    INSERT INTO neterr_events
    (regin_id, created_date, errors_count, failures_count)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        errors_count   = VALUES(errors_count),
        failures_count = VALUES(failures_count);
    """

    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    data = []

    for created_date, errors, failures, regin_id in events:
        failures_decimal = (
            Decimal(str(failures))
            .quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)
        )

        data.append((
            regin_id,
            created_date,
            errors,
            failures_decimal
        ))

    try:
        cursor.executemany(sql, data)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()




def get_sphinx_id(name):
    m = hashlib.md5()
    m.update(name.encode())
    return int(str(int(m.hexdigest()[:16], 16)))


def round_down_to_15(dt: datetime) -> datetime:
    return dt.replace(
        minute=(dt.minute // 15) * 15,
        second=0,
        microsecond=0
    )


def errors_with_periods(errors: list[int], v: list, now: datetime, id_: str) -> list[tuple[datetime, int]]:
    errors = list(reversed(errors))
    v = list(reversed(v if v else []))

    result = []

    current_start = round_down_to_15(now)

    for index, count in enumerate(errors):
        value = 0
        try:
            value = v[index]
        except:
            pass
        result.append((current_start, count, value, id_))
        current_start -= timedelta(minutes=15)

    return result


urls = [
    "[62] Рязанская область,[40] Калужская область,[78] Санкт-Петербург,[16] Татарстан,[49] Магаданская область,Москва,[25] Приморский край,[89] Ямало-Ненецкий АО,[43] Кировская область,[63] Самарская область,[70] Томская область",
    "[46] Курская область,[54] Новосибирская область,[55] Омская область,[32] Брянская область,[73] Ульяновская область,[68] Тамбовская область,[18] Удмуртия,[71] Тульская область,[1] Адыгея,[13] Мордовия,[39] Калининградская область",
    "[24] Красноярский край,[08] Калмыкия,[48] Липецкая область,[35] Вологодская область,[44] Костромская область,[47] Ленинградская область,[69] Тверская область,[56] Оренбургская область,[23] Краснодарский край",
    "[61] Ростовская область,[27] Хабаровский край,[36] Воронежская область,[33] Владимирская область,[51] Мурманская область,[38] Иркутская область,[64] Саратовская область,[72] Тюменская область,[59] Пермская область",
    "[52] Нижегородская область,[74] Челябинская область,[66] Свердловская область,[19] Хакасия,[22] Алтайский край,[53] Новгородская область,[02] Башкортостан,[60] Псковская область,[21] Чувашия,[76] Ярославская область",
    "[34] Волгоградская область,[58] Пензенская область,[82] Крым,[42] Кемеровская область,[15] Северная Осетия и Алания,[11] Коми,[26] Ставропольский край,[28] Амурская область,[31] Белгородская область,[45] Курганская область",
    "[67] Смоленская область,[37] Ивановская область,[05] Дагестан,[80] ДНР,[85] Запорожская область,[86] Ханты-Мансийский АО,[83] Ненецкий АО,[10] Карелия,[75] Читинская область,[29] Архангельская область,[30] Астраханская область",
    "[41] Камчатская область,[65] Сахалинская область,[12] Марий Эл,[57] Орловская область,[81] ЛНР,[14] Саха,[17] Тыва,[4] Алтай,[03] Бурятия,[07] Кабардино-Балкария,[06] Ингушетия,[09] Карачаево-Черкесия,[95] Чечня,[84] Херсонская область",
    "[92] Севастополь,[87] Чукотский АО,[79] Еврейская АО"

]
payload = {}
headers = {
    'Accept': '*/*',
    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Referer': 'https://detector404.ru/branches/regions',
    'Sec-Fetch-Dest': 'script',
    'Sec-Fetch-Mode': 'no-cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"'
}
with open("your_script.js", "r") as f:
    js_code = f.read()
ctx = execjs.compile(js_code)
errors = {}
tokens = {}
for url in urls:
    response = requests.request("GET", f"https://detector404.ru/data.js?service={url}", headers=headers, data=payload)
    datas = response.text.split(".push(")
    errors.update(ctx.call("assertValue", datas[1][1:].split('");')[0]))
    tokens.update(ctx.call("assertValue", datas[2][1:].split('");')[0]))

result = {}
now = datetime.now()

for e, v in errors.items():
    result[e] = errors_with_periods(tokens.get(e), v, now, get_sphinx_id(e))


# events = [
#         (
#             datetime(2025, 12, 19, 19, 0),
#             12,
#             2.9188355504144976,
#             16639457515485987309
#         ),
#         (
#             datetime(2025, 12, 19, 18, 45),
#             5,
#             1.1,
#             16639457515485987309
#         ),
#     ]

save_neterr_events(list(result.values()))
