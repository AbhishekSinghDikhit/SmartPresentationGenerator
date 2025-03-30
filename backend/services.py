from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os
from typing import List, Dict
from dotenv import load_dotenv
import requests
from PIL import Image
import re
from time import sleep

load_dotenv()

# UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
HORDE_API_KEY = os.getenv("STABLE_HORDE_KEY")

# Ensure a valid directory exists for images
IMAGE_DIR = "slide_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

# def fetch_image_from_unsplash(query: str) -> str:
#     """Fetches an image from Unsplash API."""
#     url = f"https://api.unsplash.com/photos/random?query={query}&client_id={UNSPLASH_ACCESS_KEY}"
    
#     try:
#         response = requests.get(url)
#         if response.status_code == 200:
#             image_url = response.json()["urls"]["regular"]
#             image_path = os.path.join(IMAGE_DIR, f"{sanitize_filename(query)}.jpg")

#             # Download and save image
#             img_data = requests.get(image_url).content
#             with open(image_path, "wb") as img_file:
#                 img_file.write(img_data)

#             return image_path
#         else:
#             print(f"❌ Unsplash API Error: {response.status_code} - {response.text}")
#             return None
#     except Exception as e:
#         print(f"❌ Error fetching image from Unsplash: {e}")
#         return None

def generate_slide_image(prompt: str) -> str:
    """
    Generates an image using the Stable Horde API and saves it locally as PNG.

    Args:
        prompt (str): Description of the slide content.

    Returns:
        str: Path to the saved image, or None if the request fails.
    """
    try:
        url = "https://stablehorde.net/api/v2/generate/async"

        headers = {
            "apikey": HORDE_API_KEY,
            "Client-Agent": "SmartPresentationGenerator"
        }

        payload = {
            "prompt": prompt,
            "models": ["stable_diffusion"],
            "params": {
                "width": 512,
                "height": 512
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 202:
            data = response.json()
            request_id = data.get("id")
            print(f"✅ Image request submitted successfully! Request ID: {request_id}")

            # Poll for image completion
            status_url = f"https://stablehorde.net/api/v2/generate/status/{request_id}"
            while True:
                status_response = requests.get(status_url, headers=headers)
                status_data = status_response.json()

                if "done" in status_data and status_data["done"]:
                    if "generations" in status_data and len(status_data["generations"]) > 0:
                        image_url = status_data["generations"][0]["img"]
                        print(f"✅ Image generated successfully: {image_url}")

                        # Download the image
                        webp_path = os.path.join(IMAGE_DIR, f"{sanitize_filename(prompt)}.webp")
                        png_path = os.path.join(IMAGE_DIR, f"{sanitize_filename(prompt)}.png")

                        img_data = requests.get(image_url).content
                        with open(webp_path, "wb") as img_file:
                            img_file.write(img_data)

                        # Convert WEBP to PNG
                        with Image.open(webp_path) as img:
                            img.convert("RGB").save(png_path, "PNG")

                        print(f"✅ Converted {webp_path} to {png_path}")
                        return png_path  # Return PNG path
                    else:
                        print("❌ No image found in response.")
                        return None
                else:
                    print("⏳ Image is still being processed... Waiting 5 seconds.")
                    sleep(5)  # Wait 5 seconds before checking again

        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error generating image with Stable Horde: {e}")
        return None


    
def generate_pptx(request, ppt_content: List[Dict[str, List[str]]]) -> str:
    try:
        prs = Presentation()

        title_bg_color = RGBColor(0, 51, 102)  # Dark Blue
        content_bg_color = RGBColor(220, 230, 241)  # Light Blue
        text_color = RGBColor(255, 255, 255)  # White
        bullet_color = RGBColor(0, 0, 0)  # Black

        # Title Slide
        title_slide_layout = prs.slide_layouts[5]  # Title Only layout
        slide = prs.slides.add_slide(title_slide_layout)
        title_shape = slide.shapes.title
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = title_bg_color

        title_shape.text = request.title.strip()
        title_frame = title_shape.text_frame
        title_frame.paragraphs[0].font.size = Pt(44)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = text_color

        # Author Subtitle
        author_shape = slide.shapes.add_textbox(Inches(3), Inches(3), Inches(5), Inches(1))
        author_frame = author_shape.text_frame
        author_frame.text = f"By {request.author.strip()}"
        author_frame.paragraphs[0].font.size = Pt(28)
        author_frame.paragraphs[0].font.color.rgb = text_color

        # Content Slides
        available_slides = min(len(ppt_content), request.num_slides)
        for slide_data in ppt_content[:available_slides]:
            slide_layout = prs.slide_layouts[5]  # Title Only layout
            slide = prs.slides.add_slide(slide_layout)
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = content_bg_color

            slide_title = slide.shapes.title
            slide_title.text = slide_data["title"].strip()
            slide_title.text_frame.paragraphs[0].font.size = Pt(36)
            slide_title.text_frame.paragraphs[0].font.bold = True
            slide_title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

            # Generate image if necessary
            image_path = generate_slide_image(slide_data["title"])
            if image_path:
                img_left = Inches(0.5)
                img_top = Inches(1.5)
                img_width = Inches(4)
                img_height = Inches(3)
                slide.shapes.add_picture(image_path, img_left, img_top, width=img_width, height=img_height)
                text_left = Inches(5)
            else:
                text_left = Inches(1)

            # Text Box for Content
            text_top = Inches(1.5)
            text_width = Inches(8) if not image_path else Inches(4)
            text_height = Inches(5)
            content_box = slide.shapes.add_textbox(text_left, text_top, text_width, text_height)
            text_frame = content_box.text_frame
            text_frame.word_wrap = True
            text_frame.margin_bottom = Inches(0.2)

            # Adjust font size dynamically if needed
            max_font_size = Pt(20)
            min_font_size = Pt(10)
            font_size = max_font_size

            # Add text bullets
            for bullet in slide_data["content"]:
                bullet = bullet.strip()
                if bullet:
                    p = text_frame.add_paragraph()
                    p.text = bullet
                    p.font.size = font_size
                    p.font.color.rgb = bullet_color
                    p.level = 0

            # Reduce font size if text overflows
            while text_frame.text and len(text_frame.text.split("\n")) > 8 and font_size > min_font_size:
                font_size -= Pt(2)
                for paragraph in text_frame.paragraphs:
                    paragraph.font.size = font_size

        # "Thank You" Slide
        thank_you_slide = prs.slides.add_slide(prs.slide_layouts[5])
        thank_you_title = thank_you_slide.shapes.title
        thank_you_title.text = "Thank You!"
        thank_you_slide.background.fill.solid()
        thank_you_slide.background.fill.fore_color.rgb = title_bg_color
        thank_you_title.text_frame.paragraphs[0].font.size = Pt(44)
        thank_you_title.text_frame.paragraphs[0].font.bold = True
        thank_you_title.text_frame.paragraphs[0].font.color.rgb = text_color
        thank_you_title.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER

        # Save presentation
        file_name = f"{sanitize_filename(request.title.strip())}.pptx"
        file_path = os.path.join(os.getcwd(), file_name)
        prs.save(file_path)
        return file_path

    except PermissionError:
        raise OSError(f"Permission denied when saving file to {file_path}")
    except Exception as e:
        raise Exception(f"Failed to generate presentation: {str(e)}") 
