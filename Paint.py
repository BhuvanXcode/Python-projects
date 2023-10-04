from tkinter import *
from tkinter import colorchooser, filedialog
from PIL import ImageGrab, ImageTk, Image

# create a window
root = Tk()

# set the window title
root.title("Painting Interface")

# create a canvas
canvas = Canvas(root, width=500, height=500, bg="white")
canvas.pack()

# define the choose_color function
def choose_color():
    global brush_color
    brush_color = colorchooser.askcolor()[1]

# define the drawing function
def draw(event):
    x, y = event.x, event.y
    canvas.create_oval(x-3, y-3, x+3, y+3, fill=brush_color, outline=brush_color)

# bind the canvas to the mouse events
canvas.bind("<B1-Motion>", draw)

# add a color chooser button
color_button = Button(root, text="Choose Color", command=choose_color)
color_button.pack()

# add a clear button to clear the canvas
def clear_canvas():
    canvas.delete("all")

clear_button = Button(root, text="Clear Canvas", command=clear_canvas)
clear_button.pack()

# add a save button to save the canvas
def save_canvas():
    file_path = filedialog.asksaveasfilename(defaultextension=".png")
    if file_path:
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        ImageGrab.grab().crop((x,y,x1,y1)).save(file_path)

save_button = Button(root, text="Save Canvas", command=save_canvas)
save_button.pack()

# add an open button to open an existing image
def open_canvas():
    file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg;*.gif")])
    if file_path:
        img = Image.open(file_path)
        img = img.resize((500, 500))
        img = ImageTk.PhotoImage(img)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=NW, image=img)
        canvas.image = img

open_button = Button(root, text="Open Canvas", command=open_canvas)
open_button.pack()

# set the default brush color
brush_color = "black"

# start the event loop
root.mainloop()
