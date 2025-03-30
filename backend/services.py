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

load_dotenv()

# Ensure a valid directory exists for images
IMAGE_DIR = "slide_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def generate_slide_image(prompt: str, style: str) -> str:
    """
    Generates an image using the Cloudflare Worker API with the given style.
    """
    try:
        WORKER_URL = "https://image-generator.worldforscience.workers.dev/"
        response = requests.post(WORKER_URL, json={"prompt": prompt, "style": style})
        
        if response.status_code == 200:
            image_data = response.content
            image_path = os.path.join(IMAGE_DIR, f"{sanitize_filename(prompt)}_{style}.png")

            with open(image_path, "wb") as img_file:
                img_file.write(image_data)

            return image_path
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"❌ Error generating image with Cloudflare Worker: {e}")
        return None

def adjust_font_size(text_frame, max_lines=8, max_font_size=Pt(20), min_font_size=Pt(12)):
    """
    Dynamically adjusts font size to fit content within the text box.
    """
    while text_frame.text and len(text_frame.text.split("\n")) > max_lines and max_font_size > min_font_size:
        max_font_size -= Pt(2)
        for paragraph in text_frame.paragraphs:
            paragraph.font.size = max_font_size

def generate_pptx(request, ppt_content: List[Dict[str, List[str]]], image_style: str = "realistic") -> str:
    try:
        prs = Presentation()
        prs.slide_width = Inches(13.33)
        prs.slide_height = Inches(7.5)

        title_bg_color = RGBColor(0, 51, 102)
        content_bg_color = RGBColor(220, 230, 241)
        text_color = RGBColor(255, 255, 255)
        bullet_color = RGBColor(0, 0, 0)

        # Title Slide
        title_slide_layout = prs.slide_layouts[5]
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
        left_side = True  # Toggle image placement
        for slide_data in ppt_content[:available_slides]:
            slide_layout = prs.slide_layouts[5]
            slide = prs.slides.add_slide(slide_layout)
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = content_bg_color

            slide_title = slide.shapes.title
            slide_title.text = slide_data["title"].strip()
            slide_title.text_frame.paragraphs[0].font.size = Pt(36)
            slide_title.text_frame.paragraphs[0].font.bold = True
            slide_title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)

            # Generate image using selected style
            image_path = generate_slide_image(slide_data["title"], image_style)
            if image_path:
                img_width, img_height = Inches(5), Inches(4)
                img_left = Inches(0.5) if left_side else Inches(7.5)
                text_left = Inches(7.5) if left_side else Inches(0.5)
                left_side = not left_side  # Toggle for next slide

                slide.shapes.add_picture(image_path, img_left, Inches(1.5), width=img_width, height=img_height)
                text_width = Inches(5.5)  # Adjust width if image present
            else:
                text_left = Inches(1)
                text_width = Inches(10)

            # Text Box for Content
            text_top, text_height = Inches(1.5), Inches(5)
            content_box = slide.shapes.add_textbox(text_left, text_top, text_width, text_height)
            text_frame = content_box.text_frame
            text_frame.word_wrap = True
            text_frame.margin_bottom = Inches(0.2)

            # Add text bullets
            font_size = Pt(20)
            for bullet in slide_data["content"]:
                p = text_frame.add_paragraph()
                p.text = bullet.strip()
                p.font.size = font_size
                p.font.color.rgb = bullet_color
                p.level = 0

            # Adjust font size if text overflows
            adjust_font_size(text_frame)

        # Thank You Slide
        thank_you_slide = prs.slides.add_slide(prs.slide_layouts[5])
        thank_you_slide.background.fill.solid()
        thank_you_slide.background.fill.fore_color.rgb = title_bg_color
        thank_you_title = thank_you_slide.shapes.title
        thank_you_title.text = "Thank You!"
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
