from PIL import Image

im = Image.open('MarioKart.png') # Can be many different formats.
pix = im.load()
array = []
print(im.size)  # Get the width and hight of the image for iterating over
for i in range(0, 1024, 32):
    
    list = []
    for j in range(0, 1024, 32):
        
        list.append(pix[j,i])
    print(list)
    
