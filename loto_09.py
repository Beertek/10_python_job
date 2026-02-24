import random
from typing import List, Tuple, Optional

class LottoCard:
    """Класс для представления карточки лото"""
    
    def __init__(self, card_id: str = ""):
        self.card_id = card_id
        self.rows = self._generate_card()
        self.marked = [[False for _ in range(9)] for _ in range(3)]
        self.numbers_left = 15  # Всего 15 чисел на карточке
        
    def _generate_card(self) -> List[List[Optional[int]]]:
        """Генерация случайной карточки по правилам"""
        # Создаем пустую карточку 3x9
        card = [[None for _ in range(9)] for _ in range(3)]
        
        # Для каждого столбца выбираем числа из соответствующего десятка
        for col in range(9):
            # Числа для столбца: от col*10+1 до col*10+10 (для последнего столбца 81-90)
            start = col * 10 + 1
            end = start + 9
            if col == 8:  # Последний столбец 81-90
                end = 90
            available_numbers = list(range(start, end + 1))
            random.shuffle(available_numbers)
            
            # В каждом столбце должно быть 1-2 числа (всего 15 чисел на карточке)
            numbers_in_col = random.randint(1, 2)
            if col == 0:  # Корректируем, чтобы всего было 15 чисел
                numbers_in_col = 1
            elif col == 8:
                numbers_in_col = 2
            
            # Выбираем строки для размещения чисел
            rows = random.sample(range(3), numbers_in_col)
            for row in rows:
                card[row][col] = available_numbers.pop()
        
        # Сортируем числа в каждой строке по возрастанию
        for row in range(3):
            numbers = []
            for col in range(9):
                if card[row][col] is not None:
                    numbers.append((col, card[row][col]))
            
            # Сортируем числа и возвращаем на свои места
            numbers.sort(key=lambda x: x[1])
            card[row] = [None] * 9
            for col, num in numbers:
                card[row][col] = num
        
        return card
    
    def display(self, hide_numbers: bool = False) -> str:
        """Отображение карточки"""
        result = []
        result.append("-" * 26)
        if self.card_id:
            result.append(f"Карточка {self.card_id}")
        
        for row in range(3):
            line = ""
            for col in range(9):
                if self.rows[row][col] is None:
                    line += "   "
                elif self.marked[row][col]:
                    line += f" - "
                elif hide_numbers:
                    line += " * "
                else:
                    line += f"{self.rows[row][col]:2d} "
            result.append(line)
        result.append("-" * 26)
        return "\n".join(result)
    
    def check_number(self, number: int) -> bool:
        """Проверка наличия числа на карточке и его отметка"""
        for row in range(3):
            for col in range(9):
                if self.rows[row][col] == number and not self.marked[row][col]:
                    self.marked[row][col] = True
                    self.numbers_left -= 1
                    return True
        return False
    
    def is_complete(self) -> bool:
        """Проверка, все ли числа отмечены"""
        return self.numbers_left == 0


