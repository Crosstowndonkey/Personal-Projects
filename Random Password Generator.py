# Password Generator Project
import random

letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R',
           'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

print("Welcome to the PyPassword Generator!")
nr_letters = int(input("How many letters would you like in your password?\n"))
nr_symbols = int(input(f"How many symbols would you like?\n"))
nr_numbers = int(input(f"How many numbers would you like?\n"))

pass_letters = ""
for abc in range(1, nr_letters + 1):
    pass_letters += random.choice(letters)
print(pass_letters)

pass_symbols = ""
for sym in range(1, nr_symbols + 1):
    pass_symbols += random.choice(symbols)
print(pass_symbols)

pass_numbers = ""
for num in range(1, nr_numbers + 1):
    pass_numbers += random.choice(numbers)
print(pass_numbers)

my_list = [pass_letters, pass_symbols, pass_numbers]
# make strings into lists
let_list = list(pass_letters)
sym_list = list(pass_symbols)
num_list = list(pass_numbers)
# combine lists
big_list = let_list + sym_list + num_list
# shuffle big list
random.shuffle(big_list)

# join big list together as string
password = "".join(big_list)

print(f'Your password is {password}')


