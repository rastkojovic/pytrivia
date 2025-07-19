import os
import time
import json
import requests
from datetime import date
import sound_utils
from colorama import Fore
from ascii_art import name_ascii_art, over_ascii_art, leaderboard_ascii_art

# Wait time for user to read output
OUTPUT_READ_TIME = 3
LEADERBOARD_PATH = os.path.join("resources", "data", "leaderboard.json")
CATEGORY_LIST = ("Video games", "Film", "Music", "Gadgets", "General knowledge")

def clear_terminal():
    os.system("cls")
    
def print_error(error_message):
    print(Fore.RED + error_message)
    
def quit_on_error(error_message):
    sound_utils.background_sound.stop()
    clear_terminal()
    print_error(error_message)
    return True
    
def print_logo():
    print(Fore.GREEN + name_ascii_art)
    
def goodbye_message():
    print("Goodbye!")
    
# Get the corresponding trivia category code from user input
def get_category_id(selected_category_index):

    match selected_category_index:
        case 1:
            return 15
        case 2:
            return 11
        case 3:
            return 12
        case 4:
            return 30
        case 5:
            return 9
        case _:
            return 0

def register_user():
    
    captured_input = False
    existing_user = False
    
    while not captured_input:
        username = input("Please enter your username: (q to quit) >> ").lower()
        
        if username != "q":
        
            if username == "":
                print_error("The username field must not be empty!")
                continue
            else:
                
                try:
                
                    # Check if username already in file    
                    with open(file=LEADERBOARD_PATH, mode="r") as leaderboard_file:
                        leaderboard_file_data = leaderboard_file.read()
                        user_data_json = json.loads(leaderboard_file_data)
                        leaderboard = user_data_json["entries"]
                        
                        if username in leaderboard:
                            existing_user = True
                            print("That user already exists")
                            response = input(f"Is {username} your username? (y/n) >> ").lower()
                            
                            if response == "n":
                                continue
                            else:
                                print(f"Welcome back {username}!")
                        
                        captured_input = True
                except FileNotFoundError:
                    print(Fore.YELLOW + "The leaderboard has not been created yet. Starting new game.")
                except json.JSONDecodeError:
                    print_error("The leaderboard file has been corrupted.")
                    os.remove(path=LEADERBOARD_PATH)
                    print(Fore.YELLOW + "File deleted. Starting new game.")
                    
                return {"username": username,"existing_user": existing_user}
        else:
            return False   

def select_category():    
    
    print("Please choose a category")
    for index, category in enumerate(CATEGORY_LIST, start=1):
        print(f"{index}. {category}")
        
    category_selected = False
    
    while not category_selected:
        
        try:
            user_input_string = input("Please select the category of questions by category # 1 - 5 (q to quit) >> ").lower()

            if user_input_string != "q":
                selected_category_index = int(user_input_string)
                
                if selected_category_index not in (1, 2, 3, 4, 5):
                    print_error("Invalid input. Categories range from 1 to 5!")
                else:
                    category_selected = True
                    return user_input_string
            else:
                print("Goodbye!")
                sound_utils.background_sound.stop()
                return False
            
        except ValueError:
            print_error("Invalid input. You must select the category by number!")
            
def select_answer(shuffled_answers):
    answer_selected = False
    while not answer_selected:
        try:
            user_input_string = input("Please select an answer # 1 - 4 (q to quit) >> ").lower()
            
            if user_input_string != "q":
                
                user_answer = int(user_input_string)
                if user_answer not in (1, 2, 3, 4):
                    print_error("Invalid input. Answers range from 1 to 4!")
                    continue
                else:
                    user_answer_string = shuffled_answers[user_answer - 1]
                    answer_selected = True
                    return user_answer_string
            
            else:
                print("Goodbye!")
                sound_utils.background_sound.stop()
                return False

        except ValueError:
            print_error("Invalid input. You must select the answer by number!")
            continue

def display_answer_options(question_text, current_question_index, shuffled_answers):
    print(Fore.GREEN + f"QUESTION {current_question_index + 1}")
    print(question_text)
    
    # Print options in different colors
    for index, answer in enumerate(shuffled_answers, start=1):
        match index:
            case 1:
                print(Fore.RED + f"{index}. {answer}")
            case 2:
                print(Fore.GREEN + f"{index}. {answer}")
            case 3:
                print(Fore.BLUE + f"{index}. {answer}")
            case 4:
                print(Fore.YELLOW + f"{index}. {answer}")
        
