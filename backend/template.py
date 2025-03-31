from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import os

TEMPLATE_DIR = "templates"
os.makedirs(TEMPLATE_DIR, exist_ok=True)

def create_template(template_name: str, title_color=RGBColor(255, 255, 255), bg_color=RGBColor(0, 51, 102)):
    """Creates a PowerPoint template and saves it in the templates folder."""
    prs = Presentation()
    prs.slide_width = Inches(13.33)
    prs.slide_height = Inches(7.5)

    # Title Slide
    slide_layout = prs.slide_layouts[5]
    slide = prs.slides.add_slide(slide_layout)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = bg_color

    title_shape = slide.shapes.title
    title_shape.text = "Presentation Title"
    title_shape.text_frame.paragraphs[0].font.size = Pt(44)
    title_shape.text_frame.paragraphs[0].font.bold = True
    title_shape.text_frame.paragraphs[0].font.color.rgb = title_color

    author_shape = slide.shapes.add_textbox(Inches(3), Inches(3), Inches(5), Inches(1))
    author_frame = author_shape.text_frame
    author_frame.text = "By Author Name"
    author_frame.paragraphs[0].font.size = Pt(28)
    author_frame.paragraphs[0].font.color.rgb = title_color

    # Save Template
    file_path = os.path.join(TEMPLATE_DIR, f"{template_name}.pptx")
    prs.save(file_path)
    print(f"✅ Template saved: {file_path}")

# Create two different templates
create_template("modern_minimalist", title_color=RGBColor(255, 255, 255), bg_color=RGBColor(0, 51, 102))
create_template("corporate_professional", title_color=RGBColor(0, 0, 0), bg_color=RGBColor(200, 200, 200))
