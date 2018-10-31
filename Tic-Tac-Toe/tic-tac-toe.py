
class Tic_Tac-Toe:
    def __init__(self):
        self.grid = [[0, 0, 0],[0, 0, 0],[0, 0, 0]]
        self.current_player = 1
        # self.mark_dic = {'1': 'x', '2': 'o'}
    def move(self, player, x, y):
        assert player == self.current_player
        self.grid[x][y] = player

    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1
            