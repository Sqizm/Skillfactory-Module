instructions = input("""Привет! Это логическая игра крестики-нолики. 
            Игроки по очереди ставят на свободные клетки поля 3×3 знаки (один всегда крестики, другой всегда нолики).
            Первый, выстроивший в ряд 3 своих фигуры по вертикали, горизонтали или большой диагонали, выигрывает.
            Если игроки заполнили все 9 ячеек и оказалось, что ни в одной вертикали, 
            горизонтали или большой диагонали нет трёх одинаковых знаков,
            партия считается закончившейся в ничью. Первый ход делает игрок, ставящий крестики
            \n        
            Введите 'Да' если желаете сыграть, 'Нет' если не желаете: """)

enter = instructions == "Да"  # для ответа
board = [[' ' for _ in range(3)] for _ in range(3)]  # пустое поле
player_1 = "Х"  # символ для первого игрока
player_2 = "О"  # символ для второго игрока
current_player = player_1  # определяем игрока


# Функция показывающая поле.
def board_d():
    print("   0   1   2")
    for i in range(3):
        print(i, end='  ')
        for j in range(3):
            if j < 2:
                print(board[i][j], end=' | ')
            else:
                print(board[i][j])
        if i < 2:
            print('  ' + '-' * 11)


# Функция для проверки победителя.
def check_winner():
    # Проверка по горизонтали и вертикали с помощью цикла for.
    for i in range(3):
        if board[i][0] == board[i][1] == board[i][2] != ' ':
            return board[i][0]
        if board[0][i] == board[1][i] == board[2][i] != ' ':
            return board[0][i]
    # Проверка по диагонали.
    if board[0][0] == board[1][1] == board[2][2] != ' ':
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] != ' ':
        return board[0][2]
    return None  # Если побидителя нет.


# Функция для проверки ничьи
def check_draw():
    for row in board:
        if ' ' in row:
            return False
    return True


# Функция для хода игрока
def player_move(row, col):
    if board[row][col] == ' ':
        board[row][col] = current_player
        return True
    else:
        return False


# Функция самой игры.
def started():
    global current_player
    if enter:
        print("\nНачинаем!")
        while True:
            board_d()
            print(f"\nХод делает игрок, ставящий символ - '{current_player}'")
            row = int(input("Выберите и введите номер строки '0 1 2': "))
            col = int(input("Выберите и введите номер столбца '0 1 2': "))
            if player_move(row, col):
                winner = check_winner()
                if winner:
                    board_d()
                    print(f"\nПобедил игрок, ставящий символ - {winner}")
                    break
                if check_draw():
                    board_d()
                    print("\nНичья!")
                    break
                current_player = player_2 if current_player == player_1 else player_1
            else:
                print("\nУпс! Место занято, выбирай другое).")
    else:
        return print("\nОчень жаль что вы отказались от игры. Увидимся в следующий раз.")


started()
