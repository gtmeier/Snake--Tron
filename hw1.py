# George Meier
# CS405 intro AI
# Feb 10, 2019
# python3
# run in ubuntu terminal

# Sources of help
# https://pythonspot.com/snake-with-pygame/
# https://towardsdatascience.com/slitherin-solving-the-classic-game-of-snake-with-ai-part-1-domain-specific-solvers-d1f5a5ccd635
# https://techwithtim.net/tutorials/game-development-with-python/snake-pygame/tutorial-1/

import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
import math
import sys


# text file output
f = open('hw1-output.txt','w')

#intro
print(" ____  _   _    _    _  _______ ")
print("/ ___|| \ | |  / \  | |/ / ____|")
print("\___ \|  \| | / _ \ | ' /|  _|  ")
print(" ___) | |\  |/ ___ \| . \| |___ ")
print("|____/|_| \_/_/   \_\_|\_\_____|")
print("Move with arrow keys\nAviod the Walls\nDon't cross yourself")
# user input
print("Press ESC to quit if stuck in loop or freeze")
print("Output will still be written if you esc an infinite loop")
height=int(input("Enter grid height: "))
width=int(input("Enter grid width: "))
print("Do you want to play? == 1")
print("Or watch an AI play? == 0")
play=int(input(">>> "))

f.write("height: "+str(height)+"\n"+"width: "+str(width)+"\n"+"list of moves: \n") # write to output file

# The length and width of the snake movement
HEIGHT = height
WIDTH = width
FIELD_SIZE = HEIGHT * WIDTH

# The snake head is always in the first element of the snake array
HEAD = 0

# is used to represent the number of different things, because each grid on the matrix will be processed into the path length of the food,
# Therefore there must be a large enough interval between these three variables (>HEIGHT*WIDTH)
FOOD = 0
UNDEFINED = (HEIGHT + 1) * (WIDTH + 1)
SNAKE = 2 * UNDEFINED
# since the snake is one-diminsional array, adding the following values directly to the corresponding element means moving in four directions
LEFT = -1
RIGHT = 1
UP = -WIDTH
DOWN = WIDTH

# error code
ERR = -1111

# Use a one-dimensional array to represent two-dimensional things
# board indicates the rectangular field of snake movement
# Initialize the snake head at (1,1), line 0, HEIGHT line, column 0, WIDTH column is fence, not available
# Initial snake length is 1
# Therefore there must be a large enough interval between these three variables (>HEIGHT*WIDTH)
board = [0] * FIELD_SIZE
snake = [0] * (FIELD_SIZE+1)
snake[HEAD] = 1*WIDTH+1
snake_size = 1

# Temporary variable corresponding to the above variable, used when the snake moves tentatively
tmpboard = [0] * FIELD_SIZE
tmpsnake = [0] * (FIELD_SIZE+1)
tmpsnake[HEAD] = 1*WIDTH+1
tmpsnake_size = 1

# food: Food location (0 to FIELD_SIZE-1), initial at (3, 3)
# best_move: Direction of movement
food = 3 * WIDTH + 3
best_move = ERR #initial

#Array of motion directions
mov = [LEFT, RIGHT, UP, DOWN]

# received keys and scores
key = KEY_RIGHT
score = 1 # The score also indicates the length of the snake

# Check if a cell is covered by a snake body, and if it is not overwritten, it is free and returns true.
def is_cell_free(idx, psize, psnake):
    return not (idx in psnake[:psize])

# Check if a position idx can move in the direction of move
def is_move_possible(idx, move):
    flag = False
    if move == LEFT:
        flag = True if idx%WIDTH > 1 else False
    elif move == RIGHT:
        flag = True if idx%WIDTH < (WIDTH-2) else False
    elif move == UP:
        flag = True if idx > (2*WIDTH-1) else False # which is idx/WIDTH > 1
    elif move == DOWN:
        flag = True if idx < (FIELD_SIZE-2*WIDTH) else False # which is idx/WIDTH < HEIGHT-2
    return flag

