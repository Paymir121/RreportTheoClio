from recipy import demand_invoice, recipients_name, type_of_tracer


def theodorico_bulk(file_bulk_theodorico):
    text = file_bulk_theodorico
    del text[0:8]
    text.pop(-1)
    text.pop(-1)
    max_voleum_synth = 0
    for index, line in enumerate(text):
        line = line.split()
        activ = float(line[-2])
        voleum = float(line[-1])
        time = line[1]

        if max_voleum_synth < voleum and activ > 20000:
            max_activ_synth = activ
            max_voleum_synth = voleum
            max_time_synth = time
            next_line = text[index+1]
            next_line = next_line.split()
            ostatok_valuem = next_line[-1]
            ostatok_activ = next_line[-2]

    return (max_activ_synth,
            max_voleum_synth,
            max_time_synth,
            ostatok_valuem,
            ostatok_activ,
            )


def theodorico_vials(file_vials_theodorico):
    text = file_vials_theodorico
    if "ОТЧЁТ BULK Theodorico 2" in text:
        seriers = text[1].split() # для русского отчета
    else:
        seriers = text[2].split() # для пендоского
    seriers = seriers[1]
    tracer = type_of_tracer(seriers[1])
    del text[0:7]
    text.pop(-1)
    vials = []
    count = 1
    time, code_vial, voluem_in_vial, activ_in_vial = 0, 0, 0, 0
    for line in text:
        line = line.split()
        if count == 3:
            time = line[0]
            vials.append({"Код флакона": code_vial,
                          "Активность во флаконе": activ_in_vial,
                          "Обьем во флаконе": voluem_in_vial,
                          "Назначение": recipients_name(code_vial),
                          "Время фасовки": time,
                          "Заявка": demand_invoice(code_vial, seriers),
                          })
            count = 1
        elif count == 2:
            code_vial = line[0]
            voluem_in_vial = line[1]
            count += 1
        elif count == 1:
            activ_in_vial = line[0]
            count += 1

    return vials, tracer, seriers