class LottoGame:
    """Класс для управления игрой в лото"""
    
    def __init__(self, player_types: List[str]):
        """
        Инициализация игры
        player_types: список типов игроков ('human' или 'computer')
        """
        self.players = []
        self.barrels = list(range(1, 91))
        random.shuffle(self.barrels)
        self.current_barrel = None
        
        # Создаем игроков
        for i, p_type in enumerate(player_types):
            card_id = f"Игрок {i+1}" if p_type == 'human' else f"Компьютер {i+1}"
            self.players.append({
                'type': p_type,
                'card': LottoCard(card_id),
                'name': card_id
            })
        
        self.current_player = 0  # Текущий игрок для хода
    
    def get_next_barrel(self) -> Optional[int]:
        """Получение следующего бочонка"""
        if self.barrels:
            self.current_barrel = self.barrels.pop()
            return self.current_barrel
        return None
    
    def computer_move(self, player_idx: int) -> Tuple[bool, str]:
        """Ход компьютера"""
        player = self.players[player_idx]
        number = self.current_barrel
        
        # Компьютер зачеркивает число, если оно есть на карточке
        if player['card'].check_number(number):
            if player['card'].is_complete():
                return True, f"{player['name']} зачеркнул {number} и ПОБЕДИЛ!"
            return False, f"{player['name']} зачеркнул {number}"
        else:
            # Если числа нет, компьютер пропускает ход
            return False, f"{player['name']} пропустил ход"
    
    def human_move(self, player_idx: int) -> Tuple[bool, str]:
        """Ход человека"""
        player = self.players[player_idx]
        number = self.current_barrel
        
        print(f"\n{player['name']}, ваш ход!")
        print(player['card'].display())
        
        while True:
            choice = input("Зачеркнуть цифру? (y/n): ").lower().strip()
            if choice in ['y', 'n', 'д', 'н']:
                break
            print("Пожалуйста, введите 'y' или 'n'")
        
        want_to_mark = choice in ['y', 'д']
        
        if want_to_mark:
            if player['card'].check_number(number):
                if player['card'].is_complete():
                    return True, f"{player['name']} зачеркнул {number} и ПОБЕДИЛ!"
                return False, f"{player['name']} зачеркнул {number}"
            else:
                return True, f"ОШИБКА! {number} нет на карточке! {player['name']} проигрывает."
        else:
            if player['card'].check_number(number):
                return True, f"ОШИБКА! {number} есть на карточке! {player['name']} проигрывает."
            else:
                return False, f"{player['name']} пропустил ход"
    
    def play_turn(self, player_idx: int) -> Tuple[bool, str]:
        """Выполнение хода для указанного игрока"""
        player = self.players[player_idx]
        
        if player['type'] == 'human':
            return self.human_move(player_idx)
        else:
            return self.computer_move(player_idx)
    
    def display_all_cards(self, hide_computer: bool = True):
        """Отображение всех карточек"""
        for i, player in enumerate(self.players):
            if player['type'] == 'computer' and hide_computer and i != self.current_player:
                print(player['card'].display(hide_numbers=True))
            else:
                print(player['card'].display())
    
    def play(self):
        """Основной игровой цикл"""
        print("\n" + "="*50)
        print("           ИГРА В ЛОТО")
        print("="*50)
        
        # Показываем начальные карточки
        print("\nНачальные карточки:")
        self.display_all_cards(hide_computer=False)
        
        barrels_left = len(self.barrels) + 1
        
        while self.barrels:
            # Получаем новый бочонок
            barrel = self.get_next_barrel()
            barrels_left -= 1
            
            print(f"\n{'='*50}")
            print(f"Новый бочонок: {barrel} (осталось {barrels_left})")
            
            # Показываем все карточки
            self.display_all_cards()
            
            # Ход текущего игрока
            game_over, message = self.play_turn(self.current_player)
            print(message)
            
            if game_over:
                print("\nИГРА ОКОНЧЕНА!")
                print("\nФинальные карточки:")
                self.display_all_cards(hide_computer=False)
                break
            
            # Проверяем, не победил ли кто-то автоматически
            for i, player in enumerate(self.players):
                if player['card'].is_complete():
                    print(f"\n{player['name']} ПОБЕДИЛ, зачеркнув все числа!")
                    print("\nФинальные карточки:")
                    self.display_all_cards(hide_computer=False)
                    return
            
            # Переход к следующему игроку
            self.current_player = (self.current_player + 1) % len(self.players)
        
        else:
            print("\nБочонки закончились! Игра завершена.")
            print("\nФинальные карточки:")
            self.display_all_cards(hide_computer=False)
            
            # Проверяем победителя
            winners = [p['name'] for p in self.players if p['card'].is_complete()]
            if winners:
                print(f"Победитель(и): {', '.join(winners)}")
            else:
                print("Ничья - никто не зачеркнул все числа")


def main():
    """Основная функция для запуска игры"""
    print("Добро пожаловать в игру Лото!")
    
    # Дополнительная функция: выбор количества игроков
    while True:
        try:
            num_players = int(input("\nВведите количество игроков (2 и более): "))
            if num_players >= 2:
                break
            print("Количество игроков должно быть не менее 2")
        except ValueError:
            print("Пожалуйста, введите число")
    
    # Дополнительная функция: выбор типа для каждого игрока
    player_types = []
    for i in range(num_players):
        while True:
            p_type = input(f"Игрок {i+1}: человек или компьютер? (h/c): ").lower().strip()
            if p_type in ['h', 'c', 'человек', 'компьютер']:
                player_types.append('human' if p_type in ['h', 'человек'] else 'computer')
                break
            print("Пожалуйста, введите 'h' для человека или 'c' для компьютера")
    
    # Создаем и запускаем игру
    game = LottoGame(player_types)
    game.play()
    
    # Спрашиваем о повторной игре
    while True:
        again = input("\nСыграть еще раз? (y/n): ").lower().strip()
        if again in ['y', 'n', 'д', 'н']:
            if again in ['y', 'д']:
                main()
            else:
                print("Спасибо за игру! До свидания!")
            break


if __name__ == "__main__":
    main()