import multiprocessing

# initialize the value
num = 10
def childprocess():

	# refer to the global variable
	global num 
	print(f"In child process before update: {num}")

	#updating num value
	num+= 1

	print(f"In child process after update: {num}")


def mainprocess():

	# refer to the global variable
	global num 
	print(f"In parent process before update {num}")

	#updating num value
	num = 20

	print(f"In parent process after update: {num}")
	process = multiprocessing.Process(target = childprocess)
	process.start()
	process.join()
	print(f"At the end the vaule is: {num}")

if __name__ == '__main__':

	# multiprocessing.set_start_method('fork')
	print(multiprocessing.get_start_method())
	mainprocess()
