#Logan test idk
import random


testwhat = input("What module do you want to test? 1: Even or Odd? 2: Square, 3: Fibonacci, 4: Rock, Paper, Scissors? ")
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
elif(testwhat == "4"):
    rockpaperscissors = input("Rock, Paper, or Scissors? ").strip().capitalize()
    computerchoice = random.choice(["Rock", "Paper", "Scissors"])
    print("Computer chose: " + computerchoice)
    if(rockpaperscissors == "Rock" and computerchoice == "Scissors"):
        print("You win!")
    elif(rockpaperscissors == "Rock" and computerchoice == "Paper"):
        print("You lose!")
    elif(rockpaperscissors == "Scissors" and computerchoice == "Paper"):
        print("You win!")
    elif(rockpaperscissors == "Scissors" and computerchoice == "Rock"):
        print("You lose!")
    elif(rockpaperscissors == "Paper" and computerchoice == "Rock"):
        print("You win!")
    elif(rockpaperscissors == "Paper" and computerchoice == "Scissors"):
        print("You lose!")
    else:    print("Invalid input")
else:    print("Invalid input")