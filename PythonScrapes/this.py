# Open the file for reading
with open("this.txt", "r") as file:
    # Read each line in the file
    for line in file:
        # Strip leading and trailing whitespace
        stripped_line = line.strip()
        # If the line starts with "def" or "return"
        if stripped_line.startswith("def") or stripped_line.startswith("return"):
            print(stripped_line)  # Print the line
