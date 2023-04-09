from recipy import demand_invoice, recipients_name, type_of_tracer


def theodorico_bulk(file_bulk_theodorico):
    text = file_bulk_theodorico
    seriers = text[1].split()
    tracer = type_of_tracer(seriers[1])
    del text[0:8]
    text.pop(-1)
    text.pop(-1)
    for line in text:
        line = line.split()
        activ = float(line[-2])
        voleum = float(line[-1])
        time = line[1]

        if activ > 20000.0:
            activ_synth = activ
            voleum_synth = voleum
            time_synth = time

    return (activ_synth,
            voleum_synth,
            time_synth,
            seriers[1],
            tracer)


def theodorico_vials(file_vials_theodorico, seriers):
    text = file_vials_theodorico
    del text[0:7]
    text.pop(-1)
    vials = []
    count = 1
    sum_voluem = 0
    sum_activ = 0
    time, code_vial, voluem_in_vial, activ_in_vial = 0, 0, 0, 0
    for line in text:
        line = line.split()
        if count == 3:
            time = line[0]
            sum_voluem += float(voluem_in_vial)
            sum_activ += float(activ_in_vial)
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

    return vials, sum_voluem, sum_activ