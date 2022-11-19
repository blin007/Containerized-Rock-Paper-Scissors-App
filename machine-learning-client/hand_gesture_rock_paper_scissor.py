# TechVidvan hand Gesture Recognizer

# import necessary packages

import cv2
import numpy as np
import random
import math
import mediapipe as mp
import tensorflow as tf
import time
from tensorflow.keras.models import load_model

# initialize mediapipe
mpHands = mp.solutions.hands
hands = mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
mpDraw = mp.solutions.drawing_utils

# Load the gesture recognizer model
model = load_model('mp_hand_gesture')

# Load class names
f = open('gesture.names', 'r')
classNames = f.read().split('\n')
f.close()
print(classNames)


class StaticVariables:
    '''
    Variables that should not be modified throughout lifetime of the game.
    '''

    props = ['rock', 'paper', 'scissor']
    '''
    The props for the game. Contains list of 3 elements: 'rock', 'paper', 'scissor'.
    '''

    user_win_conditions = {'rock': 'scissor', 'paper': 'rock', 'scissor': 'paper'}
    '''
    The key of the dictionary is what the user plays. 
    The value is what the computer needs to play for the user to win.
    '''

    BLACK = (0, 0, 0)
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    ORANGE = (0, 165, 255)


def predict_gesture(frame):
    '''
    This is the ml prediction of the gesture based on the frame. 
    Source: https://techvidvan.com/tutorials/hand-gesture-recognition-tensorflow-opencv/
    '''

    x, y, c = frame.shape

    # Flip the frame vertically
    frame = cv2.flip(frame, 1)
    framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Get hand landmark prediction
    result = hands.process(framergb)

    # print(result)
    
    className = ''

    # post process the result
    if result.multi_hand_landmarks:
        landmarks = []
        for handslms in result.multi_hand_landmarks:
            for lm in handslms.landmark:
                # print(id, lm)
                lmx = int(lm.x * x)
                lmy = int(lm.y * y)

                landmarks.append([lmx, lmy])

            # Drawing landmarks on frames
            mpDraw.draw_landmarks(frame, handslms, mpHands.HAND_CONNECTIONS)

            # Predict gesture
            prediction = model.predict([landmarks])
            # print(prediction)
            classID = np.argmax(prediction)
            className = classNames[classID]
    return (className, frame)

def display_content(frame, text: str, location: tuple, color: tuple):
    '''
    Render a text onto the frame at the specific location with a specific color and display it to the user.

    frame is the frame to display to the user.

    text is the string to render onto the frame.

    location is a tuple with 2 elements, representing the x and y coordinates.
    
    color is a tuple with 3 elements, representing Blue, Green, Red
    '''

    # put the text at the location with the specified color formatted as bgr.
    cv2.putText(frame, str(text), location, cv2.FONT_HERSHEY_SIMPLEX, 
            1, color, 2, cv2.LINE_AA)
    # show the frame with the time
    show_frame(frame)

def computer_plays() -> str:
    '''
    Determine what the computer plays.

    Returns either a 'rock', 'paper', or 'scissor'.
    '''
    cp_play = StaticVariables.props[math.floor(random.random()*3)]
    return cp_play

def handle_play(user_play, cp_play):
    '''
    user_play is either 'rock', 'paper', 'scissor', or ''.

    cp_play is either 'rock', 'paper', or 'scissor'.

    Returns 'user' for user victory. Returns 'cp' for computer victory. Returns 'tie' for a tie.
    Anything else means that a tie or invalid input was detected.
    '''

    #If user did not play a valid prop value, then return None
    if not user_play in StaticVariables.props:
        return None
    
    # if user played the same prop as the computer, we have a tie
    if user_play == cp_play:
        return 'tie'
    # check condition for user victory
    elif StaticVariables.user_win_conditions[user_play] == cp_play:
        return 'user'
    # otherwise, the computer wins.
    else:
        return 'cp'

def show_frame(frame):
    '''
    Display the current frame to the user.
    '''

    cv2.imshow("Output", frame)
    if cv2.waitKey(1) == ord('q'):
        raise Exception("Exiting")