# reset board
# after board_refresh, the UNDEFINED value becomes the path length of the food.
# If you need to restore, you need to reset it
def board_reset(psnake, psize, pboard):
    for i in range(FIELD_SIZE):
        if i == food:
            pboard[i] = FOOD
        elif is_cell_free(i, psize, psnake): # this location is empty
            pboard[i] = UNDEFINED
        else: # position is a snake
            pboard[i] = SNAKE

# Breadth-first search traverses the entire board,
# Calculate the path length of each non-SNAKE element in the board to reach the food
def board_refresh(pfood, psnake, pboard):
    queue = []
    queue.append(pfood)
    inqueue = [0] * FIELD_SIZE
    found = False
    # After the end of the while loop, in addition to the body of the snake,
    # Other digit code in each square from its path length to food
    while len(queue)!=0:
        idx = queue.pop(0)
        if inqueue[idx] == 1: continue
        inqueue[idx] = 1
        for i in range(4):
            if is_move_possible(idx, mov[i]):
                if idx + mov[i] == psnake[HEAD]:
                    found = True
                if pboard[idx+mov[i]] < SNAKE: #If the point is not the body of the snake

                    if pboard[idx+mov[i]] > pboard[idx]+1:
                        pboard[idx+mov[i]] = pboard[idx] + 1
                    if inqueue[idx+mov[i]] == 0:
                        queue.append(idx+mov[i])

    return found

#from the snake head, according the the element values in the board
# Select the shortest path from the 4 directions around the snake head
def choose_shortest_safe_move(psnake, pboard):
    best_move = ERR
    min = SNAKE
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<min:
            min = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

