import os

cd = os.getcwd()

while True:
    command = input(f"{cd} > ")

    if command == "exit":
        break
    if command == "neburust -u":
    os.system(command)
