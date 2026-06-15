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

