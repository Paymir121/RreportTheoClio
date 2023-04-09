import datetime
import re
import pdfplumber


def type_of_tracer(seriers):
    '''Возвращает короткий код для различных Tracers'''
    if 'F1' in seriers:
        return 'ФДГ, 18F'
    elif 'F2' in seriers:
        return 'ФЭТ, 18F'
    elif 'F3' in seriers:
        return 'ПСМА, 18F'
    elif 'F4' in seriers:
        return 'ФЭС, 18F'
    elif 'F5' in seriers:
        return 'ФЛТ, 18F'
    elif 'F6' in seriers:
        return 'ДОПА, 18F'


def recipients_name(code_vial):
    """Возвращает название заказчика"""
    if 'KK' in code_vial or 'Архив' in code_vial or 'ARHIV' in code_vial:
        return "Лаборатория контроля качества"
    elif 'OLD' in code_vial:
        return "Отдление лучевой диагностики ООО \"ПЭТ-Технолоджи Балашиха\""
    elif 'WASH' in code_vial or 'wash' in code_vial or 'BPT' in code_vial:
        return "мусор"
    else:
        return "ООО «РМС"

   
def data_request(seriers):
    """Дата заявки ОЛД с учетом выходных"""
    data_now = seriers[-6:][0:2] + '.' + seriers[-6:][2:4] + '.20' + seriers[-6:][4:]
    data_now = datetime.datetime.strptime(data_now, '%d.%m.%Y')
    weekd = data_now.weekday()
    if weekd == 0:
        data_now -= datetime.timedelta(days=3)  # Если понедельник 
    elif weekd == 6:
        data_now -= datetime.timedelta(days=2)  # Если воскресенье
    else:
        data_now -= datetime.timedelta(days=1)  # В другие дни
    return data_now.strftime('%d.%m.%Y')


def demand_invoice(code_vial, seriers):
    """Для ОЛД и ЛКК возвращает номер серии и дату заявки"""
    number = re.sub(r"F\w+", "", seriers)
    if 'KK' in code_vial or 'Архив' in code_vial or 'ARHIV' in code_vial:
        data = seriers[-6:][0:2] + '.' + seriers[-6:][2:4] + '.20' + seriers[-6:][4:]
        return f'№{number} от {data}'
    elif 'OLD' in code_vial:
        data = data_request(seriers)
        return f'№{number} от {data}'
    else:
        return ''


def read_pdf(path_pdf):
    """Чтение PDF файлов"""
    with pdfplumber.open(path_pdf) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        text = re.split("\n", text)
        return text