#from the snake head, according to the element's values in the board,
# Select the farthest path from the 4 directions around the snake head
def choose_longest_safe_move(psnake, pboard):
    best_move = ERR
    max = -1
    for i in range(4):
        if is_move_possible(psnake[HEAD], mov[i]) and pboard[psnake[HEAD]+mov[i]]<UNDEFINED and pboard[psnake[HEAD]+mov[i]]>max:
            max = pboard[psnake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

# Check if you can chase the snake tail movement, that is, there is a path between the snake head and the snake tail.
# is to avoid the snake head in a dead end
# virtual operation, in tmpboard, tmpsnake
def is_tail_inside():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpboard[tmpsnake[tmpsnake_size-1]] = 0 # Virtually turn the snake tail into food (because it is virtual, so in tmpsnake, tmpboard)
    tmpboard[food] = SNAKE # Place the food, see the snake body
    result = board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # Find the path length from each position to the snake tail
    for i in range(4): # If the snake head and the snake tail are next to each other, return False. I can't follow_tail, chasing the snake tail.
        if is_move_possible(tmpsnake[HEAD], mov[i]) and tmpsnake[HEAD]+mov[i]==tmpsnake[tmpsnake_size-1] and tmpsnake_size>3:
            result = False
    return result

# Let the snake head run one step towards the snake tail
# Regardless of the snake body blocking, running towards the snake tail
def follow_tail():
    global tmpboard, tmpsnake, food, tmpsnake_size
    tmpsnake_size = snake_size
    tmpsnake = snake[:]
    board_reset(tmpsnake, tmpsnake_size, tmpboard) # reset virtual board
    tmpboard[tmpsnake[tmpsnake_size-1]] = FOOD # let the snake tail become food
    tmpboard[food] = SNAKE # let food place become a snake
    board_refresh(tmpsnake[tmpsnake_size-1], tmpsnake, tmpboard) # Find the path length of each position to reach the snake tail
    tmpboard[tmpsnake[tmpsnake_size-1]] = SNAKE # restore snake tail

    return choose_longest_safe_move(tmpsnake, tmpboard) # Return to the running direction (let the snake head move 1 step)

# When all kinds of programs are not working, just find a feasible direction to go run(1 step)
def any_possible_move():
    global food , snake, snake_size, board
    best_move = ERR
    board_reset(snake, snake_size, board)
    board_refresh(food, snake, board)
    min = SNAKE

    for i in range(4):
        if is_move_possible(snake[HEAD], mov[i]) and board[snake[HEAD]+mov[i]]<min:
            min = board[snake[HEAD]+mov[i]]
            best_move = mov[i]
    return best_move

def shift_array(arr, size):
    for i in range(size, 0, -1):
        arr[i] = arr[i-1]

def new_food():
    global food, snake_size
    cell_free = False
    while not cell_free:
        w = randint(1, WIDTH-2)
        h = randint(1, HEIGHT-2)
        food = h * WIDTH + w
        cell_free = is_cell_free(food, snake_size, snake)
    win.addch(int(food/WIDTH), food%WIDTH, '@')

#The real snake in this function, take 1 step towards best_move
def make_move(pbest_move):
    global key, snake, board, snake_size, score
    shift_array(snake, snake_size)
    snake[HEAD] += pbest_move


    # Press esc to exit, getch also ensures the smoothness of the drawing, without it will only see the final result
    win.timeout(100)
    event = win.getch()
    key = key if event == -1 else event
    if key == 27: return #escape ascii code
#    elif key == KEY_LEFT:
#        do=LEFT
#        f.write("UP")
#    elif key==KEY_UP:
#        do=UP
#        do=RIGHT
#    elif key==KEY_DOWN:
#        do=DOWN
        
    p = snake[HEAD]
    win.addch(int(p/WIDTH), p%WIDTH, '*')


    # If the newly added snake head is the location of the food
    # snake plus 1, Generate new food, reset the board (because the original path length is not used)
    if snake[HEAD] == food:
        board[snake[HEAD]] = SNAKE # new snake head
        snake_size += 1
        score += 1
        if snake_size < FIELD_SIZE: new_food()
    else: # If the newly added snake head is not the location of the food
        board[snake[HEAD]] = SNAKE # new snake head
        board[snake[snake_size]] = UNDEFINED # snake tail becomes a space
        win.addch(int(snake[snake_size]/WIDTH), snake[snake_size]%WIDTH, ' ')

# Virtually run once, then check if the run is feasible at the call
# Feasible to run.
# virtual run to eat food, get the virtual snake under the board position
def virtual_shortest_move():
    global snake, board, snake_size, tmpsnake, tmpboard, tmpsnake_size, food
    tmpsnake_size = snake_size
    tmpsnake = snake[:] # If tmpsnake=snake is directly, then both point to the same memory
    tmpboard = board[:] # The board is already the length of the path to the food at each location, no need to calculate
    board_reset(tmpsnake, tmpsnake_size, tmpboard)

    food_eated = False
    while not food_eated:
        board_refresh(food, tmpsnake, tmpboard)
        move = choose_shortest_safe_move(tmpsnake, tmpboard)
        shift_array(tmpsnake, tmpsnake_size)
        tmpsnake[HEAD] += move # Add a new position before the snake head
        # If the position of the newly added snake head is exactly the location of the food
        # Then add 1 to the length, reset the board, and the food position becomes part of the snake (SNAKE)
        if tmpsnake[HEAD] == food:
            tmpsnake_size += 1
            board_reset(tmpsnake, tmpsnake_size, tmpboard) # After the virtual run, the position of the snake on the board (label101010)
            tmpboard[food] = SNAKE
            food_eated = True
        else: # If the snake head is not the location of the food, the newly added position is the snake head, and the last one becomes a space. If the snake head is not the position of the food, the newly added position is the snake head, and the last one becomes a space.
            tmpboard[tmpsnake[HEAD]] = SNAKE
            tmpboard[tmpsnake[tmpsnake_size]] = UNDEFINED

# Call this function if there is a path between the snake and the food
def find_safe_way():
    global snake, board
    safe_move = ERR
    # Virtually run once, because it has been ensured that there is a path between the snake and the food, so the implementation is effective
    # After running, get the position of the virtual snake in the board, ie tmpboard, see label101010
    virtual_shortest_move() # the only call to this function
    if is_tail_inside(): # If there is a path between the snakeheads after the virtual operation, select the shortest path run (1 step)
        return choose_shortest_safe_move(snake, board)
    safe_move = follow_tail() # Otherwise, virtual follow_tail 1 step, if it can be done, return true
    return safe_move



curses.initscr()
win = curses.newwin(HEIGHT, WIDTH, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)
win.addch(int(food/WIDTH), food%WIDTH, '@') #ERROR!!!!!!!!1

hitSelf=0
hitWall=0
do=WIDTH
wall=[0]
for i in range(1,WIDTH):                            #top
    wall.append(i)
for i in range(WIDTH*HEIGHT-WIDTH,WIDTH*HEIGHT):    #bottom
    wall.append(i)
for i in range(0,WIDTH*HEIGHT,WIDTH):               #left
    wall.append(i)
for i in range(WIDTH-1,WIDTH*HEIGHT-1,WIDTH):       #right
    wall.append(i)

if play==1:
    f.write("HUMAN PLAYER\n")
    while key != 27:
        win.border(0)
        win.addstr(0, 2, 'S:' + str(score) + ' ')
        win.timeout(100)
        event = win.getch()
        key = key if event == -1 else event
        
        #self collision
        if snake[0] in snake[1:] : 
            hitSelf =1
            break
        #wall collision
        if snake[HEAD] in wall :
            hitWall =1
            break
        
        if key == KEY_LEFT:
            do=LEFT
            f.write("LEFT\n")
        if key==KEY_UP:
            do=UP
            f.write("UP\n")
        if key==KEY_DOWN:
            do=DOWN
            f.write("DOWN\n")
        if key==KEY_RIGHT:
            do=RIGHT
            f.write("RIGHT\n")
        # Receive keyboard input while also making the display smooth
        
        make_move(do)
       
       #self collision
      
if play==0:
    f.write("AI")
    while key != 27:
        win.border(0)
        win.addstr(0, 2, 'S:' + str(score) + ' ')
        win.timeout(1)
        # Receive keyboard input while also making the display smooth
        event = win.getch()
        key = key if event == -1 else event
        # reset board
        board_reset(snake, snake_size, board)

        # If the snake can eat food, board_refresh returns true
        #and in addition to the snakebody (= SNAKE) in the board, other element values indicate the shortest path length from the point of movment to the food
        if board_refresh(food, snake, board):
            
                #self collision
            if snake[0] in snake[1:] : 
                hitSelf =1
                break
            #wall collision
            if snake[HEAD] in wall :
                hitWall =1
                break
            
            
            
            best_move  = find_safe_way() # find_safe_way unique call
            # output moves
            if best_move==1:
                move="LEFT"
            elif best_move==-1:
                move="RIGHT"
            elif best_move==-WIDTH:
                move="UP"
            elif best_move==WIDTH:
                move="DOWN"
            f.write("find safe way"+"\t"+move+"\n")
        else:
            best_move = follow_tail()
            # output moves
            if best_move==1:
                move="LEFT"
            elif best_move==-1:
                move="RIGHT"
            elif best_move==-WIDTH:
                move="UP"
            elif best_move==WIDTH:
                move="DOWN"
            f.write("follow tail"+"\t"+move+"\n")
        if best_move == ERR:
            best_move = any_possible_move()
            # output moves
            if best_move==1:
                move="LEFT"
            elif best_move==-1:
                move="RIGHT"
            elif best_move==-WIDTH:
                move="UP"
            elif best_move==WIDTH:
                move="DOWN"
            f.write("any possible"+"\t"+move+"\n")
        # Thinking one time, only one direction, one step
        if best_move != ERR: make_move(best_move)
        else: break 
           

curses.endwin()

print("Score - " + str(score))
if hitSelf==1:
    print("HIT SELF")
    f.write("HIT SELF\n")
if hitWall==1:
    print("HIT WALL")
    f.write("HIT WALL\n")
print("view a list of moves in hw1-output.txt")
    
    
    
    
    
    
    
    
    
    
