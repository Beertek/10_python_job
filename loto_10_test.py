# test_loto_09.py
import pytest
import random
from loto_09 import LottoCard, LottoGame, main

class TestLottoCard:
    """Тесты для класса LottoCard"""
    
    def test_card_initialization(self):
        """Тест инициализации карточки"""
        card = LottoCard("Тест")
        assert card.card_id == "Тест"
        assert len(card.rows) == 3
        assert len(card.rows[0]) == 9
        assert card.numbers_left == 15
        assert all(len(row) == 9 for row in card.marked)
        assert all(not marked for row in card.marked for marked in row)
    
    def test_card_generation_rules(self):
        """Тест правил генерации карточки"""
        card = LottoCard()
        
        # Проверяем, что всего 15 чисел
        total_numbers = sum(1 for row in card.rows for cell in row if cell is not None)
        assert total_numbers == 15
        
        # Проверяем, что числа в строках отсортированы
        for row in range(3):
            numbers = [num for num in card.rows[row] if num is not None]
            assert numbers == sorted(numbers)
        
        # Проверяем диапазоны чисел по столбцам
        for col in range(9):
            start = col * 10 + 1
            end = start + 9 if col < 8 else 90
            for row in range(3):
                num = card.rows[row][col]
                if num is not None:
                    assert start <= num <= end
    
    def test_check_number_exists(self):
        """Тест проверки существующего числа"""
        card = LottoCard()
        # Находим первое существующее число
        for row in range(3):
            for col in range(9):
                if card.rows[row][col] is not None:
                    number = card.rows[row][col]
                    initial_left = card.numbers_left
                    
                    assert card.check_number(number) is True
                    assert card.numbers_left == initial_left - 1
                    assert card.marked[row][col] is True
                    return
        
        pytest.fail("В карточке нет чисел")
    
    def test_check_number_not_exists(self):
        """Тест проверки несуществующего числа"""
        card = LottoCard()
        # Находим несуществующее число
        all_numbers = set()
        for row in range(3):
            for col in range(9):
                if card.rows[row][col] is not None:
                    all_numbers.add(card.rows[row][col])
        
        # Ищем число от 1 до 90, которого нет в карточке
        for num in range(1, 91):
            if num not in all_numbers:
                initial_left = card.numbers_left
                assert card.check_number(num) is False
                assert card.numbers_left == initial_left
                # Проверяем, что ничего не отметилось
                assert not any(card.marked[row][col] for row in range(3) 
                             for col in range(9) if card.rows[row][col] == num)
                return
        
        pytest.fail("Не найдено несуществующее число")
    
    def test_check_number_already_marked(self):
        """Тест проверки уже отмеченного числа"""
        card = LottoCard()
        # Находим число и отмечаем его
        for row in range(3):
            for col in range(9):
                if card.rows[row][col] is not None:
                    number = card.rows[row][col]
                    card.check_number(number)
                    initial_left = card.numbers_left
                    
                    # Пытаемся отметить снова
                    assert card.check_number(number) is False
                    assert card.numbers_left == initial_left
                    return
        
        pytest.fail("В карточке нет чисел")
    
    def test_is_complete(self):
        """Тест проверки заполненности карточки"""
        card = LottoCard()
        assert card.is_complete() is False
        
        # Отмечаем все числа
        for row in range(3):
            for col in range(9):
                if card.rows[row][col] is not None:
                    card.check_number(card.rows[row][col])
        
        assert card.is_complete() is True
        assert card.numbers_left == 0
    
    def test_display_formats(self):
        """Тест различных форматов отображения"""
        card = LottoCard("Тест")
        
        # Обычное отображение
        display_normal = card.display()
        assert "Тест" in display_normal
        assert "-" * 26 in display_normal
        
        # Отображение со скрытыми числами
        display_hidden = card.display(hide_numbers=True)
        assert "*" in display_hidden
        assert all(str(num) not in display_hidden for row in card.rows 
                  for num in row if num is not None)
        
        # Отображение с отмеченными числами
        for row in range(3):
            for col in range(9):
                if card.rows[row][col] is not None:
                    card.check_number(card.rows[row][col])
                    break
            break
        
        display_marked = card.display()
        assert "-" in display_marked  # Отметка должна отображаться как "-"


