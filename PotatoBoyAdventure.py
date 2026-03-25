'''
Potato Boy Adventure
Created By: Chris Herriman Jr
Goal: Beat All Levels

Character Descriptions:
-Potato Boy - Player
-Pepper Kid - Stationary Target
-Broccoli Guy - Moving Target
-Carrots Men - Moving Enemy
'''

### IMPORTS ###
import turtle as trtl #Turtle interface, used for game functionality and visuals, shortened to trtl
import random as rnd #Random, used to randomly generate enemy movements, shortened to rnd
from pygame import mixer #Mixer from the pygame library, used for music loops and sound effects
import os, sys #For pyinstaller

### Makes onefile mode work in pyinstaller
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

### Game Base and Screen Setup ###
trtl.clear()
screen = trtl.Screen()
trtl.title("Potato Boy Adventure")
screen.setup(750,750)
screen.bgpic(resource_path("UIElements/titleScreen.gif"))
#Calls to tkinter
screen._root.resizable(False, False) #Sets the screen to not be resizable
screen._root.iconbitmap(resource_path("UIElements/potatoBoy.ico")) #Sets up the app icon
#Create game state flags
game_over = False #Marks when the player dies
level_transitioning = False #Used to prevent timer leaks between levels
initial_timer_call = False #False until player hits new game or a new world, used to allow timer to work after the first attempt
#Hit Sound and Music Setup
mixer.init()
music_loop = resource_path("AudioTracks/Music/world2Music.wav") #Created by user FlavioConcini on freesound.org
mixer.music.load(music_loop)
mixer.music.play(-1)
hit_sound = mixer.Sound(resource_path('AudioTracks/hitSound.wav')) #Created by user Sadiquecat on freesound.org

#Sets up new worlds
def new_world(x=0,y=0): #x and y are required for the onclick function
    global world, level, initial_timer_call
    world += 1
    level = 0
    screen.update()
    screen.clear()
    clear_lists()
    screen.bgpic(resource_path("Backgrounds/world" + str(world) + ".gif"))
    mixer.music.stop()
    mixer.music.load(resource_path("AudioTracks/Music/world" + str(world) + "Music.wav"))
    mixer.music.play(-1)
    setup_hearts(3)
    setup_key_presses()
    setup_level_num(False)
    full_timer_setup(not initial_timer_call)
    initial_timer_call = True
    setup_player(False)
    hide_timer()
    next_level()
    
#Set level counter
world = 0
level = 0

### Function to condense object setup lines ###  
def setup_objects(game_object, object_model, object_x, object_y, start_shown, already_registered):
    game_object.speed(0)
    game_object.hideturtle()
    game_object.penup()
    if not already_registered: #Prevents registering a model twice
        screen.addshape(resource_path(object_model))
    game_object.shape(resource_path(object_model))
    game_object.goto(object_x,object_y)
    if start_shown: #Determines if the object being created will be shown to start the ga
        game_object.showturtle()

#Create Start Game Button
screen.addshape(resource_path("UIElements/startGameButton.gif"))
start_game_button = trtl.Turtle()
def setup_start_button(first_setup):
    global start_game_button
    if not first_setup:
        start_game_button = trtl.Turtle()
    setup_objects(start_game_button,"UIElements/startGameButton.gif",0,-100,True,False)

### Player Setup ###
player_frame_state = True
num_player_movement_frames = 2
player_frames = []
for i in range(num_player_movement_frames):
    player_frames.append("CharacterModels/potatoFrame" + str(i+1) + ".gif")
player = trtl.Turtle()
player.hideturtle()
for i in range(len(player_frames)):
    screen.addshape(resource_path(player_frames[i]))
def setup_player(first_setup):
    global player
    if not first_setup:
        player = trtl.Turtle()
    setup_objects(player,player_frames[0],100,-100,True,False)
player_movement_speed = 15

### Pepper Kid Setup ###
screen.addshape(resource_path("CharacterModels/pepperKid.gif"))
peppers = []
def setup_peppers(num_peppers,x_cors,y_cors):
    for p in peppers:
        p.hideturtle()
    peppers.clear()
    for i in range(num_peppers):
        p = trtl.Turtle()
        peppers.append(p)
        setup_objects(p,"CharacterModels/pepperKid.gif",x_cors[i],y_cors[i],True,True)

