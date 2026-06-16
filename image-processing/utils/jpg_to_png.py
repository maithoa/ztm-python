""" 
Convert a folder that contain jpg images to png images
Usage: python jpg_to_png.py <folder_path> [--dest <new_folder_path>] 
"""
from PIL import Image
from pathlib import Path
from argparse import ArgumentParser

def jpg_to_png(folder_path: str, new_folder_path: str| None = None) -> int:
    # 1. Make sure the inputs are clean and valid
    if not folder_path or not folder_path.strip():
        raise ValueError("Folder path cannot be empty. Please provide a valid folder path that contains JPEG images.")
        
    src_path = Path(folder_path.strip())

    if not src_path.is_dir():
        raise ValueError("Invalid folder path provided. Please provide a valid folder path that contains JPEG images.")
    
    # 2. Check if the destination folder is provided, if not use the original folder
    if new_folder_path and new_folder_path.strip():
        dest_path = Path(new_folder_path.strip())
    else:
        dest_path = src_path
    
    # 3. Create destination folder if it does not exists
    dest_path.mkdir(parents=True, exist_ok=True)
    
    # 4. Iterate through the files in the original folder, convert jpg/jpeg images to png and save them to the new folder
    processed_images_count = 0
    
    for filename in src_path.iterdir(): 
        if filename.suffix.lower() in (".jpg", ".jpeg"):
            # Load the original_image
            with Image.open(filename) as original_image:
                # Create new filename with .png extension
                new_filename = filename.with_suffix(".png").name

                # Save the loaded image in png format
                original_image.save(dest_path / new_filename)
                processed_images_count += 1

    return processed_images_count


def main() -> None:
    parser = ArgumentParser(description="Convert JPEG images to PNG format.")
    parser.add_argument("source", help="Path to the folder containing JPEG images.")
    parser.add_argument("--dest", help="Path to the folder to save the converted PNG images. If not provided, the original folder will be used.")
    
    args = parser.parse_args()

    try:
        count = jpg_to_png(args.source, args.dest)
        print(f"Successfully converted {count} images from JPEG to PNG format. and saved them to {args.dest if args.dest else args.source}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":    
    main()

