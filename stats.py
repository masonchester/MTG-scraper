import os

path = os.path.expanduser("~/MTG-scraper/data/")

file_list = os.listdir(path)

# Initialize variables to store total word length and count of words
n = len(file_list)
words = 0
# Iterate through the files and calculate word lengths
for filename in file_list:
    file_path = os.path.join(path, filename)
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            file_contents = file.read()
            words += len(file_contents.split())
            
print("Avg file size is :", words/ n)
print(n)