### Broccoli Guy Setup ###
num_broccoli_frames = 2
broccoli_frames = []
for i in range(num_broccoli_frames):
    broccoli_frames.append("CharacterModels/broccoliFrame" + str(i+1) + ".gif")
broccoli_frame_state = []
for i in range(len(broccoli_frames)):
    screen.addshape(resource_path(broccoli_frames[i]))
broccoli = []
def setup_broccoli(num_broccoli,x_cors,y_cors):
    for b in broccoli:
        b.hideturtle()
    broccoli.clear()
    broccoli_frame_state.clear()
    for i in range(num_broccoli):
        b = trtl.Turtle()
        broccoli.append(b)
        setup_objects(b,broccoli_frames[0],x_cors[i],y_cors[i],True,True)
        broccoli_frame_state.append(True)
broccoli_movement_speed = 17
broccoli_movement_generation = 0

### Carron Man Setup ###
num_carrot_frames = 2
carrot_frames = []
for i in range(num_carrot_frames):
    carrot_frames.append("CharacterModels/carrotFrame" + str(i+1) + ".gif")
carrot_frame_state = []
for i in range(len(carrot_frames)):
    screen.addshape(resource_path(carrot_frames[i]))
carrots = []
def setup_carrots(num_carrots,x_cors,y_cors):
    for c in carrots:
        c.hideturtle()
    carrots.clear()
    carrot_frame_state.clear()
    for i in range(num_carrots):
        c = trtl.Turtle()
        carrots.append(c)
        setup_objects(c,"CharacterModels/carrotFrame1.gif",x_cors[i],y_cors[i],True,True)
        carrot_frame_state.append(True)
carrot_movement_speed = 5
carrot_movement_generation = 0
current_carrot_chase_time = -1

### Hearts Setup ###
#Hearts are 70x pixels apart
lives = 3
screen.addshape(resource_path("UIElements/heart.gif")) #Heart model
screen.addshape(resource_path("UIElements/damaged.gif")) #Sprite for when the player gets hurt
hearts = []
def setup_hearts(num_hearts):
    global lives
    while len(hearts) > 0:
        hearts[0].hideturtle()
        hearts.pop(0)
    for i in range(num_hearts):
        if i >= len(hearts):
            hearts.append(trtl.Turtle())
            setup_objects(hearts[i],"UIElements/heart.gif",(-310 + (70*i)),295,True,True)
    #Makes it so damage stays consistent across worlds
    temp_lives = lives
    lives = 3
    for i in range(3 - temp_lives):
        damaged()

### Create Timer and Timer Icon ###
#Timer Icon
screen.addshape(resource_path("UIElements/timer.gif"))
timer_icon = trtl.Turtle()
#Timer Variable
timer_value = 0
stop_timer = True
timer_generation = 0
def setup_timer_icon(first_call):
    global timer_icon
    if not first_call:
        timer_icon = trtl.Turtle()
    setup_objects(timer_icon,"UIElements/timer.gif",135,290,True,False)

## Pixel Numbers ##
numbers = []
for i in range(10):
    numbers.append("PixelNumbers/" + str(i) + ".gif")
    screen.addshape(resource_path(numbers[i]))
#Create turtles for ones, tens, and hundreds place
digits = []
for i in range(3):
        digits.append(trtl.Turtle())
def setup_on_screen_digits(first_call):
    if not first_call:
        digits.clear()
        for i in range(3):
            digits.append(trtl.Turtle())
    num_list = calculate_timer_digits()
    for i in range(3):
        setup_objects(digits[i],numbers[num_list[i]],260 - (40*i),290,True,True)

### Allows for calls that require setup_on_screen_digits and setup_timer_icon to be called at one time ###
#Also allows setup_on_screen_digits and setup_timer_icon to be called seperately
def full_timer_setup(first_call):
    setup_timer_icon(first_call)
    setup_on_screen_digits(first_call)

### Calculates the on screen digits ###
def calculate_timer_digits():
    timer_math = timer_value
    num_list = []
    if timer_value >= 0:
                for i in range(len(digits)):
                    num_list.append(timer_math % 10)
                    timer_math = int(timer_math / 10)
    return num_list

### Hides the timer and timer icon for non-timed levels ###
def hide_timer():
    timer_icon.hideturtle()
    for i in range(len(digits)):
        digits[i].hideturtle()
hide_timer()

### Reverses the hide_timer function --- Reveals the timer and the timer icon ###
def reveal_timer():
    timer_icon.showturtle()
    for i in range(len(digits)):
        digits[i].showturtle()