def establish_web_cam_connection():
    '''
    Attempts to establish web cam connection for a number of times.
    '''

    # Initialize the webcam
    cap = cv2.VideoCapture(0)
    print("Cap:", cap)
    for i in range(10):
        print("Trying to establish connection. Trial", i)
        if not cap.read()[0]:
            time.sleep(2)
            cap = cv2.VideoCapture(0)
        else:
            return cap
    raise WebCamConnection("Cannot connect to camera.")

def end_program(cap):
    '''
    Performs action before exiting the program. Releases resources that program is using.
    '''

    # release the webcam and destroy all active windows
    cap.release()
    cv2.destroyAllWindows()
    print("Completed Exit steps")

def final_result_text(user_victory, cp_victory):
    '''
    Processes the number of victories and returns a tuple of what to display to the user.
    The first element of the tuple is the string to display to the user.
    The second element of the tuple is the color that the text to display should be.
    '''

    if user_victory > cp_victory:
        display_text = "You have Won!!!"
        color = StaticVariables.GREEN
    elif user_victory == cp_victory:
        display_text = "It is a tie"
        color = StaticVariables.ORANGE
    else:
        display_text = "The computer has won"
        color = StaticVariables.RED
    display_text += " " + str(user_victory) + ' : ' + str(cp_victory)
    return (display_text, color)


def storeToMongo():
    # TODO: mongo operations on storing details of the round.
    pass

def main(seconds_per_round, num_of_rounds):
    print("Game is starting...")
    # number of computer victories
    cp_victory = 0 
    # number of user victories
    user_victory = 0
    # number of ties
    tie_victory = 0
    try:
        # start off with a new round
        new_round = True
        # try establishing web cam connection
        cap = establish_web_cam_connection()
        # while we have not completed numOfRounds
        while num_of_rounds:
            if new_round:
                new_round = False
                oldTime = time.time()
                curTime = time.time()
            else:
                curTime = time.time()

            display_text = int(seconds_per_round + oldTime - curTime) + 1

            # Read each frame from the webcam
            _, frame = cap.read()
            # print("This is cap read:", cap.read())

            # get the predicted gesture along with the modified frame.
            gesture, frame = predict_gesture(frame)

            # display the gesture of the user.
            display_content(frame, gesture, (10, 50), StaticVariables.BLACK)

            # display the time left for the user to play
            display_content(frame, display_text, (100, 100), StaticVariables.RED)

            # if the time is up
            if display_text <= 0:
                # let the computer make its move
                cp_play = computer_plays()

                # tell the user what the computer played
                display_text = "Computer Plays " + cp_play
                display_content(frame, display_text, (10, 150), (255, 0, 0))

                # get the current time
                curTime = time.time()

                # process results
                result = handle_play(gesture, cp_play)

                # save details into the db, etc.
                storeToMongo()
                
                # sleep for the leftover time
                time.sleep(4 + curTime - time.time())

                # render the results based on the status
                if result == 'user':
                    display_content(frame, "You Win!!!", (10, 200), StaticVariables.GREEN)
                    # decrement the number of rounds left
                    num_of_rounds -= 1
                    user_victory += 1
                elif result == 'cp':
                    display_content(frame, "You Lose", (10, 200), StaticVariables.RED)
                    # decrement the number of rounds left
                    num_of_rounds -= 1
                    cp_victory += 1
                elif result == 'tie':
                    display_content(frame, "Tie", (10, 200), StaticVariables.ORANGE)
                    # decrement the number of rounds left
                    num_of_rounds -= 1
                    tie_victory += 1
                else:
                    display_content(frame, "Try again", (10, 200), StaticVariables.ORANGE)
                # we are ready for a new round
                new_round = True

                # give the user 3 seconds to see the results
                time.sleep(3)
    except WebCamConnection as e:
        print(e)
    except Exception as e:
        print(e)
        end_program(cap)
    else:
        # at successful completion, display frame with all results
        display_text, color = final_result_text(user_victory, cp_victory)
        display_content(frame, display_text, (10, 250), color)

        display_text = "Press any key to quit"
        display_content(frame, display_text, (10, 300), StaticVariables.BLACK)
        cv2.waitKey(0)
        end_program(cap)

class WebCamConnection(Exception):
    pass

if __name__ == '__main__':
    main(5, 5)