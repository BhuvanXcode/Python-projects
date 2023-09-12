import turtle
import random

# create a turtle object
my_turtle = turtle.Turtle()

# set the turtle's speed and pen size
my_turtle.speed(0)
my_turtle.pensize(2)

# create a list of colors
colors = ["red", "orange", "yellow", "green", "blue", "purple"]

# draw the spiral
for i in range(300):
    color = random.choice(colors)  # choose a random color from the list
    my_turtle.pencolor(color)
    my_turtle.forward(i * 2)
    my_turtle.right(119)

# hide the turtle cursor
my_turtle.hideturtle()

# keep the window open until user closes it
turtle.done()