def check_answer_update_score(user_answer, correct_answer, score):

    if user_answer == correct_answer:
        print(Fore.GREEN + "Correct!")
        sound_utils.correct_sound.play()
        time.sleep(sound_utils.correct_sound.get_length())
        score += 1
    else:
        print(Fore.RED + "Incorrect!")
        sound_utils.incorrect_sound.play()
        time.sleep(sound_utils.incorrect_sound.get_length())

    print(f"The answer was: {correct_answer}")
    return score
        
def set_difficulty():
    
    difficulty_selected = False
    while not difficulty_selected:
        print("Please select a difficulty")
        user_input_string = input("1. Easy\n2. Medium\n3. Hard\n4. All\n(q to quit) >> ").lower()

        if user_input_string == "q": # QUIT GAME
            print("Goodbye!")
            return False

        # Map input to difficulty name
        try:
            selected_difficulty_num = int(user_input_string)

            if selected_difficulty_num not in (1, 2, 3, 4):
                print_error("Invalid input. The difficulty settings are in range 1 - 4!")
                continue

        except ValueError:
            print_error("Invalid input. You must select the difficulty by number!")
            continue

        match selected_difficulty_num:
            case 1:
                return "easy"
            case 2:
                return "medium"
            case 3:
                return "hard"
            case 4:
                return ""
        
        difficulty_selected = True
        
def fetch_game_data(selected_category_index, selected_dificulty):
    
    # TODO: Get category id from input
    category_id = get_category_id(selected_category_index)
    category_name = CATEGORY_LIST[selected_category_index - 1]

    # Request a session token -- keps track of questions the API has already provided
    token_response_text = requests.get("https://opentdb.com/api_token.php?command=request").text
    session_token = json.loads(token_response_text)["token"]

    # TODO: Get list of questions of selected category
    try:
        # Check if dificulty set and send appropriate request
        if selected_dificulty == "":
            question_data = requests.get(f"https://opentdb.com/api.php?amount=10&category={category_id}&type=multiple&token={session_token}")
        else:
            question_data = requests.get(f"https://opentdb.com/api.php?amount=10&category={category_id}&type=multiple&difficulty={selected_dificulty}&token={session_token}")

        if selected_dificulty == "":
            print(Fore.BLUE + f"You have selected: {category_name}, all difficulty levels")
        else:
            print(Fore.BLUE + f"You have selected: {category_name}, {selected_dificulty} difficulty")
        time.sleep(OUTPUT_READ_TIME)
        
        # Check if response OK
        if question_data.status_code != 200:
            quit_on_error(f"Error while fetching data: {question_data.status_code}")
            return False

        # Check API response code
        api_response_code = json.loads(question_data.text)["response_code"]
        match api_response_code:
            case 1:
                quit_on_error("Error while fetching data. No results found!")
                return False
            case 2:
                quit_on_error("Error while fetching data. Invalid parameter!")
                return False
            case 3:
                quit_on_error("Error while fetching data. Token not found!")
                return False
            case 4:
                quit_on_error("You went through all the possible questions. Resetting session token and restaring game.")
                requests.get(f"https://opentdb.com/api_token.php?command=reset&token={session_token}")
                return False
            case 5:
                quit_on_error("Error while fetching data. Rate Limit!")
                return False
        
        # Check if retrieved string is in JSON format
        try:
            question_data_json = json.loads(question_data.text)
        except json.JSONDecodeError:
            quit_on_error("JSON decoding error!")
            return False

        question_data_list = question_data_json["results"]
        return question_data_list


    except requests.exceptions.ConnectionError:
        quit_on_error("Unable to retrieve Triviadb. A connection error occured!")
        return False
    except requests.exceptions.ConnectTimeout:
        quit_on_error("Unable to retrieve Triviadb. The connection timed out!")
        return False
    except (requests.exceptions.MissingSchema, requests.exceptions.InvalidSchema, requests.exceptions.InvalidURL, requests.exceptions.URLRequired):
        quit_on_error("Unable to fetch data from TriviaDB. Invalid URL!")
        return False
    except (requests.exceptions.HTTPError):
        quit_on_error("Unable to fetch data from TriviaDB. A HTTP error occured!")
        return False
    except Exception as e:
        quit_on_error(e)
        return False
    