### Sets up the game over text on screen ###
def setup_game_over():
    game_over_text = trtl.Turtle()
    setup_objects(game_over_text,"UIElements/gameOver.gif",-35,30,True,False)

### Sets up the new game button on screen ###
def setup_new_game_button():
    new_game_button = trtl.Turtle()
    setup_objects(new_game_button,"UIElements/newGame.gif",0,-150,True,False)
    #Activates the new game button to restart the game
    new_game_button.onclick(new_game)

### Activates when clicked by the new game button, resets the game to level 1-1 ###
def new_game(x,y): #x and y are required for on click
    global world, level, game_over, lives, initial_timer_call, timer_value
    #Reset game state and logic variables
    lives = 3
    game_over = False
    if not initial_timer_call:
        initial_timer_call = True
    #Starts the game back from 1-1 by calling new_world while world is 0
    world = 0
    timer_value = 5
    new_world()

### Displays the world and level in the x-x format ###
level_display_numbers = []
for i in range(10):
    level_display_numbers.append("PixelNumbers/small" + str(i) + ".gif")
    screen.addshape(resource_path(level_display_numbers[i]))
screen.addshape(resource_path("PixelNumbers/dash.gif"))
### Sets up the on screen level numbers
on_screen_level_num = []
for i in range(3):
    on_screen_level_num.append(trtl.Turtle())
def setup_level_num(first_call):
    if not first_call:
        on_screen_level_num.clear()
        for i in range(3):
            on_screen_level_num.append(trtl.Turtle())
    setup_objects(on_screen_level_num[0],level_display_numbers[world],-30,290,True,True)
    setup_objects(on_screen_level_num[1],"PixelNumbers/dash.gif",0,290,True,True)
    setup_objects(on_screen_level_num[2],level_display_numbers[1],30,290,True,True)

### Updates the on screen level number ###
def update_level_num():
    on_screen_level_num[0].shape(resource_path(level_display_numbers[world]))
    on_screen_level_num[2].shape(resource_path(level_display_numbers[level]))
    

### Clears the lists used to keep track of non player characters ###
def clear_lists():
    global peppers, broccoli, carrots, carrot_frame_state
    peppers.clear()
    broccoli.clear()
    broccoli_frame_state.clear()
    carrots.clear()
    carrot_frame_state.clear()

### Checks If Enemies And/Or The Player Is Out Of Bounds ###
def check_out_bounds(speed, direction, x_cor, y_cor):
    if direction == 90 and y_cor + speed < 330: #Check up
        return True 
    elif direction == 270 and y_cor - speed > -290: #Check down
        return True
    elif direction == 0 and x_cor + speed < 300: #Check right
        return True
    elif direction == 180 and x_cor - speed > -320: #Check left
        return True
    return False

### Player Movement Functions ###
#Refactored from 4 different functions
def move_player(direction):
    global level_transitioning, game_over
    if game_over:
        return
    x_cor, y_cor = player.position()
    player.seth(direction)
    if check_out_bounds(player_movement_speed, direction, x_cor, y_cor):
        animate_player()
        player.forward(player_movement_speed)
        pepper_collision_checks()

### Condenses the code for collision checks between the player and the peppers to one place ###
def pepper_collision_checks():
    global level_transitioning, carrot_movement_generation, broccoli_movement_generation
    try:
        for i in reversed((range(len(peppers)))):
            if check_collision(peppers[i]):
                #Works as invincibility frames to prevent double collection
                level_transitioning = True
                screen.ontimer(unlock_level_transition, 50)
                #Starts brocoli movement back up after level_transition flag is called
                if len(broccoli) > 0:
                    screen.ontimer(lambda: move_broccoli(broccoli_movement_generation), 100)
                if len(carrots) > 0:
                    gen = carrot_movement_generation
                    screen.ontimer(lambda: move_carrots(gen), 100)
                #Removes the collected pepper from the game
                peppers[i].hideturtle()
                peppers.pop(i)
                #Check for the end of the level post transition
                screen.ontimer(check_end_level, 75) #Delays check_end_level due to the unlock_level_transition timer
                break #Stops for loop at 1 collision
    #Stops stray collision checks
    except IndexError:
        return

### Plays Player Animations ###
def animate_player():
    global player_frame_state
    player_frame_state = not player_frame_state
    if player_frame_state == True:
        player.shape(resource_path(player_frames[0]))
    else:
        player.shape(resource_path(player_frames[1]))

