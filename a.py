

import psutil

# Get the process object for the Python file
p = psutil.Process()


with open("messages.txt", "a") as file:
    file.write("H")



# Get the disk I/O activity for the process
io = p.io_counters()

# Print the disk I/O activity
print(io)