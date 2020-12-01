class InvalidMoveError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__(message)


class TicTacToe(object):

    def __init__(self, player_a_marker='A', player_b_marker='B'):
        self.game_result = ""
        self.player_a_marker = player_a_marker
        self.player_b_marker = player_b_marker
        self.reset_game()

    def has_ended(self):
        return self.game_result != ""

    def abort_game(self):
        self.reset_game()

    def reset_game(self):
        self.game_choices = self._genrate_all_game_positions()
        self.winning_combos = self._generate_winning_positions()
        self.player_a_choices = set()
        self.player_b_choices = set()

    def _genrate_all_game_positions(self):
        game_positions = []
        for row in range(3):
            for col in range(3):
                game_positions.append((row, col))
        return game_positions

    def _generate_winning_positions(self):
        winning_combos = []
        for row in range(3):
            combo = set()
            for col in range(3):
                combo.add((row, col))
            winning_combos.append(combo)

        for col in range(3):
            combo = set()
            for row in range(3):
                combo.add((row, col))
            winning_combos.append(combo)

        winning_combos.append({(0, 0), (1, 1), (2, 2)})
        winning_combos.append({(0, 2), (1, 1), (2, 0)})

        return winning_combos

    def record_player_a_move(self, selection):
        self._record_player_move(self.player_a_marker, selection)

    def record_player_b_move(self, selection):
        self._record_player_move(self.player_b_marker, selection)

    def _get_player_choices(self, player_marker):

        if player_marker == self.player_a_marker:
            return self.player_a_choices
        else:
            return self.player_b_choices

    def check_winning_combinations(self, player_choices):

        for win_set in self.winning_combos:
            if win_set.issubset(player_choices):
                return True
        return False

    def check_game_draw(self):

        if self.game_result == "" and self.game_choices:
            return False
        return True

    def _record_player_move(self, player_marker, selected_item):

        # Verify that selected item is a valid selection
        if selected_item not in self.game_choices:
            raise InvalidMoveError("Not one of the valid open positions")

        player_choices = self._get_player_choices(player_marker)
        player_choices.add(selected_item)
        item_idx = self.game_choices.index(selected_item)
        self.game_choices = self.game_choices[:item_idx] + self.game_choices[item_idx + 1:]

        if self.check_winning_combinations(player_choices):
            self.game_result = player_marker

        elif self.check_game_draw():
            self.game_result = "D"
