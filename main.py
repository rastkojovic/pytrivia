import game_utils
import sound_utils
from colorama import init as colorama_init, Fore
from html import unescape
import random
import time


colorama_init(autoreset=True)

def display_menu():
    
    game_utils.clear_terminal()
    
    if not sound_utils.sound_channel1.get_busy():
        sound_utils.sound_channel1.play(sound_utils.menu_sound, loops=-1)
    game_utils.print_logo()
    print(Fore.GREEN + "Welcome to PyTrivia!")
    
    menu_active = True
    while menu_active:
        try:
            user_choice = int(input("1. New game\n2. View leaderboard\n3. Quit\nPlease choose an option >> ").lower())
        except ValueError:
            game_utils.print_error("Invalid input! You must select option #")
            continue
            
        match user_choice:
            case 1:
                menu_active = False
                sound_utils.menu_sound.stop()
                setup_game()
            case 2:
                menu_active = False
                game_utils.display_leaderboard()
                return_to_menu_prompt()
            case 3:
                menu_active = False
                sound_utils.menu_sound.stop()
                game_utils.goodbye_message()
            case _:
                game_utils.print_error("Invalid input. Please select an option 1 - 3")
                

def return_to_menu_prompt():
    option_selected = False
    while not option_selected:
        user_input = input("Type (b) to go back (q) to quit >> ").lower()
        if user_input == "q":
            game_utils.goodbye_message()
            option_selected = True
        elif user_input == "b":
            display_menu()
            option_selected = True
        else:
            game_utils.print_error("Invalid input!")
            
# Continue or quit the game
def play_again_prompt():
    play_again = input("Would you like to play again? (y/n) >> ").lower()

    if play_again == "y":
        print("Starting new game...")
        time.sleep(game_utils.OUTPUT_READ_TIME)
        setup_game()
    else:
        game_utils.goodbye_message()
        return False
    
def setup_game():
    
    # Initialize visuals and sound
    game_utils.clear_terminal()
    game_utils.print_logo()
    if not sound_utils.sound_channel2.get_busy():
        sound_utils.sound_channel2.play(sound_utils.background_sound, loops=-1)
    
    user_data = game_utils.register_user()
    
    # Check if user wants to quit the game on every input
    if user_data is not False:
        
        username = user_data["username"]
        selected_category = game_utils.select_category()
        
        if selected_category is not False:
            
            selected_difficulty = game_utils.set_difficulty()
            if selected_difficulty is not False:

                selected_category_index = int(selected_category)
                game_data = game_utils.fetch_game_data(selected_category_index, selected_difficulty)
                
                if game_data is not False:

                    start_game(game_data, username)
      
    return False
                                

def start_game(question_data_list, username):
    
    # Define question and score counters
    questions_left = 10
    current_question_index = 0
    score = 0
    
    while questions_left:

        current_question = question_data_list[current_question_index]
        question_text = unescape(current_question["question"]) # str
        correct_answer = unescape(current_question["correct_answer"]) # str
        incorrect_answers = [unescape(encoded_str) for encoded_str in current_question["incorrect_answers"]] # list

        # Clear screen before new question
        game_utils.clear_terminal()

        # Create a list of shuffled options to display to user
        shuffled_answers = [answer for answer in incorrect_answers]
        shuffled_answers.append(correct_answer)
        random.shuffle(shuffled_answers)

        game_utils.print_logo()
        game_utils.display_answer_options(question_text, current_question_index, shuffled_answers)

        # Ask user to choose an option
        user_answer = game_utils.select_answer(shuffled_answers)

        if user_answer == False:
            return False

        score = game_utils.check_answer_update_score(user_answer, correct_answer, score)

        if questions_left > 1:
            print(f"Your new score is: {score}/10")
        else:
            game_utils.game_over_mechanic(username, score)
            play_again_prompt()

        # Sleep so the user can read output
        time.sleep(game_utils.OUTPUT_READ_TIME)

        # After every question decrease # of questions | make sure loop ends
        current_question_index += 1
        questions_left -= 1
    

def main():
    display_menu()
    

if __name__ == "__main__":
    main()