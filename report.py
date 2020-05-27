#!/usr/bin/python3
"""
report - a program for generating reports
Copyright (C) 2020  Konstantin Artemchuk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import argparse
import datetime
import json
import requests
from bs4 import BeautifulSoup

# Файл с информацией о проекте
jsonFile = "project_info.json"


def createParser():
    parser = argparse.ArgumentParser(description="report - программа для генерации отчётов")
    parser.add_argument("startDate",
                        type=str,
                        help="начальная дата (дд.мм.гггг)")
    parser.add_argument("endDate",
                        type=str,
                        nargs="?",
                        help="конечная дата: (дд.мм.гггг), по умолчанию = startDate + 6")
    parser.add_argument("-t", "--table",
                        action="store_true",
                        dest="table",
                        help="вывод в виде HTML таблицы")
    return parser


if __name__ == "__main__":
    # Чтение параметров вызова
    parser = createParser()
    args = parser.parse_args()

    # Чтение даты
    startDate = datetime.datetime.strptime(args.startDate, '%d.%m.%Y')
    if args.endDate:
        endDate = datetime.datetime.strptime(args.endDate, '%d.%m.%Y')
    else:
        endDate = startDate + datetime.timedelta(days=6)

    # Импорт информации о проекте
    with open(jsonFile) as f:
        projectData = json.load(f)

    # Создание списка участников
    membersList = []
    for m in projectData['members']:
        membersList.append({'name': m['memberName'],
                            'reportURL': m['reportURL'],
                            'allTime': 0.0,
                            'currentTime': 0.0
                            })

    # Чтение отчётов
    for m in membersList:
        # Получение отчёта из URL
        response = requests.get(m['reportURL'])
        soup = BeautifulSoup(response.content, "html.parser")
        report = list(filter(None, soup.find("pre", class_="report").text.split("\n")))

        # Подсчёт времени
        for item in report:
            params = item.split(' ', 3)
            # [0] - дата, [2] - время
            if datetime.datetime.strptime(params[0], "%d.%m.%Y") <= endDate:
                m['allTime'] += float(params[2])
            if startDate <= datetime.datetime.strptime(params[0], "%d.%m.%Y") <= endDate:
                m['currentTime'] += float(params[2])

    # Вывод отчёта
    if args.table:
        timeTable = '''<table class="wikitable" border="1" style="border-collapse: collapse">\
<th>Участник</th><th>В этот период</th><th>Всего часов</th>'''
        timeTable += "".join(f"\n<tr><td>{m['name']}</td><td>{m['currentTime']}</td><td>{m['allTime']}</td></tr>"
                             for m in membersList)
        timeTable += "</table>"
    else:
        timeTable = '''Участник                В этот период   Всего часов
-----------------------------------------------'''
        timeTable += "".join(f"\n{m['name']:<24}{m['currentTime']:<16}{m['allTime']}" for m in membersList)

    print(f'''ОТЧЕТ О ТЕКУЩЕМ СОСТОЯНИИ ПРОЕКТА

Название проекта:       {projectData['projectName']}
Период:                 {startDate.strftime('%d.%m.%Y')} - {endDate.strftime('%d.%m.%Y')}

{timeTable}

Текущее состояние проекта
------------------------------------------------


Завершенные документы (название и ссылка)
------------------------------------------------


Отклонения/комментарии менеджмента
------------------------------------------------
''')
