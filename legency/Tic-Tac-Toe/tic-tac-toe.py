
class Tic_Tac_Toe:
    def __init__(self):
        self.grid = [[0, 0, 0],[0, 0, 0],[0, 0, 0]]
        self.current_player = 1
        self.remains = 9
        self.active = True
        self.winner = None
        # self.mark_dic = {'1': 'x', '2': 'o'}

    def move(self, player, x, y): # True for moveing successfully, False for failure
        assert player == self.current_player
        if self.grid[x][y] != 0:
            return False
        self.grid[x][y] = player

        self.remains -= 1
        self.winner = self.get_winner()

        if self.remains == 0 and not self.winner:
            self.terminate()
        elif not self.winner:
            self.switch_player()
        self.update_scene()
        return True

    def update_scene(self):
        pass

    def terminate(self):
        self.active = False

    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1
    
    def get_winner(self):
        p = self.current_player
        if self.grid[0][0] == p and self.grid[0][1] == p and self.grid[0][2] == p:
            return p
        elif self.grid[1][0] == p and self.grid[1][1] == p and self.grid[1][2] == p:
            return p
        elif self.grid[2][0] == p and self.grid[2][1] == p and self.grid[2][2] == p:
            return p
        elif self.grid[0][0] == p and self.grid[1][0] == p and self.grid[2][0] == p:
            return p
        elif self.grid[0][1] == p and self.grid[1][1] == p and self.grid[2][1] == p:
            return p
        elif self.grid[0][2] == p and self.grid[1][2] == p and self.grid[2][2] == p:
            return p
        elif self.grid[0][0] == p and self.grid[1][1] == p and self.grid[2][2] == p:
            return p
        elif self.grid[0][2] == p and self.grid[1][1] == p and self.grid[2][0] == p:
            return p
        return None
