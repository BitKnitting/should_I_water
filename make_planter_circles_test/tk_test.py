import tkinter
from PIL import Image



# create a root window
root = tkinter.Tk()


# I think I can make a canvas, draw in it, then save as png.

C = tkinter.Canvas(root, bg="blue", height=250, width=300)

coord = 10, 50, 240, 210
arc = C.create_arc(coord, start=0, extent=150, fill="red")

# Pack lets tkinter decide where stuff goes
C.pack()
C.postscript(file='tk_test.eps')
img = Image.open('tk_test.eps')
img.save('tk_test.png')
#show window (run forever)
# root.mainloop()
