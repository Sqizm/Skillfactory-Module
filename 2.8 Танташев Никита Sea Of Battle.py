from random import randint


# Классы исключения выводящие ошибку
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Ошибка: Стрелять нужно в пределах игровой доски!"


class BoardAlreadyShotException(BoardException):
    def __str__(self):
        return "Ошибка: Вы уже стреляли в это место!\nИли по правилам в этом месте корабль стоять не может!"


class BoardWrongShipException(BoardException):
    pass


# Класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


# Класс корабль на игровом поле
class Ship:
    def __init__(self, shiplen, shipbow, shippos):
        self.shiplen = shiplen              # Длина корабля
        self.shipbow = shipbow              # Точка, где размещен нос корабля
        self.shippos = shippos              # Направление коробля (вертикальное/горизонтальное)
        self.shiphp = shipbow               # Кол-во жизней корабля равен точке носа корабля.

    # Метод который возращает список всех точек корабля.
    @property
    def dots(self):
        ship_dots = []
        for i in range(self.shipbow):
            cor_x = self.shiplen.x
            cor_y = self.shiplen.y

            if self.shippos == 0:           # Напрваление корабля равнозначно вертикали.
                cor_x += i
            elif self.shippos == 1:         # Направление корабля равнозначно горизонтали.
                cor_y += i
            ship_dots.append(Dot(cor_x, cor_y))
        return ship_dots

    # Метод проверки попадания.
    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size                                        # Размер поля.
        self.hid = hid                                          # Скрыть поле.
        self.count = 0                                          # Кол-во пораженных кораблей.
        self.missed = 0                                         # Кол-во промахов
        self.field = [[" "] * size for _ in range(size)]        # Пустое поле.
        self.busy = []                                          # Проверка точки.
        self.ships = []                                         # Список кораблей.

    # Показываем поле.
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for col, row in enumerate(self.field):
            res += f"\n{col + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", " ")
        return res

    # Ставим корабль на доску.
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()                 # Исключение

        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    # Обводка коробля по контору.
    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    # Проверка на выход за пределы поля.
    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # Делаем выстрел по доске.
    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardAlreadyShotException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.shiphp -= 1
                self.field[d.x][d.y] = "X"
                if ship.shiphp == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "T"
        self.missed += 1
        print("Промазал!")
        return False

    def begin(self):
        self.busy = []


# Класс игрока в игру
class Player:
    def __init__(self, board, enemy):
        self.board = board                                        # Собственная доска.
        self.enemy = enemy                                        # Доска игрока.

    def ask(self):
        raise NotImplementedError()                               # Исключение

    def move(self):
        while True:
            try:                                                  # Try-except
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# Класс ИИ унаследованный от класса Player
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Координаты компьютер: {d.x + 1} {d.y + 1}")
        return d


# Класс Пользователь унаследованный от класса Player
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваши координаты: ").split()

            if len(cords) != 2:
                print("Ошибка: Введите x и y координаты!\nx - номер строки; y - номер столбца ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Ошибка: Введите числа а не буквы! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


# Класс игры
class Game:
    def __init__(self, size=6):
        self.size = size                                # Размер поля
        self.lens = [3, 2, 2, 1, 1, 1, 1]               # Список кораблей, лучше начинать с большого корабля.
        pl = self.random_board()                        # Генерация случайной игровой доски для игрока.
        co = self.random_board()                        # Генерация случайной игровой доски для компьютера.
        co.hid = True                                   # Для компьютера скрываем корабли.

        self.ai = AI(co, pl)                            # Игрок компьютер.
        self.us = User(pl, co)                          # Игрок пользователь.

    # Генерация случайной доски.
    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        board = Board(size=self.size)                   # Поле с размером.
        attempts = 0
        for i in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), i, randint(0, 1))
                try:                                    # Try-except
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:         # Исключение.
                    pass
        board.begin()
        return board

    @staticmethod
    def greet():
        print("-" * 25 + "\n\tПриветствуем вас\n\t\tв игре\n\t  морской бой\n\n" +
              "\tФормат ввода: x y\n\tx - номер строки\n\ty - номер столбца\n" + "-" * 25)

    def loop(self):
        num = 0
        while True:
            # Вывод две доски в одну строку.
            print("+" * 60)
            print("Доска пользователя:", " " * 10, "Доска компьютера:")
            user_rows = str(self.us.board).split('\n')
            ai_rows = str(self.ai.board).split('\n')
            for user_row, ai_row in zip(user_rows, ai_rows):
                print(f"{user_row:<30}{ai_row}")
            print("+" * 60)

            if num % 2 == 0:
                print("-" * 20 + "\n" + "Ходит пользователь!\n" + "-" * 20)
                repeat = self.us.move()
            else:
                print("-" * 20 + "\n" + "Ходит компьютер!\n" + "-" * 20)
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20 + "\n" + "Пользователь выиграл!\n" + "-" * 20)
                print("Доска компьютера с поражёнными кораблями:")
                print(self.ai.board)
                print(f"\nИтог пользователя: 7 пораженных целей и {self.ai.board.missed} промахов." +
                      f"\nИтог компьютера: {self.us.board.count} пораженных целей и {self.us.board.missed} промахов.")
                break

            if self.us.board.count == 7:
                print("-" * 20 + "\n" + "Компьютер выиграл!\n" + "-" * 20)
                print("Доска пользователя с поражёнными кораблями:")
                print(self.us.board)
                print(f"\nИтог компьютера: 7 пораженных целей и {self.us.board.missed} промахов." +
                      f"\nИтог компьютера: {self.ai.board.count} пораженных целей и {self.ai.board.missed} промахов.")
                break
            num += 1

    def start(self):
        self.greet()
        run = str(input("Хочешь сыграть?\n'Да', если желаешь. 'Нет', для выхода. Ввод: "))
        run_g = run == "Да"

        if run_g:
            self.loop()
        else:
            return print("Очень жаль что вы отказались от игры. Увидимся в следующий раз.")


if __name__ == "__main__":
    g = Game()
    g.start()
