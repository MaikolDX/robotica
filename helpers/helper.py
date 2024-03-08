import os


def save_image(image, output_folder, filename="output_image.jpg"):
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Save the image to the output folder
    output_path = os.path.join(output_folder, filename)
    image.save(output_path)
    print(f"Image saved to: {output_path}")