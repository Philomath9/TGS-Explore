#Logan test idk
testwhat = input("What module do you want to test? 1: Even or Odd? 2: Square, 3: Fibonacci")
if(testwhat == "1"):
    numb = input("Enter a number: ")
    if(int(numb)%2==0):
        print("Even")
    else:    print("Odd")
elif(testwhat == "2"):
    numb = input("Enter a number: ")
    print(int(numb)**2)
elif(testwhat == "3"):
    numb = input("Enter a number: ")
    a, b = 0, 1
    for i in range(int(numb)):
        print(a)
        a, b = b, a + b
else:    print("Invalid input")