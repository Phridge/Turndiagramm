from io import BytesIO
import pandas as pd
import requests
from PIL import Image
from PIL.Image import Resampling
import os.path

# Replace 'your_file.csv' with the actual path to your CSV file
file_path = 'table.csv'

def piktogramm_to_image(row):
    ref = row["Piktogramm"]
    if not ref or ref in ("-", "?", "nan"):
        return []
    # try loading the image from ref as url
    
    try:
        urls = ref.split()
        imgs = []
        for url in urls:
            resp = requests.get(url)
            image = Image.open(BytesIO(resp.content))
            imgs.append(image)
        return imgs
    except Exception as e:
        print(e)
    
    try:
        path = os.path.join("images", row["Name"].replace("/", "_") + ".png")
        image = Image.open(path)
        print("Loaded from local path", path)
        return [image]
    except Exception as e:
        print(e)

    return []


def rescale_images(imgs):
    def rescale_image(original_image):
        # Define the target height
        target_height = 200  # Replace with your desired height

        # Calculate the corresponding width to maintain the aspect ratio
        aspect_ratio = original_image.width / original_image.height
        target_width = int(target_height * aspect_ratio)

        # Resize the image while maintaining the aspect ratio
        rescaled_image = original_image.resize((target_width, target_height), Resampling.LANCZOS)

        # Save or display the rescaled image
        return rescaled_image
    return list(map(rescale_image, imgs))

def image_to_data_url(image):
    import io
    import base64

    # Convert the PIL image to bytes
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")  # Change the format accordingly

    # Encode the bytes as base64
    base64_encoded = base64.b64encode(image_bytes.getvalue()).decode("utf-8")

    # Create the data URL
    data_url = f"data:image/png;base64,{base64_encoded}"

    # Print or use the data URL as needed
    return data_url


# Load the CSV file into a DataFrame    
df = pd.read_csv(file_path)
df.where(df.notnull(), None)
df = df.loc[:1]

df["images"] = df.apply(piktogramm_to_image, axis=1)
df["images"] = df["images"].apply(rescale_images).apply(lambda imgs: list(map(image_to_data_url, imgs)))

# Display the DataFrame (optional)
print(df)


from html2image import Html2Image
from jinja2 import Template
hti = Html2Image(size=(1000, 400))

template = Template(open("format.jinja2", "r", encoding="utf-8").read())

# for id, row in df.iterrows():
for row in [df.loc[0]]:
    html = template.render(data=row)
    print(html)

    images = hti.screenshot(html_str=html, save_as="test.png")
    print(images)
