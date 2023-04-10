from recipy import demand_invoice, recipients_name, type_of_tracer
from typing import List, Dict, Union
from wrapper import timer


@timer
def theodorico_bulk(file_bulk_theodorico: List[str]) -> List[Union[str, float]]:
    text = file_bulk_theodorico

    if "ОТЧЁТ BULK Theodorico 2" in text:
        leng = 'rus'
        del text[0:8]  # Убираем строчки сверху, оставляем только таблицу с данными

    else:
        leng = 'eng'
        del text[0:4]  # Убираем строчки сверху, оставляем только таблицу с данными
    text.pop(-1)  # Убираем строчки снизу
    text.pop(-1)
    max_voleum_synth, max_activ_synth, max_time_synth, ostatok_valuem, ostatok_activ = 0, 0, 0, 0, 0

    for index, line in enumerate(text):
        line = line.split()
        if leng == 'rus':  # Отчеты на русском и англ имеют разное рассположение столбцов
            activ = float(line[-3])
            voleum = float(line[-2])
        else:
            activ = float(line[-2])
            voleum = float(line[-1])
        time = line[1]
        if max_voleum_synth < voleum and activ > 20000:
            max_activ_synth = activ
            max_voleum_synth = voleum
            max_time_synth = time
            next_line = text[index+1]
            next_line = next_line.split()
            if leng == "rus":
                ostatok_valuem = next_line[-2]
                ostatok_activ = next_line[-3]
            else:
                ostatok_valuem = next_line[-1]
                ostatok_activ = next_line[-2]

    return (max_activ_synth,
            max_voleum_synth,
            max_time_synth,
            float(ostatok_valuem),
            float(ostatok_activ),
            )


@timer
def theodorico_vials(file_vials_theodorico: str) -> Union[Dict[str, Union[str, float]], str]:
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
