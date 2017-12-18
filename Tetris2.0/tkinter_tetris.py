from tkinter import Canvas, Label, Tk, StringVar, Button, LEFT
from random import choice, randint


class GameCanvas(Canvas):
    def clean_line(self, boxes_to_delete):
        for box in boxes_to_delete:
            self.delete(box)
        self.update()

    def drop_boxes(self, boxes_to_drop):
        for box in boxes_to_drop:
            self.move(box, 0, Tetris.BOX_SIZE)
        self.update()

    def completed_lines(self, y_coords):
        cleaned_lines = 0
        y_coords = sorted(y_coords)
        for y in y_coords:
            if sum(1 for box in self.find_all() if self.coords(box)[3] == y) == \
               ((Tetris.GAME_WIDTH - 20) // Tetris.BOX_SIZE):
                self.clean_line([box
                                for box in self.find_all()
                                if self.coords(box)[3] == y])
                
                self.drop_boxes([box
                                 for box in self.find_all()
                                 if self.coords(box)[3] < y])
                cleaned_lines += 1
        return cleaned_lines
    
    def game_board(self):
        board = [[0] * ((Tetris.GAME_WIDTH - 20) // Tetris.BOX_SIZE)\
                 for _ in range(Tetris.GAME_HEIGHT // Tetris.BOX_SIZE)]
        for box in self.find_all():
            x, y, _, _ = self.coords(box)
            board[int(y // Tetris.BOX_SIZE)][int(x // Tetris.BOX_SIZE)] = 1
        return board
    def boxes(self):
        return self.find_all() == self.find_withtag(fill="blue")




class Shape():
    def __init__(self):
        self.__coords = choice(Tetris.SHAPES)

    @property
    def coords(self):
        return self.__coords

    def rotate(self):  
        self.__coords = self.__rotate()
    
    def rotate_directions(self):
        rotated = self.__rotate()
        directions = [(rotated[i][0] - self.__coords[i][0],
                       rotated[i][1] - self.__coords[i][1]) for i in range(len(self.__coords))]

        return directions

    def drop(self, board, offset):
        shape = [[1 if (i, j) in self.__coords else 0 \
                 for j in range(max(self.__coords, key=lambda x: x[1])[1] + 1)]\
                 for i in range(max(self.__coords, key=lambda x: x[0])[0] + 1)]
        last_level = len(board) - len(shape) + 1
        for level in range(last_level):
            for i in range(len(shape)):
                for j in range(len(shape[0])):
                    if board[level+i][offset+j] == 1 and shape[i][j] == 1:
                        return level - 1
        return last_level - 1

    def __rotate(self):
        max_x = max(self.__coords, key=lambda x:x[0])[0]
        new_original = (max_x, 0)

        return [(new_original[0] - coord[1],
                 new_original[1] + coord[0]) for coord in self.__coords]


class Piece():
    def __init__(self, canvas, start_point, shape = None):
        self.__shape = shape
        if not shape:
            self.__shape = Shape()
        self.canvas = canvas
        self.boxes = self.__create_boxes(start_point)
        self.predict_boxes = []
    
    @property
    def shape(self):
        return self.__shape
    
    
    def move(self, direction):
        if all(self.__can_move(self.canvas.coords(box), direction) for box in self.boxes):
            x, y = direction
            for box in self.boxes:
                self.canvas.move(box,
                                 x * Tetris.BOX_SIZE,
                                 y * Tetris.BOX_SIZE)
            return True
        return False

    def rotate(self):
        directions = self.__shape.rotate_directions()
        if all(self.__can_move(self.canvas.coords(self.boxes[i]), directions[i]) for i in range(len(self.boxes))):
            self.__shape.rotate()
            for i in range(len(self.boxes)):
                x, y = directions[i]
                self.canvas.move(self.boxes[i],
                                 x * Tetris.BOX_SIZE,
                                 y * Tetris.BOX_SIZE)

    @property
    def offset(self):
        return min(int(self.canvas.coords(box)[0]) // Tetris.BOX_SIZE for box in self.boxes)
    
    def predict_drop(self, board):
        print(self.offset)
        level = self.shape.drop(board, self.offset)
        self.remove_predicts()
        for coord in self.__shape.coords:
            x, y = coord
            box = self.canvas.create_rectangle((x + self.offset) * Tetris.BOX_SIZE + 10,
                                               (y + level) * Tetris.BOX_SIZE,
                                               (x + self.offset + 1) * Tetris.BOX_SIZE + 10,
                                               (y + level + 1) * Tetris.BOX_SIZE,
                                               fill="yellow")
            self.predict_boxes += [box]

    def remove_predicts(self):
        for box in self.predict_boxes:
            self.canvas.delete(box)
        self.canvas.update()
        self.predict_boxes = []


    def __create_boxes(self, start_point):
        boxes = []
        for coord in self.__shape.coords:
            x, y = coord
            box = self.canvas.create_rectangle(x * Tetris.BOX_SIZE + start_point,
                                               y * Tetris.BOX_SIZE,
                                               x * Tetris.BOX_SIZE + Tetris.BOX_SIZE + start_point,
                                               y * Tetris.BOX_SIZE + Tetris.BOX_SIZE,
                                               fill="blue")
            boxes += [box]

        return boxes

    def __can_move(self, box_coords, new_pos):
        x, y = new_pos
        x = x * Tetris.BOX_SIZE
        y = y * Tetris.BOX_SIZE
        x_left, y_up, x_right, y_down = box_coords

        overlap = set(self.canvas.find_overlapping((x_left + x_right) / 2 + x, 
                                                   (y_up + y_down) / 2 + y, 
                                                   (x_left + x_right) / 2 + x,
                                                   (y_up + y_down) / 2 + y))
        other_items = set(self.canvas.find_all()) - set(self.boxes)

        if y_down + y > Tetris.GAME_HEIGHT or \
           x_left + x < 0 or \
           x_right + x > Tetris.GAME_WIDTH or \
           overlap & other_items:
            return False
        return True        


class Tetris():
    SHAPES = ([(0, 0), (1, 0), (0, 1), (1, 1)],     # Square
              [(0, 0), (1, 0), (2, 0), (3, 0)],     # Line
              [(2, 0), (0, 1), (1, 1), (2, 1)],     # Right L
              [(0, 0), (0, 1), (1, 1), (2, 1)],     # Left L
              [(0, 1), (1, 1), (1, 0), (2, 0)],     # Right Z
              [(0, 0), (1, 0), (1, 1), (2, 1)],     # Left Z
              [(1, 0), (0, 1), (1, 1), (2, 1)])     # T

    BOX_SIZE = 20

    GAME_WIDTH = 300
    GAME_HEIGHT = 500
    GAME_START_POINT = GAME_WIDTH / 2 / BOX_SIZE * BOX_SIZE - BOX_SIZE

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        self._level = level

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, score):
        self._score = score

    @property
    def blockcount(self):
        return self._blockcount

    @blockcount.setter
    def blockcount(self, blockcount):
        self._blockcount = blockcount

    def __init__(self):
        self.root = Tk()
        self.root.geometry("500x550") 
        self.root.title('Tetris')
        self.root.bind("<Key>", self.game_control)
        self.__game_canvas()
        self.__level_score_label()
        self.__next_piece_canvas()

    def game_control(self, event):
        if event.char in ["a", "A", "\uf702"]:
            self.current_piece.move((-1, 0))
        elif event.char in ["d", "D", "\uf703"]:
            self.current_piece.move((1, 0))
        # Hard drop left for now, I wanna do it different...
        # 1. Have a mirror piece, (What the piece will look like, if you do the "hard drop")
        # 2. When "Hard Drop" is pressed, Fill the mirror piece and delete the old one. No more clunky speed things :)
        # 
        # elif event.char in ["s", "S", "\uf701"]:
        #     self.hard_drop()
        elif event.char in ["w", "W", "\uf700"]:
            self.current_piece.rotate()

    # Is this after a Pause? Or a new_game?
    def new_game(self):
        self.level = 1
        self.score = 0
        self.blockcount = 0
        self.speed = 500

        self.canvas.delete("all")
        self.next_canvas.delete("all")
        
        self.current_piece = None
        self.next_piece = None

        self.update_piece()

        self.game_board = [[0] * ((Tetris.GAME_WIDTH - 20) // Tetris.BOX_SIZE)\
                           for _ in range(Tetris.GAME_HEIGHT // Tetris.BOX_SIZE)]

    def update_piece(self):
        if not self.next_piece:
            self.next_piece = Piece(self.next_canvas, 0)

        self.current_piece = Piece(self.canvas, Tetris.GAME_START_POINT, self.next_piece.shape)
        self.next_canvas.delete("all")
        self.next_piece = Piece(self.next_canvas, 0)

    def start(self):
        self.new_game()
        self.root.after(self.speed, None)
        self.drop()
        self.root.mainloop()
        
    def drop(self):
        if not self.current_piece.move((0,1)):
            if self.current_piece.predict_boxes != []:
                self.current_piece.remove_predicts()
                self.root.after(self.speed, self.drop)
                return 
            self.game_board = self.canvas.game_board()
            self.completed_lines()
            self.update_piece()
            if self.is_game_over():
                return 

            self.blockcount += 1
        self.current_piece.predict_drop(self.game_board)
        self.root.after(self.speed, self.drop)

    def update_status(self):        
        self.status_var.set(f"Level: {self.level}, Score: {self.score}")
        self.status.update()

    def is_game_over(self):
        if not self.current_piece.move((0,1)):
            self.play_again_btn = Button(self.root, text="Play Again", command=self.play_again)
            self.quit_btn = Button(self.root, text="Quit", command=self.quit) 
            self.play_again_btn.place(x = Tetris.GAME_WIDTH + 10, y = 200, width=100, height=25)
            self.quit_btn.place(x = Tetris.GAME_WIDTH + 10, y = 300, width=100, height=25)
            return True
        return False

    def play_again(self):
        self.play_again_btn.destroy()
        self.quit_btn.destroy()
        self.start()

    def quit(self):
        self.root.quit()     

    def completed_lines(self):
        y_coords = [self.canvas.coords(box)[3] for box in self.current_piece.boxes]
        self.score += self.canvas.completed_lines(y_coords)

    def __game_canvas(self):
        self.canvas = GameCanvas(self.root, 
                             width = Tetris.GAME_WIDTH, 
                             height = Tetris.GAME_HEIGHT)
        self.canvas.pack(padx=5 , pady=10, side=LEFT)

    def __level_score_label(self):
        self.status_var = StringVar()        
        self.status = Label(self.root, 
                            textvariable=self.status_var, 
                            font=("Helvetica", 10, "bold"))
        self.status.place(x = Tetris.GAME_WIDTH + 10, y = 100, width=100, height=25)

    def __next_piece_canvas(self):
        self.next_canvas = Canvas(self.root,
                                 width = 60,
                                 height = 60)
        self.next_canvas.pack(padx=5 , pady=10)
    


if __name__ == '__main__':
    game = Tetris()
    game.start()
