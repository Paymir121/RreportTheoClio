from typing import List, Dict, Union
from recipy import read_pdf
from synthese import synthese_report
from wrapper import timer
import pandas as pd


@timer
def read_pdf_files_in_folder(pdf_files: List[str]) -> List[str]:
    """Читаем все pdf файлы и среди них ищем те кто содержат ключевые слова"""
    device: str = 'Пусто'
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
    try:
        if device == "clio":
            files = {"Фасовщик": device,
                     "Отчет Балка": file_clio,
                     "Отчет с флаконами": file_clio,
                     "Отчет с модуля синтеза": synth,
                     }
            return files
        else:
            files = {"Фасовщик": device,
                     "Отчет Балка": file_bulk_theodorico,
                     "Отчет с флаконами": file_vials_theodorico,
                     "Отчет с модуля синтеза": synth,
                     }
            return files
    except UnboundLocalError:
        input('Аллах видит, что нет тут файлов\n')


@timer
def write_excel(data: Dict[str, Union[float, str]],
                vials: Dict[str, Union[str, float]],
                seriers: str,
                ostatok_voluem: float,
                ostatok_activ: float):
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
    input('Нажмите Enter для выхода\n')



