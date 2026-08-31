import random
import datetime
from typing import Any

import requests

# DAILY: Determines whether the game should choose a seed based off of the current day or not
# COLORBLIND: If true, prints direct results instead of colored text
# WORD_LENGTH: Anything other than 5 uses an API, max of 15, min of 2
# USE_DICTIONARY_API: If false, disables the check to see if you guessed a valid word. Doesn't disable the answer generator.
settings: dict[str,Any] = {
    'DAILY': False,
    'MAX_GUESSES': 6,
    'COLORBLIND': False,
    'WORD_LENGTH': 6,
    'USE_DICTIONARY_API': True
}


def change_setting(setting: str, description: str):
    """
    Prompts the user to input a new value for setting with description.

    Args:
        setting: the setting to change, must be in Settings dictionary.
        description: the description to display to the user
    Returns:
        None
    """
    if setting not in settings:
        return
    allowed_type = type(settings[setting])  # type: ignore
    print(f"Input desired value for the following setting: {setting}")
    new_value = input(f"Description: {description}\nNew value:")
    
    if allowed_type is bool:
        if new_value.lower() == 'true':
            new_value = True
        elif new_value.lower() == 'false':
            new_value = False
        else:
            print("Enter either 'true' or 'false'.")
            change_setting(setting,description)
            return
    elif allowed_type is int:
        try:
            new_value = int(new_value)
        except ValueError:
            print("Please enter a valid integer.")
            change_setting(setting,description)
            return
    settings[setting] = new_value


change_setting('DAILY','Determines whether the game should choose a seed based off of the current day or not. ONLY WORKS WITH 5 LETTER ANSWERS')
change_setting('MAX_GUESSES','The maximum amount of times you can guess')
change_setting('COLORBLIND',"Use if you can't see the colors or are COLORBLIND")
change_setting('WORD_LENGTH','The length of the answer. Values other than 5 use an API. Value must be >1 <16')
change_setting('USE_DICTIONARY_API','If false, disables valid word check for answers not length 5.')

RANDOM_WORD_API = 'https://random-word-api.herokuapp.com/word'
DICTIONARY_API = 'https://api.dictionaryapi.dev/api/v2/entries/en/'


def request_data(url: str):
    """Requests data from a website with given url parameter"""
    headers = {
        "User-Agent": "WordleBot/1.0",
        "Accept": "application/json"
    }
    request = requests.get(url, headers=headers)
    return request.json()

# Allows colored text to be printed in the console
class Color:
    GREEN = '\033[32m' 
    YELLOW = '\033[33m' 
    WHITE = '\033[37m'
    RESET = '\033[0m'


