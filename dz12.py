from collections import UserDict
from collections.abc import Iterator
from datetime import datetime
from pickle import dump, load

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_value):
        self.__value = new_value

class Phone(Field):
    def __init__(self, value):
        self.__value = value

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_value):
        if self.__is_phone(new_value):
            raise ValueError("WrongPhone")
        self.__value = new_value

    def __is_phone(self, user_data):
        return not user_data.isnumeric() or len(user_data) != 10
    
class Birthday(Field):
    def __init__(self, value):
        self.__value = datetime(*value)

    @property
    def value(self):
        return self.__value
    
    @value.setter
    def value(self, new_value):
        self.__value = datetime(*new_value)
        today_date = datetime.now()

        # Перевірка на правильність дня народження - якщо ДН відбувся у попередні 100 років, то ДН приймається
        if not datetime(today_date.year - 100, today_date.month, today_date.day) <= self.birthday_date <= today_date:
            self.__value = None
            raise ValueError("WrongBirthdayDate")

class Record:
    def __init__(self, name, birthday=None):
        self.name = Name(name)
        self.phones = []
        if birthday:
            self.birthday = Birthday(birthday)

    def add_phone(self, user_data):
        phone = Phone(user_data)
        self.phones.append(phone)

    def remove_phone(self, user_data):
        for phone in self.phones:
            if phone.value == user_data:
                self.phones.remove(phone)
                break
        else:
            raise ValueError("NoSuchRecord")

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                self.phones.remove(phone)
                self.add_phone(new_phone)
                break
        else:
            raise ValueError("NoSuchRecord")
    
    def find_phone(self, user_data):
        for phone in self.phones:
            if phone.value == user_data:
                return phone
            else:
                raise ValueError("NoSuchRecord")
        
    def add_birthday(self, user_data):
        self.birthday = Birthday(user_data)
    
    def days_to_birthday(self):
        if hasattr(self, "birthday"):

            birthday_date = self.birthday.value.date()
            today = datetime.today().date()
            next_birthday = birthday_date.replace(year=today.year)  # Дата дня народження у поточному році

            if next_birthday < today:                               # Якщо день народження у поточному році вже минув...
                next_birthday = next_birthday.replace(year=today.year + 1)  # встановлюємо ДН на наступний рік

            days_untill_birthday = (next_birthday - today).days     # Отримуємо кількість днів
            
            return days_untill_birthday

    def __str__(self):
        bday = ""
        if hasattr(self, "birthday"):                               # Якщо доданий ДН, то під час друку запису покажемо його
            bday = f", birthday: {self.birthday.value.strftime("%m-%d-%Y")}"
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}" + bday
    
    def simple_str(self):
        return f"{self.name.value} {' '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def __init__(self, n=3):
        super().__init__()
        self.n = n                          # За замовчуванням 3 (три) записи на сторінку
        self.keys = list(self.data.keys())  # Ключі для ітерації
        self.current_index = 0              # Поточний індекс

    def add_record(self, record: Record):
        self.data[record.name.value] = record
        self.keys = list(self.data.keys())  # Оновлюємо ключі для ітерації

    def find(self, user_data):

        result = ""

        for i in self.keys:                         # Перебираємо ключі у книзі
            j = self.data[i].simple_str()           # З даних робимо рядки
            if j.lower().find(user_data) != -1:     # Якщо рядок для пошуку присутній в рядку з даними
                result += j + "\n"                  # то додаємо до результату

        return result[:-1]                          # Повертаємо результат

    def delete(self, user_data):
        if user_data in self.data:
            del self.data[user_data]
        else:
            raise ValueError("NoSuchRecord")
        self.keys = list(self.data.keys())   # Оновлюємо ключі для ітерації
        
    def __str__(self) -> str:
        book_data = ""
        for i in self.data:
            book_data += f"{self.data[i]}\n"
        return book_data[:-1]
    
    def __iter__(self) -> Iterator:
        return self
    
    def __next__(self):
        if self.current_index >= len(self.keys):
            raise StopIteration  # Коли досягли кінця словника
        
        # Беремо наступні N ключів
        end_index = min(self.current_index + self.n, len(self.keys))
        current_keys = self.keys[self.current_index:end_index]
        
        # Оновлюємо індекс на наступну групу ключів
        self.current_index = end_index
        
        current_book_data = ""
        for i in current_keys:
            current_book_data += f"{self.data[i]}\n"
        return current_book_data[:-1]
    
    def set_records_per_page(self, n):
        self.n = n

    def save_to_file(self, filename):
        with open(filename, "wb") as file:
            dump(self, file)

    def read_from_file(self, filename):
        try:
            with open(filename, "rb") as file:
                result = load(file)
            return result
        except:
            return None


if __name__ == "__main__":
    # Створення нової адресної книги
    filename = "book.bin"
    book = AddressBook()
    file_data = book.read_from_file(filename)

    if file_data:

        book = file_data
    
    else:

        john_record = Record("John", (1972, 5, 12))
        john_record.add_phone("1234567890")
        john_record.add_phone("5555555555")
        book.add_record(john_record)

        bob_record = Record("Bob", (1988, 12, 11))
        bob_record.add_phone("9876543888")
        book.add_record(bob_record)

        steve_record = Record("Steve", (1999, 6, 18))
        steve_record.add_phone("9876543888")
        book.add_record(steve_record)

        jill_record = Record("Jill", (1992, 3, 13))
        jill_record.add_phone("9812345698")
        book.add_record(jill_record)

        meg_record = Record("Meg", (1998, 7, 11))
        meg_record.add_phone("1232345698")
        book.add_record(meg_record)

        alice_record = Record("Allice", (1996, 9, 20))
        alice_record.add_phone("8642345698")
        book.add_record(alice_record)

        book.save_to_file(filename)

    print(f"= all book =\n{book}")

    print("\n! empty input for exit !")

    while True:
        
        what_to_search = input("what to search? > ")

        if what_to_search == "":
            print("good bye!")
            quit()
        
        search_data = book.find(what_to_search)

        if search_data:
            print(f"matches:\n{search_data}")
        else:
            print("no matches")