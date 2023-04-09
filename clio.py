from recipy import demand_invoice, recipients_name, type_of_tracer


def clio_bulk(file_clio):
    text = file_clio
    line_activ = text[6].split()
    activ_synth = line_activ[2]
    time_synth = line_activ[6]
    line_series = text[1].split()
    line_voleum1 = text[7].split()
    line_voleum2 = text[8].split()
    from_sync_voleum = line_voleum1[2]
    predelution_voleum = line_voleum2[4]
    delution_voleum = line_voleum2[8]
    seriers = line_series[2]
    tracer = type_of_tracer(seriers)
    voleum_synth = float(from_sync_voleum.replace(',', ".")) + float(predelution_voleum.replace(',', ".")) + float(delution_voleum.replace(',', ".")) # Все обьемый в clio через запятую, питон работает через точку
    return (float(activ_synth.replace(',', ".")),
            voleum_synth,
            time_synth,
            seriers,
            tracer)


def clio_vials(file_clio, seriers):
    text = file_clio
    del text[0:12]
    text.pop(-1)
    text.pop(-1)
    # print(text)
    vials = []
    count = 1
    sum_voluem = 0
    sum_activ = 0
    time, code_vial, voluem_in_vial, activ_in_vial = 0, 0, 0, 0
    for line in text:
        line = line.split()
        # print(line)
        if count == 3:
            if 'WASH' in code_vial or 'wash' in code_vial or 'BPT' in code_vial:
                time = line[0]
            else:
                time = line[1]
            if "ARHIV" in code_vial:
                code_vial = 'архив'
            voluem_in_vial = "0" + voluem_in_vial
            sum_voluem += float(voluem_in_vial.replace(',', "."))
            sum_activ += float(activ_in_vial.replace(',', "."))
            vials.append({"Код флакона": code_vial,
                          "Активность во флаконе": activ_in_vial,
                          "Обьем во флаконе": voluem_in_vial,
                          "Назначение": recipients_name(code_vial),
                          "Время фасовки": time,
                          "Заявка": demand_invoice(code_vial, seriers),
                          })
            count = 1
        elif count == 2:
            code_vial = line[1]
            activ_in_vial = line[6]
            voluem_in_vial = line[12]
            count += 1
        elif count == 1:
            count += 1
    return vials, sum_voluem, sum_activ