### Check For Collisions ###
def check_collision(npc):
    if level_transitioning:
        return False
    player_x, player_y = player.position()
    npc_x_cor, npc_y_cor = npc.position()
    if (player_x - npc_x_cor < 45 and player_x - npc_x_cor > -45) and (player_y - npc_y_cor < 70 and player_y - npc_y_cor > -70):
        hit_sound.play()
        return True
    return False

### Checks if level is done, and if so, sets up the next level ###
def check_end_level():
    global level, stop_timer, level_transitioning, game_over, lives
    if level_transitioning or game_over:
        return
    #World 1 level endings
    if world == 1:
        #Level 1-1
        if level == 1:
            if len(peppers) < 1:
                next_level()
        #Level 1-2
        elif level == 2:
            if len(peppers) < 1:
                next_level()
        #Level 1-3
        elif level == 3:
            if len(broccoli) < 1:
                next_level()
        #Level 1-4
        elif level == 4:
            if len(broccoli) < 1 and len(peppers) < 1:
                next_level()
        #Level 1-5
        elif level == 5:
            if timer_value <= 0:
                stop_game(False)
            elif len(peppers) < 1:
                stop_timer = True
                next_level()
        #Level 1-6
        elif level == 6:
            if timer_value <= 0:
                for c in carrots:
                    c.hideturtle()
                carrots.clear()
                carrot_frame_state.clear()
                stop_timer = True
                next_level()
    ##Start of World 2##
    elif world == 2:
        #Level 2-1
        if level == 1:
            if len(peppers) < 1:
                for c in carrots:
                    c.hideturtle()
                carrots.clear()
                carrot_frame_state.clear()
                next_level()
        #Level 2-2
        elif level == 2:
            if len(peppers) < 1:
                for c in carrots:
                    c.hideturtle()
                carrots.clear()
                carrot_frame_state.clear()
                next_level()
        #Level 2-3
        elif level == 3:
            if len(broccoli) < 1:
                for c in carrots:
                    c.hideturtle()
                carrots.clear()
                carrot_frame_state.clear()
                next_level()
        #Level 2-4
        elif level == 4:
            if timer_value <= 0:
                stop_game(False)
            elif len(peppers) < 1: 
                stop_timer = True
                for c in carrots:
                    c.hideturtle()
                carrots.clear()
                carrot_frame_state.clear()
                next_level()
        #Level 2-5
        elif level == 5:
            if timer_value <= 0:
                stop_game(False)
            elif len(broccoli) < 1: 
                stop_timer = True
                next_level()
        #Level 2-6
        elif level == 6:
            if timer_value <= 0:
                for c in carrots:
                    c.hideturtle()
                carrots.clear()
                carrot_frame_state.clear()
                stop_timer = True
                next_level()

### Player Damaged ###
def damaged():
    global lives
    if lives > 0:
        lives = lives - 1
        hearts[lives].shape(resource_path("UIElements/damaged.gif"))
        if lives == 0:
            stop_game(False)

### Brocoli Movement ###
def move_broccoli(gen = 0):
    global broccoli_movement_generation
    try:
        if level_transitioning or game_over: 
                return
        if gen == broccoli_movement_generation:
            for i in reversed(range(len(broccoli))):
                random_movement(broccoli[i], broccoli_movement_speed)
                animate_broccoli(broccoli[i], i)
                if check_collision(broccoli[i]):
                    broccoli[i].hideturtle()
                    broccoli.pop(i)
                    broccoli_frame_state.pop(i)
            #Checks if the game is over
            #If the game is over, the carrot timer will stop
            if len(broccoli) > 0:
                screen.ontimer(lambda: move_broccoli(gen), 100)
    #Stops stray movement loops
    except IndexError:
        return
    check_end_level()

