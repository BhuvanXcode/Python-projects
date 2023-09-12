import turtle

# create a turtle object
t = turtle.Turtle()

# set the turtle's speed and pen size
t.speed(0)
t.pensize(3)

# draw the dog's head
t.penup()
t.goto(0, -150)
t.pendown()
t.color("purple", "tan")
t.begin_fill()
t.circle(150)
t.end_fill()

# draw the dog's ears
t.penup()
t.goto(-75, 75)
t.pendown()
t.color("yellow", "tan")
t.begin_fill()
t.right(45)
t.circle(100, -90)
t.right(90)
t.forward(100)
t.end_fill()

t.penup()
t.goto(75, 75)
t.pendown()
t.color("brown", "tan")
t.begin_fill()
t.left(135)
t.circle(-100, -90)
t.left(90)
t.forward(100)
t.end_fill()

# draw the dog's eyes
t.penup()
t.goto(-50, 0)
t.pendown()
t.color("black", "white")
t.begin_fill()
t.circle(25)
t.end_fill()

t.penup()
t.goto(50, 0)
t.pendown()
t.color("black", "white")
t.begin_fill()
t.circle(25)
t.end_fill()

t.penup()
t.goto(-50, 5)
t.pendown()
t.color("black", "black")
t.begin_fill()
t.circle(10)
t.end_fill()

t.penup()
t.goto(50, 5)
t.pendown()
t.color("black", "black")
t.begin_fill()
t.circle(10)
t.end_fill()

# draw the dog's nose
t.penup()
t.goto(0, -40)
t.pendown()
t.color("black", "black")
t.begin_fill()
t.circle(20)
t.end_fill()

# draw the dog's tongue
t.penup()
t.goto(0, -70)
t.pendown()
t.color("red", "pink")
t.begin_fill()
t.circle(30)
t.end_fill()

# hide the turtle cursor
t.hideturtle()

# keep the window open until user closes it
turtle.done()
