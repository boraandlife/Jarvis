import json

my_list = [
    'a'
]

with open('output.json', 'w') as file:
    json.dump(my_list, file)



with open('output.json', 'r') as file:
    new_list = json.load(file)

print(new_list)