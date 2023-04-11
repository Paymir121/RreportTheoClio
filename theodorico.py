from recipy import demand_invoice, recipients_name, type_of_tracer
from typing import List, Dict, Union
from wrapper import timer


@timer
def theodorico_bulk(file_bulk_theodorico: List[str]) -> Dict[str, Union[str, float]]:
    text = file_bulk_theodorico

    if "ОТЧЁТ BULK Theodorico 2" in text:
        leng = 'rus'
        del text[0:8]  # Убираем строчки сверху, оставляем только таблицу с данными

    else:
        leng = 'eng'
        del text[0:4]  # Убираем строчки сверху, оставляем только таблицу с данными
    text.pop(-1)  # Убираем строчки снизу
    text.pop(-1)
    result = {}
    result["Активность с фасовщика"] = 0
    for index, line in enumerate(text):
        line = line.split()
        if leng == 'rus':  # Отчеты на русском и англ имеют разное рассположение столбцов
            activ = float(line[-3])
            voleum = float(line[-2])
        else:
            activ = float(line[-2])
            voleum = float(line[-1])
        time = line[1]
        if result["Активность с фасовщика"] < voleum and activ > 20000:
            result["Активность с фасовщика"] = activ
            result["Обьем с фасовщика"] = voleum
            result["Время с фасовщика"] = time
            next_line = text[index+1]
            next_line = next_line.split()
            if leng == "rus":
                result["остаток обьема"] = next_line[-2]
                result["остаток активности"] = next_line[-3]
            else:
                result["остаток обьема"] = next_line[-1]
                result["остаток активности"] = next_line[-2]

    return result


@timer
def theodorico_vials(file_vials_theodorico: List[str]) -> Union[str, List[Dict[str, Union[str, float]]]]:
    text = file_vials_theodorico
    seriers = text[2].split()
    seriers = seriers[1]
    tracer = type_of_tracer(seriers)
    del text[0:7]  # Убираем строчки сверху, оставляем только таблицу с данными
    text.pop(-1)  # Убираем строчки снизу
    vials = []
    count = 1
    time, code_vial, voluem_in_vial, activ_in_vial = 0, 0, 0, 0
    for line in text:
        line = line.split()
        if count == 3:  # Так как каждая строка в таблицу содержит в себе 3 различных строк, то их нужно прочитывать по разному. В 3 строчке есть только время замера
            time = line[0]
            vials.append({"Код флакона": code_vial,
                          "Активность во флаконе": float(activ_in_vial),
                          "Обьем во флаконе": float(voluem_in_vial),
                          "Назначение": recipients_name(code_vial),
                          "Время фасовки": time,
                          "Заявка": demand_invoice(code_vial, seriers),
                          })
            count = 1
        elif count == 2:  # Во второй строке содержится код флакона и обьем
            code_vial = line[0]
            voluem_in_vial = line[1]
            count += 1
        elif count == 1:  # Во первой строке содержится активность
            activ_in_vial = line[0]
            count += 1

    return vials, tracer, seriers
