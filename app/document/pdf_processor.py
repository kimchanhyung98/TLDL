import base64
import json
from pathlib import Path
from typing import List, Dict, Any

import PyPDF2
import requests
from PIL import Image
from openai import OpenAI
from pdf2image import convert_from_path

from app.config import OPENAI_API_KEY, SUMMARY_MODEL


class PDFProcessor:
    """Class for processing PDF files"""

    def __init__(self, api_key=OPENAI_API_KEY):
        self.client = OpenAI(api_key=api_key)
        self.summary_model = SUMMARY_MODEL

    def process_pdf(self, pdf_path: str, output_dir: Path) -> Dict[str, Any]:
        """Process a PDF file and extract text, images, and analysis
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Base output directory
            
        Returns:
            Dict containing processing results
        """
        pdf_path = Path(pdf_path)
        file_name = pdf_path.stem

        # Create output directory for this PDF
        pdf_output_dir = output_dir / f"pdf-{file_name}"
        pdf_output_dir.mkdir(parents=True, exist_ok=True)

        # Create images directory
        images_dir = pdf_output_dir / "images"
        images_dir.mkdir(exist_ok=True)

        # Create analysis directory
        analysis_dir = pdf_output_dir / "analysis"
        analysis_dir.mkdir(exist_ok=True)

        # 1. Extract text from PDF
        text_content = self.extract_text(pdf_path)
        text_file = pdf_output_dir / "text_content.txt"
        with open(text_file, "w", encoding="utf-8") as f:
            f.write(text_content)

        # 2. Convert PDF to images and save
        images = self.convert_to_images(pdf_path)
        image_paths = []

        for i, image in enumerate(images):
            image_path = images_dir / f"page_{i + 1}.png"
            image.save(image_path, "PNG")
            image_paths.append(image_path)

        # 3. Analyze images with GPT Vision
        page_analyses = []

        for i, image_path in enumerate(image_paths):
            # Analyze image
            analysis = self.analyze_image(image_path)

            # Save analysis
            analysis_file = analysis_dir / f"page_{i + 1}_analysis.txt"
            with open(analysis_file, "w", encoding="utf-8") as f:
                f.write(analysis)

            page_analyses.append({
                "page": i + 1,
                "analysis": analysis
            })

        # 4. Extract important content and summarize
        important_content = self.extract_important_content(text_content, page_analyses)
        important_file = pdf_output_dir / "important_content.txt"
        with open(important_file, "w", encoding="utf-8") as f:
            f.write(important_content)

        summary = self.summarize_content(text_content, page_analyses)
        summary_file = pdf_output_dir / "summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        # Save metadata
        metadata = {
            "file_name": file_name,
            "page_count": len(images),
            "has_text": bool(text_content.strip()),
            "pages": [{"page": item["page"], "has_analysis": bool(item["analysis"])} for item in page_analyses]
        }

        metadata_file = pdf_output_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "file_name": file_name,
            "output_dir": pdf_output_dir,
            "text_file": text_file,
            "image_paths": image_paths,
            "analysis_files": [analysis_dir / f"page_{i + 1}_analysis.txt" for i in range(len(images))],
            "important_file": important_file,
            "summary_file": summary_file,
            "metadata": metadata
        }

    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        text_content = ""

        try:
            with open(pdf_path, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    text_content += f"--- Page {page_num + 1} ---\n"
                    text_content += page.extract_text() or "[No extractable text on this page]"
                    text_content += "\n\n"
        except Exception as e:
            text_content = f"Error extracting text: {str(e)}"

        return text_content

    def convert_to_images(self, pdf_path: Path) -> List[Image.Image]:
        """Convert PDF to a list of images
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            List of PIL Image objects
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=200)
            return images
        except Exception as e:
            print(f"Error converting PDF to images: {str(e)}")
            return []

    def analyze_image(self, image_path: Path) -> str:
        """Analyze an image using GPT-4 Vision
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Analysis text
        """
        try:
            # Read image and encode as base64
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')

            # Call GPT-4 Vision API
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this lecture slide or page. Identify and explain key concepts, formulas, diagrams, and their significance. If there are any important points that would be relevant for exams or assignments, highlight them."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )

            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def extract_important_content(self, text_content: str, page_analyses: List[Dict]) -> str:
        """Extract important content from text and page analyses
        
        Args:
            text_content: Extracted text content
            page_analyses: List of page analysis results
            
        Returns:
            Important content
        """
        # Combine text content with page analyses
        combined_content = text_content + "\n\n"
        for page in page_analyses:
            combined_content += f"--- Page {page['page']} Analysis ---\n"
            combined_content += page['analysis'] + "\n\n"

        # Use OpenAI to extract important content
        prompt = f"""
        The following is content extracted from a lecture PDF, including both text and analysis of visual elements.
        Please identify and extract the most important content, focusing on:
        
        1. Key concepts and definitions
        2. Important formulas and equations
        3. Critical information for exams or assignments
        4. Significant diagrams or visual elements and their meaning
        
        Content:
        {combined_content[:25000]}  # Limit content length to avoid token limits
        """

        response = self.client.chat.completions.create(
            model=self.summary_model,
            messages=[
                {"role": "system",
                 "content": "You are an expert academic assistant that helps students identify the most important information from lecture materials."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content

    def summarize_content(self, text_content: str, page_analyses: List[Dict]) -> str:
        """Summarize content from text and page analyses
        
        Args:
            text_content: Extracted text content
            page_analyses: List of page analysis results
            
        Returns:
            Summary of content
        """
        # Combine text content with page analyses
        combined_content = text_content + "\n\n"
        for page in page_analyses:
            combined_content += f"--- Page {page['page']} Analysis ---\n"
            combined_content += page['analysis'] + "\n\n"

        # Use OpenAI to summarize content
        prompt = f"""
        The following is content extracted from a lecture PDF, including both text and analysis of visual elements.
        Please provide a comprehensive summary that:
        
        1. Outlines the main topics and concepts covered
        2. Explains key ideas in a clear, structured manner
        3. Preserves the logical flow of the lecture material
        4. Includes important formulas, diagrams, and their significance
        
        Content:
        {combined_content[:25000]}  # Limit content length to avoid token limits
        """

        response = self.client.chat.completions.create(
            model=self.summary_model,
            messages=[
                {"role": "system",
                 "content": "You are an expert academic assistant that helps students understand complex lecture materials by providing clear, comprehensive summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
