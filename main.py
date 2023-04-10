import re
import pdfplumber
import pandas as pd
import glob

from theodorico import theodorico_bulk, theodorico_vials
from clio import clio_bulk, clio_vials
from recipy import read_pdf



def write_excel(data, vials, seriers, ostatok_voluem, ostatok_activ):
    """ Записываем необходимые данные в excel файл"""
    df = pd.DataFrame(data, index=[0])  # Добавляем инфу об серии из отчета по синтезу и балку
    df2 = pd.DataFrame(vials)
    if 'K' in seriers:
        CF18T = {"н/п": ["н/п", "н/п", "УКТ CF18T №A"],
                 "н/п1": ["н/п", "н/п", "Паспорт на OРнИ, сертификат - разрешение УКТ - RUS/7268/A-96T "], }
    else:
        CF18T = {"н/п": ["", "", ""],
                 "н/п1": ["", "", ""], }
    df3 = pd.DataFrame(CF18T)

    ostatok = {"Остаток активности": [ostatok_activ, ],
               "Остаток обьем": [ostatok_voluem, ], }
    print(ostatok)
    df4 = pd.DataFrame(ostatok)
    df = pd.concat([df, df2, ], axis=1)  # Добавляем флаконы
    df = pd.concat([df, df3, ], axis=1)  # Добавляем шляпу про контейенеы
    df = pd.concat([df, df4, ], axis=1)  # ДОбавляем шляпу про остатки
    print(df)
    df.to_excel('./report_new.xlsx')
    print("<----------------------Файл создан---------------------------------------->")
    # input('Нажмите Enter для выхода\n')


def synthese_report(path_pdf):
    """Достаем из отчета по синтезу активность пришедшую с циклотрона и время синтеза"""
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


def read_pdf_files_infolder(pdf_files):
    """Читаем все pdf файлы и среди них ищем те кто содержат ключевые слова"""
    device = ''
    for file in pdf_files:
        text = read_pdf(file)
        if "Synthesis Report" in text:
            print("Synthesis Repor найден")
            synth = synthese_report(file)
        elif "ОТЧЁТ ФАСОВКИ Theodorico 2" in text:
            print("ОТЧЁТ ФАСОВКИ Theodorico 2 найден")
            device = 'theodorico'
            file_vials_theodorico = text
        elif "Distribution report" in text:
            print("Distribution report найден")
            device = 'clio'
            file_clio = text
        elif "ОТЧЁТ BULK Theodorico 2" in text or "BULK Report" in text:
            print("ОТЧЁТ BULK Theodorico 2 найден")
            device = 'theodorico'
            file_bulk_theodorico = text

    print("<--------------------- Фасуем на ", device, " ------------------------------>")
    if device == "clio":
        return device, file_clio, file_clio, synth
    else:
        return device,  file_bulk_theodorico, file_vials_theodorico, synth


if __name__ == "__main__":
    pdf_files = glob.glob('*.pdf')  # Смотрим все файлики
    print("<----------------------Погнали--------------------------------------------->")
    device, file_bulk, file_vials, synth = read_pdf_files_infolder(pdf_files)
    print("<----------------------Парсим--------------------------------------------->")
    if device == "clio":
        BULK_Activity, volume, time_of_sert, seriers, tracer = clio_bulk(file_bulk)
        print("Балк прочитан")
        vials, sum_voluem_in_vials, sum_activ_in_vials = clio_vials(file_vials, seriers)
        print(f"Виалки прочитаны. Серия: {seriers}, Обьем серии: {volume}, Активность: {BULK_Activity}, Время изготовления: {time_of_sert}")
        ostatok_voluem = volume - sum_voluem_in_vials
        ostatok_activ = BULK_Activity - sum_activ_in_vials
    elif device == "theodorico":
        BULK_Activity, volume, time_of_sert, ostatok_voluem, ostatok_activ = theodorico_bulk(file_bulk)
        print("Балк прочитан.")
        vials, tracer, seriers = theodorico_vials(file_vials)
        print(f"Виалки прочитаны. Серия: {seriers}, Обьем серии: {volume}, Активность: {BULK_Activity}, Время изготовления: {time_of_sert}")
    else:
        print(" Нетю файликов")
    print("<------------ Передаем данные парсинга в словарь-------------------------->")
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
    print("<----------------------Закончили парсинг------------------------------------>")
    print("<----------------------Записываем в файл------------------------------------>")
    write_excel(data_in_report, vials, seriers, ostatok_voluem, ostatok_activ)
    print("<----------------------------------Конец------------------------------------>")
