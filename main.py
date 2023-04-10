import re
import glob

from theodorico import theodorico_bulk, theodorico_vials
from clio import clio_bulk, clio_vials
from write_read import write_excel, read_pdf_files_in_folder


def parsing(device, file_bulk, file_vials):
    if device == "clio":
        (BULK_Activity,
         volume,
         time_of_sert,
         seriers,
         tracer) = clio_bulk(file_bulk)
        print("Балк прочитан")
        (vials,
         sum_voluem_in_vials,
         sum_activ_in_vials) = clio_vials(file_vials, seriers)
        print(f"Виалки прочитаны. Серия: {seriers}, Обьем серии: {volume}, Активность: {BULK_Activity}, Время изготовления: {time_of_sert}")
        ostatok_voluem = volume - sum_voluem_in_vials
        ostatok_activ = BULK_Activity - sum_activ_in_vials
    elif device == "theodorico":
        (BULK_Activity,
         volume,
         time_of_sert,
         ostatok_voluem,
         ostatok_activ) = theodorico_bulk(file_bulk)
        print("Балк прочитан.")
        vials, tracer, seriers = theodorico_vials(file_vials)
        print(f"Виалки прочитаны. Серия: {seriers}, Обьем серии: {volume}, Активность: {BULK_Activity}, Время изготовления: {time_of_sert}")
    else:
        print(" Нетю файликов")
    return (BULK_Activity,
            volume,
            time_of_sert,
            seriers,
            tracer,
            ostatok_voluem,
            ostatok_activ, vials)


if __name__ == "__main__":
    pdf_files = glob.glob('*.pdf')  # Смотрим все файлики
    print("<----------------------Погнали----------------------------------->")
    device, file_bulk, file_vials, synth = read_pdf_files_in_folder(pdf_files)
    print("<----------------------Парсим------------------------------------>")

    (BULK_Activity,
     volume,
     time_of_sert,
     seriers,
     tracer,
     ostatok_voluem,
     ostatok_activ,
     vials) = parsing(device, file_bulk, file_vials)

    print("<----------------------Закончили парсинг------------------------->")
    print("<------------ Передаем данные парсинга в словарь----------------->")
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

    print("<----------------------Записываем в файл------------------------->")
    write_excel(data_in_report, vials, seriers, ostatok_voluem, ostatok_activ)
    print("<----------------------------------Конец------------------------->")
