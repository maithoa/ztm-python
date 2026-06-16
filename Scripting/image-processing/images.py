from PIL import Image, ImageFilter

folder_path = "Pokedex/"

img = Image.open(folder_path + "pikachu.jpg")

# Print image
print(img)

# Print image mode
print (img.mode)

# Filter image
filtered_img = img.filter(ImageFilter.BLUR)

# Save filtered image 
filtered_img.save(folder_path + "pikachu_blur.jpg")

# Sharper image
sharper_img = img.filter(ImageFilter.SHARPEN)
sharper_img.save(folder_path + "pikachu_sharper.jpg")

#sharper_img.show()

# Resize_image
sharper_img.resize((200, 200)).save(folder_path + "pikachu_resized.jpg")

# Crop image
box = (100, 100, 400, 400)
cropped_img = img.crop(box)
cropped_img.save(folder_path + "pikachu_cropped.jpg")
