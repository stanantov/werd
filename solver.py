from calendar import c
import os
import re
import sys
import json
from dotenv import dotenv_values


config = {
    **dotenv_values(".env"),  # load shared development variables
    **os.environ,  # override loaded values with environment variables
}


def has_repeated_letter(letter, word):
    if word.count(letter) > 1:
        return True

    return False


# keeping words where letter is not in position
def filter_negative_pos(position, letter, possible_words):
    filtered = []
    for word in possible_words:
        # print(word, position, letter)
        if word[position] != letter:
            # print(word, position, letter)
            filtered.append(word)
    return filtered


# keeping words where letter is in position
def filter_positive_pos(position, letter, possible_words):
    filtered = []
    for word in possible_words:
        if word[position] == letter:
            filtered.append(word)
    return filtered


# keeping words where letter is in word
def filter_possible_letter(letter, possible_words):
    filtered = []
    for word in possible_words:
        if letter in word:
            filtered.append(word)
    return filtered


# keeping words where letter is in word
def filter_impossible_letter(letter, possible_words):
    filtered = []
    for word in possible_words:
        if letter not in word:
            filtered.append(word)
    return filtered


# return most popular letter in position
def most_popular_letter(position, possible_words):
    letter_count = {}
    for word in possible_words:
        letter = word[position]
        if letter in letter_count:
            letter_count[letter] += 1
        else:
            letter_count[letter] = 1
    return max(letter_count, key=letter_count.get)


# filter out a word out of a list of possibles
def filter_word(word, possible_words):
    filtered = []
    for possible_word in possible_words:
        if possible_word != word:
            filtered.append(possible_word)
    return filtered


# find most common word, based on frequency
def find_most_common_word(words):
    most_common_count = 0
    most_common_word = ""

    with open("./fivers-freq.json") as json_file:
        freq = json.load(json_file)

        for word in words:
            if word in freq:
                count = freq[word]
                if count > most_common_count:
                    most_common_count = count
                    most_common_word = word

    # did not find a word so grab the first possible one
    if not most_common_word:
        if len(words):
            return words[0]
        else:
            return None

    return most_common_word


def guess(results):
    # read file into variable
    possible = open("wordle.txt", "r").read().splitlines()

    words = {}
    for i in range(int(len(results) / 2)):
        x = i * 2
        words[results[x].lower()] = results[x + 1]

    for word in words:
        result = words[word]

        possible = filter_word(word, possible)

        for position in range(5):
            letter = word[position]
            if result[position] == "0":
                if not has_repeated_letter(letter, word):
                    possible = filter_impossible_letter(letter, possible)
                possible = filter_negative_pos(position, letter, possible)

            if result[position] == "1":
                possible = filter_possible_letter(letter, possible)
                possible = filter_negative_pos(position, letter, possible)

            if result[position] == "2":
                possible = filter_possible_letter(letter, possible)
                possible = filter_positive_pos(position, letter, possible)

    # propose a word
    proposed = find_most_common_word(possible)
    return proposed


def check(test_word):
    # print(f"Check({test_word})...")
    if "WERD" not in config:
        exit("No word specified")

    werd = config["SOLUTION"].lower()
    test_word = test_word.lower()

    if len(werd) > 5 or len(test_word) > 5:
        exit("Word too long")

    result = ""

    for pos in range(5):
        if test_word[pos] in werd:
            if test_word[pos] == werd[pos]:
                result += "2"
            else:
                result += "1"
        else:
            result += "0"

    return result


# start the game
def play(solution, quiet=False):
    config["SOLUTION"] = solution

    won = 0
    first_word = "crane"  # suggested by Anna
    guesses = 1

    result = check(first_word)
    if not quiet:
        print(f"#1: First word: {first_word}: {result}")
    results = []
    results.append(first_word)
    results.append(result)

    while not won:
        guesses += 1
        proposed = guess(results)
        # print(f"Guess() proposed {proposed}")
        if not proposed:
            if not quiet:
                print(f"I'm out of words... :(")
            won = guesses
            if not quiet:
                print(f"Gave up after {guesses - 1} guesses")
            break

        result = check(proposed)
        if not quiet:
            print(f"#{guesses}: Proposed word: {proposed}: {result}")
        if result == "22222":
            won = guesses
            if not quiet:
                print(f"Won in {guesses} guesses")
        else:
            results.append(proposed)
            results.append(result)

    return won


if len(sys.argv) > 1:
    print(f"Solving for {sys.argv[1]}")
    solution = sys.argv[1]
    won = play(solution)
else:
    print("Self-play all words")
    count = 0
    sum = 0
    failed = 0
    won_sum = 0

    allwords = open("official.txt", "r").read().splitlines()
    allwordcount = len(allwords)
    for word in allwords:
        count += 1
        print(f"{count}/{allwordcount} {word} {count/allwordcount*100:.2f}%")
        won = play(word, quiet=True)
        if won > 6:
            failed += 1
        else:
            sum += won

    print(f"Won {count - failed} out of {count}.")
    print(f"Solve rate: {(count - failed)/allwordcount * 100:.2f}%")
    print(f"Average words per solve: {sum / (count - failed):.2f}")
