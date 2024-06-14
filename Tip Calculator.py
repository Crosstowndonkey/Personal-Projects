#If the bill was $150.00, split between 5 people, with 12% tip. 
"""
12 / 100
0.12
150 * 0.12
18.0
150 + 18
168
150 * 1.12
168.00000000003
168 / 5
33.6
round to 2 decimal places
"""
#Each person should pay (150.00 / 5) * 1.12 = 33.6
#Format the result to 2 decimal places = 33.60

#Tip: There are 2 ways to round a number. You might have to do some Googling to solve this.💪

#Write your code below this line 👇

print("Welcome to the tip calculator!")
total_bill = input("What was the total bill? ")
total_bill_as_int = int(total_bill)
tip_percentage = input("How much of a tip would you like to give? 10, 12 or 15? ")
tip_percentage_as_int = int(tip_percentage)
how_many_people = input("how many people split the bill? ")
how_many_people_int = int(how_many_people)

user_tip_percentage = tip_percentage_as_int / 100
total_tip = total_bill_as_int * user_tip_percentage
total_cost = total_bill_as_int + total_tip 
individual_cost = total_cost / how_many_people_int
individual_cost_rounded = round(individual_cost, 2)

print(f"Each Person should pay: ${individual_cost_rounded}")