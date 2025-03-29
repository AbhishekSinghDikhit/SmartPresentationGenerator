from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import os
import re
from typing import List, Dict
from diffusers import StableDiffusionPipeline
import torch
import comtypes.client  # For adding transitions (Windows only)

# Ensure a valid directory exists for images
IMAGE_DIR = "slide_images"
os.makedirs(IMAGE_DIR, exist_ok=True)

# Load Stable Diffusion model using diffusers
# device = "cuda" if torch.cuda.is_available() else "cpu"
# pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0")
# pipe.to(device)

class PresentationRequest:
    def __init__(self, title: str, author: str, num_slides: int):
        self.title = title
        self.author = author
        self.num_slides = num_slides

def sanitize_filename(filename: str) -> str:
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def generate_slide_image(prompt: str) -> str:
    """Generates an image using Stable Diffusion and saves it locally."""
    image = pipe(prompt).images[0]  # Generate image
    sanitized_prompt = sanitize_filename(prompt)
    image_path = os.path.join(IMAGE_DIR, f"{sanitized_prompt}.png")
    image.save(image_path)
    return image_path

def generate_pptx(request, ppt_content: List[Dict[str, List[str]]]) -> str:
    try:
        prs = Presentation()

        title_bg_color = RGBColor(0, 51, 102)  # Dark Blue
        content_bg_color = RGBColor(220, 230, 241)  # Light Blue
        text_color = RGBColor(255, 255, 255)  # White
        bullet_color = RGBColor(0, 0, 0)  # Black

        # Title Slide
        title_slide_layout = prs.slide_layouts[5]
        slide = prs.slides.add_slide(title_slide_layout)
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = title_bg_color

        title_shape = slide.shapes.title
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
            slide_layout = prs.slide_layouts[5]
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

            # Add text bullets
            for bullet in slide_data["content"]:
                bullet = bullet.strip()
                if bullet:
                    p = text_frame.add_paragraph()
                    p.text = bullet
                    p.font.size = Pt(24)
                    p.font.color.rgb = bullet_color
                    p.level = 0

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

        # Add transitions using PowerPoint automation
        add_transitions(file_path)

        return file_path

    except PermissionError:
        raise OSError(f"Permission denied when saving file to {file_path}")
    except Exception as e:
        raise Exception(f"Failed to generate presentation: {str(e)}")

def add_transitions(pptx_path):
    """Adds slide transitions using PowerPoint automation (Windows only)."""
    ppt_app = comtypes.client.CreateObject("PowerPoint.Application")
    ppt_app.Visible = True
    presentation = ppt_app.Presentations.Open(pptx_path)

    for slide in presentation.Slides:
        slide.SlideShowTransition.EntryEffect = 2  # 2 = Fade transition
        slide.SlideShowTransition.Duration = 2  # 2-second transition duration
        slide.SlideShowTransition.AdvanceOnTime = True
        slide.SlideShowTransition.AdvanceTime = 5  # Each slide lasts 5 seconds

    presentation.Save()
    presentation.Close()
    ppt_app.Quit()
