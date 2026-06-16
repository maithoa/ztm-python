# Covert a folder that contain jpg images to png images
# Usage: python jpg_to_png.py <folder_path>

from PIL import Image
import os

test_folder_path = "utils/"

def jpg_to_png(folder_path, new_folder_path=None) -> int:
    #Make sure the inputs are clean and valid
    folder_path = folder_path.strip() if folder_path else None
    new_folder_path = new_folder_path.strip() if new_folder_path else None

    if not folder_path or not os.path.exists(folder_path):
        raise ValueError("Invalid folder path provided. Please provide a valid folder path that contains JPEG images.")
    
    # If new_folder_path is not provided or is empty, use the original folder path to save the converted images
    if not new_folder_path:
        new_folder_path = folder_path
    else:
        # if not existing then create new folder
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
    
    processed_images_count = 0

    for filename in os.listdir(folder_path): 
        if(filename.endswith(".jpg")or filename.endswith("jpeg")):
            # Load the original_image
            original_image = Image.open(os.path.join(folder_path, filename))
            # Create new filename with .png extension
            new_filename = os.path.splitext(filename)[0]+".png"
            # Save the loaded image in png format
            original_image.save(os.path.join(new_folder_path, new_filename))
            processed_images_count += 1

    return processed_images_count


def main():
    folder_path = input("Enter the folder path that stores the images in JPEG format:")
    new_folder_path = input("Enter the folder path to save the converted PNG images:")
    try:
        count = jpg_to_png(folder_path, new_folder_path)
        print(f"Successfully converted {count} images from JPEG to PNG format. and saved them to {new_folder_path}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":    main()

