import pdfplumber
from typing import Union
from wrapper import timer


@timer
def synthese_report(path_pdf: str) -> Union[float, int]:
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
        return (float(activity_synth), time_of_synth)