### Carrot Movement ###
#Negative value for start_follow_time makes carrots always random
def move_carrots(gen = 0):
    global carrot_movement_speed, level_transitioning, game_over, carrot_movement_generation, current_carrot_chase_time, broccoli_movement_speed
    try:     
        if level_transitioning or game_over: 
                return
        if gen == carrot_movement_generation:
            for i in range(len(carrots)):
                if timer_value > current_carrot_chase_time:
                    random_movement(carrots[i], carrot_movement_speed)
                else:
                    if carrot_movement_speed != 5 and timer_value < current_carrot_chase_time:
                        carrot_movement_speed = 5
                    follow_player(carrots[i])
                animate_carrot(carrots[i], i)
                if check_collision(carrots[i]):
                    level_transitioning = True
                    screen.ontimer(unlock_level_transition, 50)
                    #Starts brocoli movement back up after level_transition flag is called
                    if len(broccoli) > 0:
                        screen.ontimer(lambda: move_broccoli(broccoli_movement_generation), 100)
                    jump_in_bounds = False
                    while not jump_in_bounds:
                        direction = rnd.randint(0,3)*90
                        jump_in_bounds = check_out_bounds(300, direction, carrots[i].xcor(), carrots[i].ycor())
                    carrots[i].seth(direction)
                    carrots[i].forward(300)
                    damaged()
                    screen.ontimer(check_end_level, 75) #Delays check_end_level due to the unlock_level_transition timer
                    break #Stops for loop at 1 collision
            #Checks if the game is over
            #If the game is over, the carrot timer will stop
            if not game_over:
                screen.ontimer(lambda: move_carrots(gen), 50) #restart carrot movement loop
    #Stops stray movement loops
    except IndexError:
        return

### Random Movement
def random_movement(npc, speed):
    direction = rnd.randint(0,3) * 90
    x_cor, y_cor = npc.position()
    #Checks if the move will bring the carrot out of bounds
    if check_out_bounds(speed, direction, x_cor, y_cor):
        npc.seth(direction)
        npc.forward(speed)

### Move Towards Player AI ###
# Effective speed is 1.41x speed
def follow_player(carrot):
    if player.xcor() > carrot.xcor():
        carrot.seth(0)
        carrot.forward(carrot_movement_speed)
    else:
        carrot.seth(180)
        carrot.forward(carrot_movement_speed)
    if player.ycor() > carrot.ycor():
        carrot.seth(90)
        carrot.forward(carrot_movement_speed)
    else:
        carrot.seth(270)
        carrot.forward(carrot_movement_speed)

### Swaps between frames to animate carrots ###
def animate_carrot(carrot, carrot_num):
    global carrot_frame_state
    try:
        if len(carrots) > 0: #Helps to prevent against bugs caused by carrots being deleted mid animation
            carrot_frame_state[carrot_num] = not carrot_frame_state[carrot_num]
            if carrot_frame_state[carrot_num] == True:
                carrot.shape(resource_path(carrot_frames[0]))
            else:
                carrot.shape(resource_path(carrot_frames[1]))
    #Stops stray animations
    except IndexError:
        return
    
def animate_broccoli(this_broccoli, broccoli_num):
    global broccoli_frame_state
    try:
        if len(broccoli) > 0: #Helps to prevent against bugs caused by broccoli being deleted mid animation
            broccoli_frame_state[broccoli_num] = not broccoli_frame_state[broccoli_num]
            if broccoli_frame_state[broccoli_num] == True:
                this_broccoli.shape(resource_path(broccoli_frames[0]))
            else:
                this_broccoli.shape(resource_path(broccoli_frames[1]))
    #Stops stray animations
    except IndexError:
        return

#End the game
def stop_game(victory):
    global game_over
    #Mark the game as over
    game_over = True
    clear_lists()
    screen.clear()
    if victory:
        screen.bgpic(resource_path("UIElements/youWin.gif"))
    else:
        screen.bgpic(resource_path("Backgrounds/world2.gif"))
        setup_game_over()
    setup_new_game_button()

### Key Presses For Player Movement ###
#Seperate function to allow for clear in new worlds
def setup_key_presses():
    #Looks for key presses
    screen.listen() 
    #Up Movements
    screen.onkey(lambda: move_player(90), "Up")
    screen.onkey(lambda: move_player(90), "w")
    screen.onkey(lambda: move_player(90), "W") #Counters capslock
    #Left Movements
    screen.onkey(lambda: move_player(180), "Left")
    screen.onkey(lambda: move_player(180), "a")
    screen.onkey(lambda: move_player(180), "A") #Counters capslock
    #Right Movements
    screen.onkey(lambda: move_player(0), "Right")
    screen.onkey(lambda: move_player(0), "d")
    screen.onkey(lambda: move_player(0), "D") #Counters capslock
    #Down Movements
    screen.onkey(lambda: move_player(270), "Down")
    screen.onkey(lambda: move_player(270), "s")
    screen.onkey(lambda: move_player(270), "S") #Counters capslock

