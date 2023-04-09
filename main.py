import re
import pdfplumber
import pandas as pd
import glob

from theodorico import theodorico_bulk, theodorico_vials
from clio import clio_bulk, clio_vials
from recipy import read_pdf


def write_excel(data, vials, seriers, sum_voluem, ostatok_activ):
    df = pd.DataFrame(data, index=[0])# Добавляем инфу об серии из отчета по синтезу и балку
    df2 = pd.DataFrame(vials)
    if 'K' in seriers:
        CF18T = {"н/п": ["н/п", "н/п", "УКТ CF18T №A"],
                 "н/п1": ["н/п", "н/п", "Паспорт на OРнИ, сертификат - разрешение УКТ - RUS/7268/A-96T "], }
    else:
        CF18T = {"н/п": ["", "", ""],
                 "н/п1": ["", "", ""], }
    df3 = pd.DataFrame(CF18T)
    ostatok = {"активность во флаконах": [ostatok_activ],
               "обьем во флаконах": [sum_voluem], }
    df4 = pd.DataFrame(ostatok)
    df = pd.concat([df, df2, ], axis=1) # Добавляем флаконы
    df = pd.concat([df, df3, ], axis=1) # Добавляем шляпу про контейенеы
    df = pd.concat([df, df4, ], axis=1) # ДОбавляем шляпу про остатки 
    print(df)
    # df.to_excel('./teams.xlsx')


def synthese_report():
    path_pdf = 'Synthesis Report.pdf'
    with pdfplumber.open(path_pdf) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        text = text.split()
        try:
            time_of_synth = text[text.index("min.")-1]
        except ValueError:
            print('В отчете не найдена продолжительность синтеза')
        try:
            activity_synth = text[text.index("MBq")-1]
        except ValueError:
            print('В отчете не найдена активность изотопа')
        time_of_synth
        return (activity_synth, time_of_synth)


if __name__ == "__main__":
    pdf_files = glob.glob('*.pdf') # Смотрим все файлики
    print("<----------------------Погнали------------------------------------>")
    device = ''
    for file in pdf_files:
        text = read_pdf(file)
        if "Synthesis Report" in text:
            print("Synthesis Repor найден")
            synth = synthese_report()
        elif "ОТЧЁТ ФАСОВКИ Theodorico 2" in text:
            print("ОТЧЁТ ФАСОВКИ Theodorico 2 найден")
            device = 'theodorico'
            file_vials_theodorico = text
        elif "Distribution report" in text:
            print("Distribution report найден")
            device = 'clio'
            file_clio = text
        elif "ОТЧЁТ BULK Theodorico 2" in text:
            print("ОТЧЁТ BULK Theodorico 2 найден")
            device = 'theodorico'
            file_bulk_theodorico = text
    print("<-------------- Фасуем на ", device, " --------------------->")
    if device == "clio":
        BULK_Activity, volume, time_of_sert, seriers, tracer = clio_bulk(file_clio)
        print("Балк прочитан")
        vials, sum_voluem_in_vials, sum_activ_in_vials = clio_vials(file_clio, seriers)
        print("Виалки прочитаны")
    elif device == "theodorico":
        BULK_Activity, volume, time_of_sert, seriers, tracer = theodorico_bulk(file_bulk_theodorico)
        print("Балк прочитан")
        vials, sum_voluem_in_vials, sum_activ_in_vials = theodorico_vials(file_vials_theodorico, seriers)
        print("Виалки прочитаны")
    else:
        print(" Нетю файликов")

    data_in_report = {
        "Активность пришедшей на модуль": synth[0],
        "Tracer": tracer,
        "Номер серии": seriers,
        "Время синеза": synth[1],
        "Активность в фасовщике": BULK_Activity,
        "Обьем серии": volume,
        "Время производства": time_of_sert,
        "Номер паспорт": re.sub(r"\d{6}", "", seriers),
    }
    ostatok_voluem = volume - sum_voluem_in_vials
    ostatok_activ = BULK_Activity - sum_activ_in_vials
    print("<----------------------Закончили парсинг------------------------------------>")
    print("<----------------------Записываем в файл------------------------------------>")
    write_excel(data_in_report, vials, seriers, ostatok_voluem, ostatok_activ)
    print("<----------------------Конец------------------------------------>")