import os
import glob
from PIL import Image

# 1. Define the folder containing your PNG images and the output path
image_folder = "plots/ky_yearly_flash_floods_maps"
output_gif_path = "plots/ky_yearly_flash_floods_animation.gif"

# 2. Gather and sort the PNG files so they play in the correct chronological order
# Using sorted() prevents frames from rendering out of order.
png_files = sorted(glob.glob(os.path.join(image_folder, "*.png")))

# 3. Create an empty list to store the image objects (frames)
frames = []

# 4. Use a for loop to loop through the PNG images and open them
for file_path in png_files:
    img = Image.open(file_path)
    # Force the PNG into full RGB color mode to clear any existing localized palettes
    rgb_img = img.convert("RGB")
    frames.append(rgb_img)

# 5. Create the GIF using the first frame to save the entire sequence
if frames:
    frames[0].save(
        output_gif_path,
        format="GIF",
        append_images=frames[1:],  # Append the remaining frames
        save_all=True,             # Ensure all images in the list are included
        duration=1200,             # Display duration for each frame in milliseconds
        loop=0                     # 0 means the GIF will loop infinitely
    )
    print(f"Successfully created GIF at: {output_gif_path}")
else:
    print("No PNG images found in the specified directory.")