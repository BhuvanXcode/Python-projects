from PIL import Image, ImageDraw

# Set up the dimensions and background color
width, height = 200, 200
background_color = (280,280,280)

# Create a list of frames
frames = []
for i in range(10):
    # Create a new frame
    im = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(im)
    
    # Draw a circle that moves across the image
    radius = 30
    x = i * 20
    y = 100
    draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=(200,200,120))
    
    # Add the frame to the list
    frames.append(im)

# Save the frames as an animated GIF
frames[0].save('animation.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
