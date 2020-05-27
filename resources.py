#!/usr/bin/python3
"""
resources - a program for generating reports
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
    '''# Чтение параметров вызова
    parser = createParser()
    args = parser.parse_args()

    # Чтение даты
    startDate = datetime.datetime.strptime(args.startDate, '%d.%m.%Y')
    if args.endDate:
        endDate = datetime.datetime.strptime(args.endDate, '%d.%m.%Y')
    else:
        endDate = startDate + datetime.timedelta(days=6)'''

    # Импорт информации о проекте
    with open(jsonFile) as f:
        projectData = json.load(f)

    # Создание списка участников
    symbols = {'ME': 0.0,
               'LC': 0.0,
               'PP': 0.0,
               'PR': 0.0,
               'DO': 0.0,
               'CO': 0.0,
               'TE': 0.0,
               'AD': 0.0,
               'TM': 0.0,
               'RE': 0.0,
               'RD': 0.0
               }
    membersList = []
    allTime = symbols.copy()
    allTime.update({'allTime': 0.0})
    for m in projectData['members']:
        membersList.append({'name': m['memberName'],
                            'reportURL': m['reportURL'],
                            'allTime': 0.0
                            })
        membersList[-1].update(symbols)

    # Чтение отчётов
    for m in membersList:
        # Получение отчёта из URL
        response = requests.get(m['reportURL'])
        soup = BeautifulSoup(response.content, "html.parser")
        report = list(filter(None, soup.find("pre", class_="report").text.split("\n")))

        # Подсчёт времени
        for item in report:
            params = item.split(' ', 3)
            # [0] - дата, [1] - тип, [2] - время
            m['allTime'] += float(params[2])
            m[params[1]] += float(params[2])
            allTime['allTime'] += float(params[2])
            allTime[params[1]] += float(params[2])

    # Вывод отчёта
    timeTable = '<table class="wikitable" border="1" style="border-collapse: collapse">\n<tr><th>Участник</th>'
    timeTable += "".join(f"<th>{k}</th>" for k in symbols.keys())
    timeTable += "<th>Всего часов</th></tr>\n"
    for m in membersList:
        timeTable += f"<tr><td>{m['name']}</td>"
        timeTable += "".join(f"<td>{m[k]}</td>" for k in symbols.keys())
        timeTable += f"<td>{m['allTime']}</td></tr>\n"
    timeTable += "<tr><td><b>Всего</b></td>"
    timeTable += "".join(f"<td><b>{allTime[k]}</b></td>" for k in symbols.keys())
    timeTable += f"<td><b>{allTime['allTime']}</b></td></tr>\n</table>"
    print(timeTable)
