import re
import glob
from typing import List, Dict, Union

from theodorico import theodorico_bulk, theodorico_vials
from clio import clio
from write_read import write_excel, read_pdf_files_in_folder


def parsing(device: str, file_bulk: List[str], file_vials: List[str]) -> Dict[str, Union[str, float]]:
    if device == "clio":
        result = clio(file_bulk)
        print("Балк прочитан")
        print(f"Виалки прочитаны. Серия: {result['Серия']},")
        print(f"Обьем серии: {result['Обьем с фасовщика']},")
        print(f"Активность: {result['Активность с фасовщика']},")
        print(f"Время изготовления: {result['Время с фасовщика']}")
        print(result["Препарат"])
        result["остаток обьема"] = result['Обьем с фасовщика'] - result["Обьем в виалках"]
        result["остаток активности"] = result['Активность с фасовщика'] - result["Активность в виалках"]
    elif device == "theodorico":
        result = theodorico_bulk(file_bulk)
        print("Балк прочитан.")
        result["Виалки"], result["Препарат"], result["Серия"] = theodorico_vials(file_vials)
        print(f"Виалки прочитаны. Серия: {result['Серия']},")
        print(f"Обьем серии: {result['Обьем с фасовщика']},")
        print(f"Активность: {result['Активность с фасовщика']},")
        print(f"Время изготовления: {result['Время с фасовщика']}")
        print(result["Препарат"])
    else:
        print(" Нетю файликов")
    return result


if __name__ == "__main__":
    pdf_files = glob.glob('*.pdf')  # Смотрим все файлики
    print("<----------------------Погнали----------------------------------->")
    files = read_pdf_files_in_folder(pdf_files)
    print("<----------------------Парсим------------------------------------>")
    result_parsing = parsing(files["Фасовщик"],
                             files["Отчет Балка"],
                             files["Отчет с флаконами"])
    activity_synth, time_of_synth = files["Отчет с модуля синтеза"]
    print("<----------------------Закончили парсинг------------------------->")
    print("<------------ Передаем данные парсинга в словарь----------------->")
    data_in_report = {
        "Активность пришедшей на модуль": activity_synth,
        "Tracer": result_parsing["Препарат"],
        "Номер серии": result_parsing["Серия"],
        "Время синеза": time_of_synth,
        "Активность в фасовщике": result_parsing['Активность с фасовщика'],
        "Обьем серии": result_parsing['Обьем с фасовщика'],
        "Время производства": result_parsing['Время с фасовщика'],
        "Номер паспорт": re.sub(r"\d{6}", "", result_parsing["Серия"]),
    }

    print("<----------------------Записываем в файл------------------------->")
    write_excel(data_in_report,
                result_parsing["Виалки"],
                result_parsing["Серия"],
                result_parsing["остаток обьема"],
                result_parsing["остаток активности"])
    print("<----------------------------------Конец------------------------->")
