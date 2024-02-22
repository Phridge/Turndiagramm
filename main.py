from io import BytesIO
import jinja2
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
df["images"] = df["images"].apply(rescale_images)
df["image_urls"] = df["images"].apply(lambda imgs: list(map(image_to_data_url, imgs)))

# Display the DataFrame (optional)
print(df)


# from html2image import Html2Image
# from jinja2 import Template
# hti = Html2Image(size=(1000, 400))

# template = Template(open("format.jinja2", "r", encoding="utf-8").read())

# # for id, row in df.iterrows():
# for row in [df.loc[0]]:
#     html = template.render(data=row)
#     print(html)

#     images = hti.screenshot(html_str=html, save_as="test.png")
#     print(images)


# Sieht scheise aus
# import tkinter as tk
# from tkinter import ttk
# from PIL import Image, ImageTk

# class CardRenderer:
#     def __init__(self, master, data):
#         self.master = master
#         self.master.title("Card Renderer")

#         # Left side: Canvas
#         self.left_canvas = tk.Canvas(master, width=400, height=200, bg="white")
#         self.left_canvas.grid(row=0, column=0, padx=0, pady=0)

#         # Right side: Treeview
#         self.right_tree = ttk.Treeview(master, columns=("Name", "Datum"), show="headings")
#         self.right_tree.heading("Name", text="Name")
#         self.right_tree.heading("Datum", text="Datum")
#         self.right_tree.grid(row=0, column=1, padx=0, pady=0)

#         # Create style for the Treeview

#         # Sample data for the Treeview
#         for i in range(7):
#             self.right_tree.insert("", "end", values=("", ""))

#         # Sample data for the left side
#         title = data["Name"] # "Card Title"
#         datapoints = [f"Typ: {data['Typ']}"] # ["Label1: Value1", "Label2: Value2", "Label3: Value3"]
#         image = data["images"][0]

#         # Draw on the left canvas
#         self.draw_left_card(title, datapoints, image)

#     def draw_left_card(self, title, datapoints, image):
#         # Clear the canvas
#         self.left_canvas.delete("all")

#         # Title
#         title_font = ("Arial", 16, "bold")
#         self.left_canvas.create_text(10, 10, text=title, anchor="nw", font=title_font)

#         # Datapoints
#         datapoint_font = ("Arial", 12)
#         for i, datapoint in enumerate(datapoints):
#             self.left_canvas.create_text(10, 40 + i * 20, text=datapoint, anchor="nw", font=datapoint_font)

#         # Image
#         # image = Image.open(image_path)
#         image = image.resize((400, 200), Resampling.LANCZOS)  # Resize as needed
#         photo = ImageTk.PhotoImage(image)

#         self.left_canvas.image = photo  # Keep a reference to the image to prevent garbage collection
#         self.left_canvas.create_image(10, 30, anchor="nw", image=photo)


# root = tk.Tk()
# app = CardRenderer(root, df.iloc[0])
# root.mainloop()


# Funktioniert nicht weil native bib fehlt
# import cairosvg

# width = 600
# height = 300
# cairosvg.svg2png(url='Turnen Card.svg', write_to='test.png', output_width=width, output_height=height)

import subprocess
inkscape = r"C:\Program Files\Inkscape\bin\inkscape.exe" # path to inkscape executable

def svg_render(data):
    import tempfile
    template = jinja2.Template(open("Turnen Card.svg.jinja2", "r").read())
    save_file = open("temp.svg", "w+")

    save_file.write(template.render(data))
    save_file.flush()

    input_svg_path = "temp.svg"
    output_png_path = "test.png"
    width = 600
    height = 300


    # read svg file -> write png file
    subprocess.run([inkscape, '--export-type=png', f'--export-filename={output_png_path}', f'--export-width={width}', f'--export-height={height}', input_svg_path])

    save_file.close()
    # read svg file -> png data
    # result = subprocess.run([inkscape, '--export-type=png', '--export-filename=-', f'--export-width={width}', f'--export-height={height}', input_svg_path], capture_output=True)
    #   (result.stdout will have the png data)

    # svg string -> write png file
    # subprocess.run([inkscape, '--export-type=png', f'--export-filename={output_png_path}', f'--export-width={width}', f'--export-height={height}', '--pipe'], input=svg_str.encode())

    # svg string -> png data
    # result = subprocess.run([inkscape, '--export-type=png', '--export-filename=-', f'--export-width={width}', f'--export-height={height}', '--pipe'], input=svg_str.encode(), capture_output=True)
    #   (result.stdout will have the png data)

data = df.iloc[0].to_dict()

svg_render(data)