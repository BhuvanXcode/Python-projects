# Importing the required modules
import tkinter as tk
from tkinter import filedialog

# Defining the Notepad class
class Notepad:
    # Initializing the class
    def __init__(self, master):
        self.master = master
        master.title("Untitled - IdeaPad")
        self.textarea = tk.Text(master, undo=True)
        self.textarea.pack(fill=tk.BOTH, expand=True)
        self.filename = None
        
        # Create a menu bar
        menubar = tk.Menu(master)
        master.config(menu=menubar)
        
        # Create a "File" menu with "Open", "Save", and "Save As" options
        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As", command=self.save_file_as)
        menubar.add_cascade(label="File", menu=file_menu)
    
    # Define a method to open a file
    def open_file(self):
        # Get the file path using filedialog
        file_path = filedialog.askopenfilename()
        if file_path:
            # Read the contents of the file and insert it into the textarea
            with open(file_path, "r") as f:
                content = f.read()
                self.textarea.delete("1.0", tk.END)
                self.textarea.insert(tk.END, content)
            self.filename = file_path
            # Update the window title to include the filename
            self.master.title(self.filename + " - Notepad")
    
    # Define a method to save a file
    def save_file(self):
        if self.filename:
            # If a filename exists, write the contents of the textarea to the file
            with open(self.filename, "w") as f:
                f.write(self.textarea.get("1.0", tk.END))
        else:
            # If no filename exists, prompt the user to save the file as
            self.save_file_as()
    
    # Define a method to save a file as a new filename
    def save_file_as(self):
        # Get the file path using filedialog
        file_path = filedialog.asksaveasfilename(defaultextension=".txt")
        if file_path:
            # Write the contents of the textarea to the new file
            with open(file_path, "w") as f:
                f.write(self.textarea.get("1.0", tk.END))
            self.filename = file_path
            # Update the window title to include the new filename
            self.master.title(self.filename + " - Notepad")

# Create the Tkinter root window
root = tk.Tk()

# Create an instance of the Notepad class
notepad = Notepad(root)

# Start the Tkinter event loop
root.mainloop()