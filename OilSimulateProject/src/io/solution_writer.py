def write_solution():
    lines = [
        "Line 1: This is the first line.\n",
        "Line 2: This is the second line.\n",
        "Line 3: This is the third line.\n"
    ]

    # Open the file in write mode
    with open("solutions/{folder}/solution{i}.txt", "w") as file:
        file.writelines(lines)

    print("Lines written to solution{i}.txt")