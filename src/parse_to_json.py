import json

# считывание данных


def parseJson(json, fileObject):
    while True:
        line = fileObject.readline().decode('utf-8')
        if not line:
            return json

        line = line.rstrip('\r\n')

        separator = line.find(":")

        if separator == -1:
            continue

        key = line[:separator]
        value = line[separator + 1:]

        if key == "UID":
            while True:
                line = fileObject.readline().decode('utf-8')

                line = line.rstrip('\r\n')

                separator = line.find(":")

                if separator != -1:
                    key = line[:separator]

                if key == "CREATED" or key == "X-GOOGLE-HANGOUT":
                    json["mailto"] = value
                    value = line[separator + 1:]
                    break
                else:
                    value += line

        if key == "BEGIN":
            if value not in json:
                json[value] = []
            json[value].append(parseJson({}, fileObject))
        elif key == "END":
            return json
        else:
            json[key] = value

# преобразование данных в нужный вид


def redact(username, data):
    for event in data:
        # удаляем из event ненужное
        del event["DTSTAMP"]
        del event["CREATED"]
        del event["DESCRIPTION"]
        del event["SEQUENCE"]
        del event["STATUS"]
        del event["TRANSP"]
        del event["LAST-MODIFIED"]
        if "VALARM" in event:
            del event["VALARM"]
        # находим и изменяем файлы об организваторе и приглашенных
        changeKey = event.keys()
        myNewKey = None
        for i in changeKey:
            if i.find("ORGANIZER") != -1:
                myNewKey = i
        # переделываем поле организатор
        if myNewKey is not None:
            event['ORGANIZER'] = event.get(myNewKey)
            separator = event["mailto"].find("mailto:")
            if separator != -1:
                event['ORGANIZER'] = event['ORGANIZER'][7:]
            del event[myNewKey]
        else:
            del event["mailto"]
            event["ORGANIZER"] = username
            event["VISITORS"] = []

        # переделываем поле приглашенных, если они есть
        if "mailto" in event:
            line = event["mailto"]
            separator = event["mailto"].find("mailto:")
            visitors = []

            while separator != -1:
                line = line[separator + 7:]  # взяли все что после mailto
                sep = line.find("ATTENDEE;")  # считываем до att и короче посде mailto берем все email
                if sep == -1:
                    visitors.append(line)
                    break
                visitors.append(line[:sep])
                separator = line.find("mailto:")
            event["VISITORS"] = visitors
            del event["mailto"]
    return data


def createjson (filename):
    result = parseJson({}, filename)

    myData = result.get('VCALENDAR')[0]  # извлекаем наш календарь
    username = myData['X-WR-CALNAME']   # извлекаем имя владельца

    # оставляем только поля event
    myData = myData['VEVENT']
    myData = redact(username, myData) # изменяем данные как необходимо

    with open('./data/' + username + '.json', 'w') as outfile:  # создаем json файл
        json.dump(myData, outfile, indent=4, ensure_ascii=False)

    return username