def update_leaderboard(username, score):
    
    current_date = date.today()

    if os.path.exists(path=LEADERBOARD_PATH):

        
        with open(file=LEADERBOARD_PATH, mode="r+") as leaderboard_file:
            leaderboard_file_json = json.loads(leaderboard_file.read())
            
            username_found = False    
            for key in leaderboard_file_json["entries"]:
                if key == username:
                    username_found = True
                    break
                
            if username_found:
    
                if score > leaderboard_file_json["entries"][username]["score"]:
                    
                    leaderboard_file_json["entries"][username]["score"] = score
                    leaderboard_file.seek(0)
                    leaderboard_file.write(json.dumps(leaderboard_file_json, indent=4))
                    leaderboard_file.truncate()
            else:
                leaderboard_file_json["entries"][username] = {"score": score, "date": str(current_date)}
                leaderboard_file.seek(0)
                leaderboard_file.write(json.dumps(leaderboard_file_json, indent=4))
                leaderboard_file.truncate()
                  
    else:
        print_error("The leaderboard file does not exist!")
        
def calc_extra_space(leaderboard_arr, current_username):
    
    max_len = 0
    for entry in leaderboard_arr:
        username_str = entry[0]
        if len(username_str) > max_len:
            max_len = len(username_str)
            
    return max_len - len(current_username)

def longest_username_len(leaderboard_arr):
    
    max_len = 0
    for entry in leaderboard_arr:
        if len(entry[0]) > max_len:
            max_len = len(entry[0])
    return max_len       
        
def display_leaderboard():
    
    PRINT_LEN_WITHOUT_USERNAME = 34
    
    clear_terminal()
    
    print(Fore.GREEN + leaderboard_ascii_art)
    with open(file=LEADERBOARD_PATH, mode="r") as leaderboard_file:
        leaderboard_file_str = leaderboard_file.read()
        # Converting dict into 2d array for easier sorting
        leaderboard_file_dict = json.loads(leaderboard_file_str)
        leaderboard_arr = [(key, value["score"], value["date"]) for key, value in leaderboard_file_dict["entries"].items()]
        leaderboard_arr = sorted(leaderboard_arr, key=lambda x: x[1], reverse=True)
        
        repeat_times = longest_username_len(leaderboard_arr)
        
        username_title_space = calc_extra_space(leaderboard_arr, "USERNAME")
        print(Fore.GREEN + "PLACE   " + "|" + Fore.RED + "  USERNAME" + Fore.GREEN + f"{username_title_space * " "}  | " + Fore.YELLOW +  "SCORE" + Fore.GREEN + " |  " + Fore.BLUE + "DATE")
        print(Fore.GREEN + "-" * (repeat_times + PRINT_LEN_WITHOUT_USERNAME))
        
        for index, entry in enumerate(leaderboard_arr, start=1):
            place_entry = index
            index_extra_space = " "
            if index in (1, 2, 3):
                index_extra_space = ""
            match index:
                case 1:
                    place_entry = "🥇"
                case 2:
                    place_entry = "🥈"
                case 3:
                    place_entry = "🥉"
                    
            username_extra_space = calc_extra_space(leaderboard_arr, entry[0])
            print(Fore.GREEN + f"{index_extra_space}{place_entry:<7}" + Fore.GREEN + "|" + Fore.RED + f"  {entry[0]}{username_extra_space * " "}" + Fore.GREEN + "  |  " + Fore.YELLOW + f"{entry[1]:<3}" + Fore.GREEN + "  |  " + Fore.BLUE + f"{entry[2]:10}")
            print(Fore.GREEN + "-" * (repeat_times + PRINT_LEN_WITHOUT_USERNAME))
    
    print(Fore.GREEN + "#")
        
        
def game_over_mechanic(username, score):
    clear_terminal()
    print(Fore.BLUE + over_ascii_art)
    print(f"Your final score is: {score}/10")
    #TODO: Check if current score is greated than user highscore
    update_leaderboard(username, score)
    sound_utils.background_sound.stop()
    sound_utils.game_over_sound.play()
    time.sleep(sound_utils.game_over_sound.get_length())