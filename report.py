#!/usr/bin/python3
"""
report.py - simple program for generating reports in the Software
manufacturing technology course of Petrozavodsk State University
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
import requests
import json
import datetime
import sys
from bs4 import BeautifulSoup

# Файл с информацией о проекте
jsonFile = "project_info.json"

# Файл справки
helpMe = '''
Использование: report.py [начальная дата] [конечная дата]
Формат даты: дд.мм.гггг
Оба параметра являются обязательными, если не используются дополнительные параметры.

Дополнительные параметры:
  -h, --help    Показать эту справку
'''


class ProjectMember:
    def __init__(self, name, reportURL: str):
        self.name = name
        self.reportURL = reportURL
        self.allTime = 0.0
        self.currentTime = 0.0


if __name__ == "__main__":
    # Вызов справки
    if len(sys.argv) == 2 and (sys.argv[-1] == "-h" or sys.argv[-1] == "--help"):
        print("report.py: программа для генерации отчётов по курсу ТТПО Петрозаводского государственного университета.")
        print(helpMe)
        sys.exit(0)

    # Если параметров вызова не 3, вывести ошибку и справку
    if len(sys.argv) != 3:
        print("Ошибка: Параметры указаны неверно")
        print(helpMe)
        sys.exit(1)

    # Промежуток времени из параметров вызова
    try:
        startDate = datetime.datetime.strptime(sys.argv[1], '%d.%m.%Y')
        endDate = datetime.datetime.strptime(sys.argv[2], '%d.%m.%Y')
    except ValueError:
        print("Ошибка: Некорректный формат даты")
        print(helpMe)
        sys.exit(1)

    # Проверка на корректность ввода даты
    if startDate > endDate:
        print("Ошибка: Начальная дата не может быть больше конечной даты")
        print(helpMe)
        sys.exit(1)

    # Импорт информации о проекте
    try:
        with open(jsonFile) as f:
            projectData = json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{jsonFile}' не найден")
        sys.exit(1)
    except PermissionError:
        print(f"Ошибка: Файл '{jsonFile}' недоступен")
        sys.exit(1)

    # Создание списка участников
    membersList = []
    try:
        for m in projectData['members']:
            membersList.append(ProjectMember(m['memberName'], m['reportURL']))
    except KeyError as e:
        print(f"Ошибка: отсутствует ключ {e} в '{m}'")
        sys.exit(1)

    # Чтение отчётов
    for m in membersList:
        # Получение отчёта из URL
        try:
            response = requests.get(m.reportURL)
            soup = BeautifulSoup(response.content, "html.parser")
            report = list(filter(None, soup.find("pre", class_="report").text.split("\n")))
        except requests.exceptions.InvalidSchema:
            print(f"Ошибка: Некорректный reportURL у участника '{m.name}'")
            sys.exit(1)
        except requests.exceptions.MissingSchema:
            print(f"Ошибка: Некорректный reportURL у участника '{m.name}'")
            sys.exit(1)
        except AttributeError:
            print(f"Ошибка: Отчёт участника '{m.name}' не найден по адресу '{m.reportURL}'")
            print("Может быть, страница отчёта оформлена неправильно? (См. файл README)")
            sys.exit(1)
        # Подсчёт времени
        for item in report:
            params = item.split(' ', 3)
            # [0] - дата, [2] - время
            m.allTime += float(params[2])
            if startDate <= datetime.datetime.strptime(params[0], "%d.%m.%Y") <= endDate:
                m.currentTime += float(params[2])

    # Вывод отчёта
    print("ОТЧЕТ О ТЕКУЩЕМ СОСТОЯНИИ ПРОЕКТА")
    print()
    print(f"Название проекта:       {projectData['projectName']}")
    print(f"Период:                 {startDate.strftime('%d.%m.%Y')} - {endDate.strftime('%d.%m.%Y')}")
    print()
    print()
    print("Участник                В этот период   Всего часов")
    print("------------------------------------------------")
    for m in membersList:
        print(m.name, end='')
        for i in range(24 - len(m.name)):
            print(' ', end='')
        print(str(m.currentTime), end='')
        for i in range(16 - len(str(m.currentTime))):
            print(' ', end='')
        print(str(m.allTime))
    print()
    print()
    print("Текущее состояние проекта")
    print("------------------------------------------------")
    print()
    print()
    print("Завершенные документы (название и ссылка)")
    print("------------------------------------------------")
    print()
    print()
    print("Отклонения/комментарии менеджмента")
    print("------------------------------------------------")
    print()
