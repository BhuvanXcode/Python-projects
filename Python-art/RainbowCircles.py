import turtle

# Set up the Turtle
t = turtle.Turtle()
t.speed(0)
t.hideturtle()

# Define the colors
color1 = "red"
color2 = "blue"

# Draw the illusion
for i in range(30):
    t.color(color1)
    t.circle(100)
    t.color(color2)
    t.circle(90)
    t.left(12)

# Keep the window open until manually closed
turtle.done()