### Disables level_transitioning flag, used to prevent double calls ###
def unlock_level_transition():
    global level_transitioning
    level_transitioning = False

def next_level():
    global level_transitioning, broccoli_movement_generation, carrot_movement_generation, level, world, current_carrot_chase_time, carrot_movement_speed
    level +=1
    update_level_num()
    screen.update()
    level_transitioning = True
    ### World 1: Dirt Field (Tutorial) ###
    if world == 1:
        #Level 1-1: Collect 1 Static Pepper
        if level == 1:
            pepper_coordinates = [[0],[0]]
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0], pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
        #Level 1-2: Collect 2 Static Peppers
        elif level == 2:
            player.goto(200,-200)
            pepper_coordinates = [[0,150],[0,200]]
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0], pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
        #Level 1-3: Collect 1 Moving Broccoli
        elif level == 3:
            player.goto(0,0)
            broccoli_coordinates = [[-200],[200]]
            broccoli_movement_generation += 1
            setup_broccoli(calc_max_npcs(broccoli_coordinates),broccoli_coordinates[0],broccoli_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            screen.ontimer(lambda: move_broccoli(broccoli_movement_generation), 100)
        #Level 1-4: Collect 1 Moving Broccoli and 2 Static Peppers
        elif level == 4:
            player.goto(0,0)
            broccoli_coordinates = [[-200],[200]]
            pepper_coordinates = [[-200,0],[0,200]]
            broccoli_movement_generation += 1
            setup_broccoli(calc_max_npcs(broccoli_coordinates),broccoli_coordinates[0],broccoli_coordinates[1])
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0], pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            screen.ontimer(lambda: move_broccoli(broccoli_movement_generation), 100)
        #Level 1-5: Collect 4 Static Peppers in 30 Seconds
        elif level == 5:
            player.goto(0,0)
            pepper_coordinates = [[200,200,-200,-200],[200,-200,200,-200]]
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0],pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            start_timer(30)
            reveal_timer()
        #Level 1-6 (Boss Level) Survive 15 Seconds Against an Enemy Carrot
        elif level == 6:
            player.goto(0,0)
            carrot_coordinates = [[175],[175]]
            setup_carrots(calc_max_npcs(carrot_coordinates),carrot_coordinates[0],carrot_coordinates[1])
            start_timer(15)
            screen.ontimer(unlock_level_transition, 50)
            carrot_movement_generation += 1
            current_carrot_chase_time = 10
            screen.ontimer(lambda: move_carrots(carrot_movement_generation), 100)
        #Jump to world 2
        else:
            new_world()
    ### World 2: Grasslands (Potato Boy Survival Callback) ###
    elif world == 2:    
        #Level 2-1: Collect one static pepper with a randomly moving carrot in the middle
        if level == 1:
            player.goto(-300,-300)
            carrot_coordinates = [[0],[0]]
            pepper_coordinates = [[300],[300]]
            setup_carrots(calc_max_npcs(carrot_coordinates),carrot_coordinates[0],carrot_coordinates[1])
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0],pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            carrot_movement_generation += 1
            current_carrot_chase_time = -1
            screen.ontimer(lambda: move_carrots(carrot_movement_generation), 100) #Negative value makes carrots always random
        #Level 2-2: Collect one static pepepr with 2 randomly moving carrots blocking the path
        elif level == 2:
            player.goto(-300,-300)
            carrot_coordinates = [[100,-100],[-100,100]]
            pepper_coordinates = [[300],[300]]
            setup_carrots(calc_max_npcs(carrot_coordinates),carrot_coordinates[0],carrot_coordinates[1])
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0],pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            carrot_movement_generation += 1
            current_carrot_chase_time = -1 #Negative value makes carrots always random
            screen.ontimer(lambda: move_carrots(carrot_movement_generation), 100) 
        #Level 2-3: Collect one moving broccoli with 2 randomly moving broccoli
        elif level == 3:
            player.goto(-300,-300)
            carrot_coordinates = [[100,-100],[-100,100]]
            broccoli_coordinates = [[200],[200]]
            setup_carrots(calc_max_npcs(carrot_coordinates),carrot_coordinates[0],carrot_coordinates[1])
            setup_broccoli(calc_max_npcs(broccoli_coordinates),broccoli_coordinates[0],broccoli_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            carrot_movement_generation += 1
            current_carrot_chase_time = -1 #Negative value makes carrots always random
            screen.ontimer(lambda: move_carrots(carrot_movement_generation), 100)
            broccoli_movement_generation += 1            
            screen.ontimer(lambda: move_broccoli(broccoli_movement_generation), 100)
        #Level 2-4: Collect one static pepper with a following pepper in the middle, in 20 seconds
        elif level == 4:
            player.goto(-300,-300)
            carrot_coordinates = [[100],[100]]
            pepper_coordinates = [[300],[300]]
            setup_carrots(calc_max_npcs(carrot_coordinates),carrot_coordinates[0],carrot_coordinates[1])
            setup_peppers(calc_max_npcs(pepper_coordinates),pepper_coordinates[0],pepper_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            carrot_movement_generation += 1
            current_carrot_chase_time = 20 #Set chase time as the timer time to have carrots always chase
            screen.ontimer(lambda: move_carrots(carrot_movement_generation), 100)
            reveal_timer()
            start_timer(20)
        #Level 2-5: Collect three randomly moving broccoli in 20 seconds
        elif level == 5:
            player.goto(-200,-200)
            broccoli_coordinates = [[200,200,-200],[200,-200,200]]
            setup_broccoli(calc_max_npcs(broccoli_coordinates),broccoli_coordinates[0],broccoli_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            broccoli_movement_generation += 1            
            screen.ontimer(lambda: move_broccoli(broccoli_movement_generation), 100)
            start_timer(20)
        #Level 2-6: Potato Boy Adventure Callback, survive 30 seconds
        elif level == 6:
            player.goto(-100,100)
            carrot_coordinates = [[250,250,-250],[250,-250,-250]]
            setup_carrots(calc_max_npcs(carrot_coordinates),carrot_coordinates[0],carrot_coordinates[1])
            screen.ontimer(unlock_level_transition, 50)
            carrot_movement_generation += 1      
            current_carrot_chase_time = 15
            carrot_movement_speed = 15
            screen.ontimer(lambda: move_carrots(carrot_movement_generation), 100)
            start_timer(30)
        else:
            stop_game(True)

### Protects against an uneven number of coordinates
def calc_max_npcs(npc_coordinates):
    try:
        #Protects against invalid data being passed through
        if len(npc_coordinates) != 2:
            return 0
        return min(len(npc_coordinates[0]),len(npc_coordinates[1]))
    #Protects against invalid data being passed through
    except TypeError:
        return 0

### Starts update_timer and sets timer_value ###
def start_timer(set_time):
    global timer_value, stop_timer, timer_generation
    stop_timer = False
    timer_value = set_time
    timer_generation += 1
    gen = timer_generation
    #Makes sure that the timer for each level starts at the correct value
    num_list = calculate_timer_digits()
    for i in range(len(digits)):
        digits[i].shape(resource_path(numbers[num_list[i]]))
    #Starts the update_timer
    screen.ontimer(lambda: update_timer(gen), 1000)

#Counts down the timer
def update_timer(gen):
    global timer_value, stop_timer, timer_generation
    if gen != timer_generation:
        return
    if not game_over and not stop_timer:
        timer_value -= 1
        num_list = calculate_timer_digits()
        for i in range(len(digits)):
            digits[i].shape(resource_path(numbers[num_list[i]]))
        if timer_value <= 0:
            stop_timer = True
            check_end_level()
        else:
            screen.ontimer(lambda: update_timer(gen), 1000) #restart timer loop

#Create the new game button
setup_start_button(True)
start_game_button.onclick(new_world)

#Allow for key presses
setup_key_presses()

#Sets the screen to the main loop
trtl.mainloop()


### Credits ###
'''
Publisher: 
->DuckTape Games

Software Developer: 
->Chris Herriman Jr

Visual Asset Production: 
->Chris Herriman Jr

Sound Effects:
->Hit Sound: "Woosh - Metal tea strainer 1" Created by user Sadiquecat on freesound.org

Music:
->World 1 Music: "drums bass 125 bpm" created by user FlavioConcini on freesound.org
->World 2 Music: "Violin Drum loop" created by user EEE3333E on freesound.org
'''
#Woosh - Metal tea strainer 1 by Sadiquecat -- https://freesound.org/s/742832/ -- License: Creative Commons 0
#drums bass 125 bpm by FlavioConcini -- https://freesound.org/s/843066/ -- License: Creative Commons 0
#Violin Drum loop by EEE3333E -- https://freesound.org/s/842764/ -- License: Creative Commons 0