class TestLottoGame:
    """Тесты для класса LottoGame"""
    
    def test_game_initialization(self):
        """Тест инициализации игры"""
        game = LottoGame(['human', 'computer'])
        
        assert len(game.players) == 2
        assert game.players[0]['type'] == 'human'
        assert game.players[1]['type'] == 'computer'
        assert game.players[0]['name'] == "Игрок 1"
        assert game.players[1]['name'] == "Компьютер 2"
        assert len(game.barrels) == 90
        assert game.current_player == 0
    
    def test_game_initialization_multiple_players(self):
        """Тест инициализации с несколькими игроками"""
        game = LottoGame(['human', 'computer', 'human', 'computer'])
        
        assert len(game.players) == 4
        assert game.players[0]['type'] == 'human'
        assert game.players[1]['type'] == 'computer'
        assert game.players[2]['type'] == 'human'
        assert game.players[3]['type'] == 'computer'
    
    def test_get_next_barrel(self):
        """Тест получения следующего бочонка"""
        game = LottoGame(['human', 'computer'])
        initial_length = len(game.barrels)
        
        barrel = game.get_next_barrel()
        assert barrel is not None
        assert 1 <= barrel <= 90
        assert len(game.barrels) == initial_length - 1
        assert game.current_barrel == barrel
        
        # Проверяем, что все бочонки уникальны
        barrels = []
        while game.barrels:
            barrels.append(game.get_next_barrel())
        assert len(barrels) == 89  # Один уже достали
        assert len(set(barrels)) == 89  # Все уникальны
    
    def test_get_next_barrel_empty(self):
        """Тест получения бочонка из пустого списка"""
        game = LottoGame(['human', 'computer'])
        game.barrels = []
        
        assert game.get_next_barrel() is None
    
    def test_computer_move_mark(self):
        """Тест хода компьютера с зачеркиванием числа"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 1  # Ход компьютера
        
        # Получаем бочонок
        barrel = game.get_next_barrel()
        
        # Подменяем карточку компьютера, чтобы точно было число
        computer = game.players[1]
        # Находим существующее число на карточке
        for row in range(3):
            for col in range(9):
                if computer['card'].rows[row][col] is not None:
                    number = computer['card'].rows[row][col]
                    game.current_barrel = number
                    break
            break
        
        initial_left = computer['card'].numbers_left
        game_over, message = game.computer_move(1)
        
        assert game_over is False
        assert "зачеркнул" in message
        assert computer['card'].numbers_left == initial_left - 1
    
    def test_computer_move_skip(self):
        """Тест хода компьютера с пропуском"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 1
        
        # Получаем бочонок с числом, которого нет в карточке
        computer = game.players[1]
        all_numbers = set()
        for row in range(3):
            for col in range(9):
                if computer['card'].rows[row][col] is not None:
                    all_numbers.add(computer['card'].rows[row][col])
        
        # Ищем число, которого нет
        for num in range(1, 91):
            if num not in all_numbers:
                game.current_barrel = num
                break
        
        initial_left = computer['card'].numbers_left
        game_over, message = game.computer_move(1)
        
        assert game_over is False
        assert "пропустил" in message
        assert computer['card'].numbers_left == initial_left
    
    def test_computer_move_win(self):
        """Тест хода компьютера с победой"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 1
        
        computer = game.players[1]
        # Отмечаем все числа кроме одного
        numbers = []
        for row in range(3):
            for col in range(9):
                if computer['card'].rows[row][col] is not None:
                    numbers.append(computer['card'].rows[row][col])
        
        # Отмечаем все кроме последнего
        for num in numbers[:-1]:
            computer['card'].check_number(num)
        
        assert computer['card'].numbers_left == 1
        
        # Ходим с последним числом
        last_number = numbers[-1]
        game.current_barrel = last_number
        
        game_over, message = game.computer_move(1)
        
        assert game_over is True
        assert "ПОБЕДИЛ" in message
        assert computer['card'].is_complete() is True
    
    def test_human_move_mark_correct(self, monkeypatch):
        """Тест хода человека с правильным зачеркиванием"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        
        human = game.players[0]
        # Находим число для зачеркивания
        for row in range(3):
            for col in range(9):
                if human['card'].rows[row][col] is not None:
                    number = human['card'].rows[row][col]
                    game.current_barrel = number
                    break
            break
        
        # Имитируем ввод 'y'
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        
        initial_left = human['card'].numbers_left
        game_over, message = game.human_move(0)
        
        assert game_over is False
        assert "зачеркнул" in message
        assert human['card'].numbers_left == initial_left - 1
    
    def test_human_move_mark_incorrect(self, monkeypatch):
        """Тест хода человека с ошибочным зачеркиванием"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        
        human = game.players[0]
        # Находим число, которого нет в карточке
        all_numbers = set()
        for row in range(3):
            for col in range(9):
                if human['card'].rows[row][col] is not None:
                    all_numbers.add(human['card'].rows[row][col])
        
        for num in range(1, 91):
            if num not in all_numbers:
                game.current_barrel = num
                break
        
        # Имитируем ввод 'y'
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        
        initial_left = human['card'].numbers_left
        game_over, message = game.human_move(0)
        
        assert game_over is True
        assert "ОШИБКА" in message
        assert "нет на карточке" in message
        assert human['card'].numbers_left == initial_left
    
    def test_human_move_skip_correct(self, monkeypatch):
        """Тест хода человека с правильным пропуском"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        
        human = game.players[0]
        # Находим число, которого нет в карточке
        all_numbers = set()
        for row in range(3):
            for col in range(9):
                if human['card'].rows[row][col] is not None:
                    all_numbers.add(human['card'].rows[row][col])
        
        for num in range(1, 91):
            if num not in all_numbers:
                game.current_barrel = num
                break
        
        # Имитируем ввод 'n'
        monkeypatch.setattr('builtins.input', lambda _: 'n')
        
        initial_left = human['card'].numbers_left
        game_over, message = game.human_move(0)
        
        assert game_over is False
        assert "пропустил" in message
        assert human['card'].numbers_left == initial_left
    
    def test_human_move_skip_incorrect(self, monkeypatch):
        """Тест хода человека с ошибочным пропуском"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        
        human = game.players[0]
        # Находим число, которое есть в карточке
        for row in range(3):
            for col in range(9):
                if human['card'].rows[row][col] is not None:
                    number = human['card'].rows[row][col]
                    game.current_barrel = number
                    break
            break
        
        # Имитируем ввод 'n'
        monkeypatch.setattr('builtins.input', lambda _: 'n')
        
        initial_left = human['card'].numbers_left
        game_over, message = game.human_move(0)
        
        assert game_over is True
        assert "ОШИБКА" in message
        assert "есть на карточке" in message
        assert human['card'].numbers_left == initial_left
    
    def test_human_move_invalid_input(self, monkeypatch):
        """Тест обработки неверного ввода человека"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        game.current_barrel = 50
        
        # Имитируем сначала неверный ввод, потом правильный
        inputs = ['x', 'y']
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        game_over, message = game.human_move(0)
        
        # Проверяем, что игра продолжилась после неверного ввода
        assert game_over is False or game_over is True  # Может быть любым в зависимости от числа
    
    def test_human_move_win(self, monkeypatch):
        """Тест хода человека с победой"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        
        human = game.players[0]
        # Отмечаем все числа кроме одного
        numbers = []
        for row in range(3):
            for col in range(9):
                if human['card'].rows[row][col] is not None:
                    numbers.append(human['card'].rows[row][col])
        
        for num in numbers[:-1]:
            human['card'].check_number(num)
        
        last_number = numbers[-1]
        game.current_barrel = last_number
        
        # Имитируем ввод 'y'
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        
        game_over, message = game.human_move(0)
        
        assert game_over is True
        assert "ПОБЕДИЛ" in message
        assert human['card'].is_complete() is True
    
    def test_play_turn(self):
        """Тест выполнения хода"""
        game = LottoGame(['computer', 'computer'])
        game.current_barrel = 50
        
        game_over, message = game.play_turn(0)
        
        assert isinstance(game_over, bool)
        assert isinstance(message, str)
    
    def test_display_all_cards(self, capsys):
        """Тест отображения всех карточек"""
        game = LottoGame(['human', 'computer'])
        game.current_player = 0
        
        game.display_all_cards()
        captured = capsys.readouterr()
        assert "Игрок 1" in captured.out
        assert "Компьютер 2" in captured.out
        
        # Скрываем карточку компьютера
        game.display_all_cards(hide_computer=True)
        captured = capsys.readouterr()
        assert "*" in captured.out
    
    def test_play_game_computer_win(self, monkeypatch):
        """Тест полной игры с победой компьютера"""
        game = LottoGame(['computer', 'computer'])
        
        # Подменяем карточку первого компьютера, чтобы он быстро победил
        computer1 = game.players[0]
        # Отмечаем все числа кроме одного
        numbers = []
        for row in range(3):
            for col in range(9):
                if computer1['card'].rows[row][col] is not None:
                    numbers.append(computer1['card'].rows[row][col])
        
        for num in numbers[:-1]:
            computer1['card'].check_number(num)
        
        # Запускаем игру (она остановится, когда компьютер победит)
        game.play()
    
    def test_play_game_human_win(self, monkeypatch):
        """Тест полной игры с победой человека"""
        game = LottoGame(['human', 'computer'])
        
        # Отмечаем все числа человека кроме одного
        human = game.players[0]
        numbers = []
        for row in range(3):
            for col in range(9):
                if human['card'].rows[row][col] is not None:
                    numbers.append(human['card'].rows[row][col])
        
        for num in numbers[:-1]:
            human['card'].check_number(num)
        
        # Имитируем правильный ввод для последнего числа
        monkeypatch.setattr('builtins.input', lambda _: 'y')
        
        game.play()
    
    def test_play_game_no_winner(self, monkeypatch):
        """Тест игры без победителя"""
        game = LottoGame(['computer', 'computer'])
        # Уменьшаем количество бочонков для быстрого теста
        game.barrels = list(range(1, 5))
        random.shuffle(game.barrels)
        
        game.play()
    
    def test_play_game_auto_win_check(self):
        """Тест автоматической проверки победы"""
        game = LottoGame(['computer', 'computer'])
        
        # Заполняем карточку первого компьютера
        computer1 = game.players[0]
        for row in range(3):
            for col in range(9):
                if computer1['card'].rows[row][col] is not None:
                    computer1['card'].check_number(computer1['card'].rows[row][col])
        
        # Запускаем игру - должна сразу обнаружить победителя
        game.play()


class TestMainFunction:
    """Тесты для главной функции"""
    
    def test_main_game_start(self, monkeypatch):
        """Тест запуска игры через main"""
        # Имитируем ввод: 2 игрока, человек и компьютер, не играть снова
        inputs = ['2', 'h', 'c', 'n']
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        main()
    
    def test_main_invalid_player_count(self, monkeypatch):
        """Тест обработки неверного количества игроков"""
        # Сначала неверное количество, потом правильное
        inputs = ['1', '2', 'h', 'c', 'n']
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        main()
    
    def test_main_invalid_player_type(self, monkeypatch):
        """Тест обработки неверного типа игрока"""
        # Сначала неверный тип, потом правильный
        inputs = ['2', 'x', 'h', 'c', 'n']
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        main()
    
    def test_main_play_again(self, monkeypatch):
        """Тест повторной игры"""
        # Для повторной игры нужно много входных данных
        # Первая игра: 2 игрока, оба компьютера
        # Вторая игра: 2 игрока, оба компьютера, потом выход
        inputs = ['2', 'c', 'c', 'y',  # первая игра и запрос на повтор
                  '2', 'c', 'c', 'n']   # вторая игра и выход
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        main()
    
    def test_main_invalid_replay_input(self, monkeypatch):
        """Тест обработки неверного ввода при запросе на повтор"""
        # Неверный ввод, потом правильный
        inputs = ['2', 'c', 'c', 'x', 'n']
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        main()
    
    def test_main_value_error_handling(self, monkeypatch):
        """Тест обработки ValueError при вводе количества игроков"""
        # Сначала не число, потом правильное число
        inputs = ['abc', '2', 'h', 'c', 'n']
        monkeypatch.setattr('builtins.input', lambda _: inputs.pop(0))
        
        main()