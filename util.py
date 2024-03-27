with open("messages.txt",'r') as file:
     data = (file.read()).split("\n")
     print(len(data))
  
    #  print(data[0].split('\n'))
     # https://upcloud.com/resources/tutorials/configure-load-balancing-nginx