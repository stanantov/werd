import csv

possible = open("fivers.txt", "r").read().splitlines()

with open("unigram_freq.csv", newline="") as csvfile:
    freq_data = csv.reader(csvfile, delimiter=",")
    for row in freq_data:
        if len(row[0]) == 5 and row[0] in possible:
            print(f'"{row[0]}": {row[1]},')
