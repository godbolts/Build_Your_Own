import random
from datetime import datetime, timedelta

def generate_czech_id_codes(num_codes):
    mass = []
    for i in range(num_codes):
        birth_date = datetime(1940, 1, 1) + timedelta(days=random.randint(0, 40000))
        year, month, day = birth_date.year, birth_date.month, birth_date.day
        date_array = [year, month, day]
        check = True
        if year < 1954:
            check = False
        year = str(date_array[0])
        day = str(date_array[2])
        birth_date_str = birth_date.strftime('%Y-%m-%d')

        gender = random.choice(['M', 'F'])
        if gender == 'F':
            date_array = [date_array[0], date_array[1] + 50, date_array[2]]
        month = str(date_array[1])
        if len(month) == 1:
            month = '0' + month
        if len(day) == 1:
            day = '0' + day

        birth_number = year[2:] + month + day

        if check:

            while True:
                serial = str(random.randint(1, 999))
                if len(serial) == 1:
                    serial = '00' + serial
                if len(serial) == 2:
                    serial = '0' + serial

                number = birth_number + serial

                check_digit = str(10 - sum([int(x) * y for x, y in zip(number, [2, 4, 8, 5, 10, 9, 7, 3, 6])]) % 11)
                if check_digit == '10':
                    check_digit = '0'
                elif check_digit == '11':
                    check_digit = '1'

                final = number + check_digit

                if int(final) % 11 == 0:
                    break

        else:
            serial = str(random.randint(100, 999))
            final = birth_number + serial

        id_code = final + ' ' + birth_date_str + ' ' + gender
        mass.append(id_code)

    return mass

id_codes = generate_czech_id_codes(10)
for id_code in id_codes:
    print(id_code)
