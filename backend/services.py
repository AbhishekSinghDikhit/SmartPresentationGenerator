from pptx import Presentation
from pptx.util import Inches, Pt
import os
from typing import List, Dict

class PresentationRequest:
    def __init__(self, title: str, author: str, num_slides: int):
        self.title = title
        self.author = author
        self.num_slides = num_slides

def generate_pptx(request: PresentationRequest, ppt_content: List[Dict[str, List[str]]]) -> str:
    """
    Generate a PowerPoint presentation based on request and content data.
    
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
        
        # Title Slide
        title_slide_layout = prs.slide_layouts[0]  # Title slide layout
        slide = prs.slides.add_slide(title_slide_layout)
        title = slide.shapes.title
        subtitle = slide.placeholders[1] if len(slide.placeholders) > 1 else None

        title.text = request.title.strip()
        title.text_frame.text = request.title.strip()
        title.text_frame.paragraphs[0].font.size = Pt(44)  # Increase font size

        if subtitle:
            subtitle.text = f"By {request.author.strip()}"
            subtitle.text_frame.paragraphs[0].font.size = Pt(28)

        # Content Slides
        available_slides = min(len(ppt_content), request.num_slides)
        if available_slides < request.num_slides:
            print(f"Warning: Requested {request.num_slides} slides but only {available_slides} available")

        for slide_data in ppt_content[:available_slides]:
            if not isinstance(slide_data, dict) or "title" not in slide_data or "content" not in slide_data:
                print("Warning: Skipping invalid slide data")
                continue

            slide_layout = prs.slide_layouts[1]  # Title & Content layout
            slide = prs.slides.add_slide(slide_layout)
            slide_title = slide.shapes.title
            content_box = slide.placeholders[1] if len(slide.placeholders) > 1 else None

            slide_title.text = str(slide_data["title"]).strip()
            slide_title.text_frame.paragraphs[0].font.size = Pt(36)  # Bigger font for title

            if content_box and slide_data["content"]:
                text_frame = content_box.text_frame
                text_frame.clear()  # Clear any default text

                for bullet in slide_data["content"]:
                    bullet = str(bullet).strip()
                    if bullet:
                        p = text_frame.add_paragraph()
                        p.text = bullet
                        p.font.size = Pt(24)  # Increase bullet point font size
                        p.level = 0  # Bullet point level

        # Add "Thank You" Slide
        thank_you_slide = prs.slides.add_slide(prs.slide_layouts[5])  # Title Only Layout
        thank_you_title = thank_you_slide.shapes.title
        thank_you_title.text = "Thank You!"
        thank_you_title.text_frame.paragraphs[0].font.size = Pt(44)  # Make it large

        # Save the presentation
        file_name = f"{request.title.strip().replace(' ', '_')}.pptx"
        file_path = os.path.join(os.getcwd(), file_name)

        prs.save(file_path)
        return file_path

    except PermissionError:
        raise OSError(f"Permission denied when saving file to {file_path}")
    except Exception as e:
        raise Exception(f"Failed to generate presentation: {str(e)}")