class Wordle:
    def __init__(
            self,*,MAX_GUESSES: int = 6, DAILY: bool = False,
            COLORBLIND: bool = False, WORD_LENGTH: int = 5,
            USE_DICTIONARY_API: bool = True
        ):
        """
        Initializes a new wordle game.

        Args:
            MAX_GUESSES: The amount of time a player can guess
            DAILY: Whether or not to use rng based off current day
            COLORBLIND: Whether or not to display results colored
            WORD_LENGTH: The length of the answer
            USE_DICTIONARY_API: Whether or not to use the diciontary API to check if words are valid
        Returns:
            None
        """

        WORD_LENGTH = min(WORD_LENGTH,15)
        WORD_LENGTH = max(2,WORD_LENGTH)

        self.answer_list: list[str] = []
        with open('unit-1-welcome/answers.txt','r',encoding='utf-8') as f:
            for line in f:
                self.answer_list.append(line.strip())
        self.word_list: list[str] = []
        with open('unit-1-welcome/words.txt','r',encoding='utf-8') as f:
            for line in f:
                self.word_list.append(line.strip())

        self.guesses: list[str] = []
        self.results: list[list[str]] = []

        self.USE_DICTIONARY_API: bool = USE_DICTIONARY_API

        self.MAX_GUESSES: int = MAX_GUESSES
        self.COLORBLIND: bool = COLORBLIND
        self.won: bool = False

        if WORD_LENGTH == 5:
            self.answer = self.generate_answer(DAILY)
        else:
            print("Calling dictionary API...")
            self.answer = request_data(RANDOM_WORD_API + '?length=' + str(WORD_LENGTH))[0]

            if not self.answer:
                print("API call failed, defaulting to default word length (5)")
                self.answer = self.generate_answer(DAILY)


        self.start_game()

    # Should return something like this if successful:
    # ['Green','Green','Yellow','Grey','Grey']
    def guess(self) -> list[str] | None:
        """Prompts the player to guess a new word

        Args:
            None
        Returns:
            results: The colors that correspond with the player's guess
        """
        print(f"Guesses left: {self.MAX_GUESSES - len(self.guesses)}/{self.MAX_GUESSES}")
        print("----------------------")
        player_guess = input(f"Guess a {len(self.answer)} letter word: ")

        try:
            player_guess = player_guess.lower()
        except Exception:
            print("Error while trying to lower player guess")
            self.guess()
            return

        if len(player_guess) != len(self.answer):
            print(f"\nGuess must be {len(self.answer)} letters.\n")
            self.guess()
            return

        if player_guess in self.guesses:
            print("\nAlready guessed word.\n")
            self.guess()
            return

        if len(self.answer) == 5:
            if player_guess not in self.word_list:
                print("\nGuess not in word list.\n")
                self.guess()
                return
        elif self.USE_DICTIONARY_API:
            try:
                print("Checking dictionary for guess...")
                print("Requesting:",DICTIONARY_API+player_guess)
                data = request_data(DICTIONARY_API+player_guess)
                
                if data is None:
                    retry = input("DictionaryAPI failed to return data, retry? (y/n):")

                    if 'y' in retry:
                        print("Retrying.")
                        self.guess()
                    else:
                        print("Retrying without API.")
                        self.USE_DICTIONARY_API = False
                        self.guess()
                    return
                data[0] # Errors if the API returns a blank table instead of a definition
            except Exception:
                print("Could not find word in dictionary API")
                self.guess()
                return
        
        results: list[str] = ['' for _ in self.answer]
        found_letters: list[str] = []

        for index,letter in enumerate(player_guess):
            if letter == self.answer[index]:

                # Prevents case where guessing a letter n times can cause letter to show greater than n times
                # Happens because yellow letter does not check future cases
                if self.answer.count(letter) <= found_letters.count(letter):
                    for i in range(0,index):
                        if results[i] == 'Yellow' and player_guess[i] == letter:
                            found_letters.remove(player_guess[i])
                            results[i] = 'Grey'

                found_letters.append(letter)
                results[index] = 'Green'
            elif self.answer.count(letter) > found_letters.count(letter):
                found_letters.append(letter)
                results[index] = 'Yellow'
            else:
                results[index] = 'Grey'

        self.guesses.append(player_guess)
        self.results.append(results)
        self.display_guess(player_guess,results)

        if player_guess == self.answer:
            self.won = True

        return results


    def display_guess(self,guess: str, results: list[str]) -> None:
        """
        Prints out the player's guess with colors

        Args:
            guess: The player's guess
            results: The colors to display
        """
        guess_index = self.guesses.index(guess)
        if guess_index > 0:
            self.display_guess(self.guesses[guess_index - 1],self.results[guess_index - 1])

        if self.COLORBLIND:
            print(results)
            return

        string = ""

        for index,letter in enumerate(guess):
            if results[index] == 'Green':
                string += Color.GREEN + letter.upper() + Color.RESET
            elif results[index] == 'Yellow':
                string += Color.YELLOW + letter.upper() + Color.RESET
            else:
                string += Color.WHITE + letter.upper() + Color.RESET
        
        print(string)


    def generate_answer(self, DAILY: bool = False) -> str:
        """Generates an answer for the wordle"""
        if DAILY:
            today = datetime.date.today().isoformat()
            random.seed(today)

        return random.choice(self.answer_list)


    # Main game loop, function should end when the game is over
    def start_game(self) -> None:
        """The main game loop"""
        while len(self.guesses) < self.MAX_GUESSES and not self.won:
            self.guess()
        if self.won:
            print(f"You won!\nYou correctly guessed the word {self.answer}.\nGuesses used: {len(self.guesses)}")
        else:
            print(f"You lost.\nThe word was: {self.answer}")

game = Wordle(**settings)
