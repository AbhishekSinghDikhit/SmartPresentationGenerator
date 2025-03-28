from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os
from typing import List, Dict

class PresentationRequest:
    def __init__(self, title: str, author: str, num_slides: int):
        self.title = title
        self.author = author
        self.num_slides = num_slides

def generate_pptx(request: PresentationRequest, ppt_content: List[Dict[str, List[str]]]) -> str:
    """
    Generate a PowerPoint presentation with custom design and color.
    
    Args:
        request: PresentationRequest object with title, author, and number of slides
        ppt_content: List of dictionaries containing slide title and content
    
    Returns:
        str: Path to the generated presentation file
    """
    try:
        if not request.title or not request.author:
            raise ValueError("Title and author must not be empty")
        if not isinstance(request.num_slides, int) or request.num_slides < 1:
            raise ValueError("Number of slides must be a positive integer")
        if not ppt_content:
            raise ValueError("Presentation content cannot be empty")

        prs = Presentation()

        # Custom Colors
        title_bg_color = RGBColor(0, 51, 102)  # Dark Blue
        content_bg_color = RGBColor(220, 230, 241)  # Light Blue
        text_color = RGBColor(255, 255, 255)  # White
        bullet_color = RGBColor(0, 0, 0)  # Black

        # Title Slide
        title_slide_layout = prs.slide_layouts[5]  # Title Only layout
        slide = prs.slides.add_slide(title_slide_layout)
        title_shape = slide.shapes.title

        # Set background color
        slide_background = slide.background
        fill = slide_background.fill
        fill.solid()
        fill.fore_color.rgb = title_bg_color

        # Title formatting
        title_shape.text = request.title.strip()
        title_frame = title_shape.text_frame
        title_frame.paragraphs[0].font.size = Pt(44)
        title_frame.paragraphs[0].font.bold = True
        title_frame.paragraphs[0].font.color.rgb = text_color

        # Add author as subtitle
        author_shape = slide.shapes.add_textbox(Inches(3), Inches(3), Inches(5), Inches(1))
        author_frame = author_shape.text_frame
        author_frame.text = f"By {request.author.strip()}"
        author_frame.paragraphs[0].font.size = Pt(28)
        author_frame.paragraphs[0].font.color.rgb = text_color

        # Content Slides
        available_slides = min(len(ppt_content), request.num_slides)
        for slide_data in ppt_content[:available_slides]:
            if not isinstance(slide_data, dict) or "title" not in slide_data or "content" not in slide_data:
                print("Warning: Skipping invalid slide data")
                continue

            slide_layout = prs.slide_layouts[1]  # Title & Content layout
            slide = prs.slides.add_slide(slide_layout)
            slide_title = slide.shapes.title
            content_box = slide.placeholders[1] if len(slide.placeholders) > 1 else None

            # Set background color
            slide_background = slide.background
            fill = slide_background.fill
            fill.solid()
            fill.fore_color.rgb = content_bg_color

            # Title Formatting
            slide_title.text = slide_data["title"].strip()
            slide_title.text_frame.paragraphs[0].font.size = Pt(36)
            slide_title.text_frame.paragraphs[0].font.bold = True
            slide_title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)  # Dark Blue

            # Content Formatting
            if content_box and slide_data["content"]:
                text_frame = content_box.text_frame
                text_frame.clear()  # Clear default text

                for bullet in slide_data["content"]:
                    bullet = bullet.strip()
                    if bullet:
                        p = text_frame.add_paragraph()
                        p.text = bullet
                        p.font.size = Pt(24)
                        p.font.color.rgb = bullet_color  # Set bullet point color
                        p.level = 0  # Bullet point level

        # Add "Thank You" Slide
        thank_you_slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only Layout
        thank_you_title = thank_you_slide.shapes.title
        thank_you_title.text = "Thank You!"
        
        # Set background color
        slide_background = thank_you_slide.background
        fill = slide_background.fill
        fill.solid()
        fill.fore_color.rgb = title_bg_color

        # Format Thank You text
        thank_you_title.text_frame.paragraphs[0].font.size = Pt(44)
        thank_you_title.text_frame.paragraphs[0].font.bold = True
        thank_you_title.text_frame.paragraphs[0].font.color.rgb = text_color
        thank_you_title.text_frame.paragraphs[0].alignment = 1  # Center alignment

        # Save the presentation
        file_name = f"{request.title.strip().replace(' ', '_')}.pptx"
        file_path = os.path.join(os.getcwd(), file_name)

        prs.save(file_path)
        return file_path

    except PermissionError:
        raise OSError(f"Permission denied when saving file to {file_path}")
    except Exception as e:
        raise Exception(f"Failed to generate presentation: {str(e)}")
