import turtle

# Set up the screen
screen = turtle.Screen()
screen.title("Bouncing Ball Animation")
screen.bgcolor("black")
screen.setup(width=600, height=600)

# Create the ball turtle
ball = turtle.Turtle()
ball.shape("circle")
ball.color("white")
ball.penup()

# Set the initial position and speed of the ball
ball.goto(0, 250)
ball.dy = -5

# Define the main animation loop
while True:
    # Move the ball
    ball.sety(ball.ycor() + ball.dy)

    # Check for collision with the top or bottom walls
    if ball.ycor() > 280 or ball.ycor() < -280:
        ball.dy *= -1

    # Update the screen
    screen.update()

