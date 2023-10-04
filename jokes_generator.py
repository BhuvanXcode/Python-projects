import tkinter as tk
import requests

# Define a function to generate a random dad joke
def generate_joke():
    response = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"})
    joke_text = response.text
    joke_label.config(text=joke_text)

# Create the main window
root = tk.Tk()
root.title("Dad Joke Generator")

# Create a label to display the dad joke
joke_label = tk.Label(root, text="")
joke_label.pack()

# Create a button to generate a new dad joke
joke_button = tk.Button(root, text="Generate Joke", command=generate_joke)
joke_button.pack()

# Run the main loop to start the application
root.mainloop()
 