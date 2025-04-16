import base64
import json
from pathlib import Path
from typing import Dict, Any

from openai import OpenAI

from app.config import OPENAI_API_KEY, SUMMARY_MODEL


class ImageAnalyzer:
    """Class for analyzing image files"""

    def __init__(self, api_key=OPENAI_API_KEY):
        self.client = OpenAI(api_key=api_key)
        self.summary_model = SUMMARY_MODEL

    def process_image(self, image_path: str, output_dir: Path) -> Dict[str, Any]:
        """Process an image file and generate analysis
        
        Args:
            image_path: Path to the image file
            output_dir: Base output directory
            
        Returns:
            Dict containing processing results
        """
        image_path = Path(image_path)
        file_name = image_path.stem

        # Create output directory for this image
        image_output_dir = output_dir / file_name
        image_output_dir.mkdir(parents=True, exist_ok=True)

        # 1. Analyze image with GPT Vision
        analysis = self.analyze_image(image_path)
        analysis_file = image_output_dir / "analysis.txt"
        with open(analysis_file, "w", encoding="utf-8") as f:
            f.write(analysis)

        # 2. Extract important content
        important_content = self.extract_important_content(analysis)
        important_file = image_output_dir / "important_content.txt"
        with open(important_file, "w", encoding="utf-8") as f:
            f.write(important_content)

        # 3. Summarize content
        summary = self.summarize_content(analysis)
        summary_file = image_output_dir / "summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary)

        # Save metadata
        metadata = {
            "file_name": file_name,
            "file_path": str(image_path),
            "has_analysis": bool(analysis.strip())
        }

        metadata_file = image_output_dir / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return {
            "file_name": file_name,
            "output_dir": image_output_dir,
            "analysis_file": analysis_file,
            "important_file": important_file,
            "summary_file": summary_file,
            "metadata": metadata
        }

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
                                "text": "Analyze this lecture slide or image. Identify and explain key concepts, formulas, diagrams, and their significance. If there are any important points that would be relevant for exams or assignments, highlight them."
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

    def extract_important_content(self, analysis: str) -> str:
        """Extract important content from image analysis
        
        Args:
            analysis: Image analysis text
            
        Returns:
            Important content
        """
        prompt = f"""
        The following is an analysis of a lecture slide or image.
        Please identify and extract the most important content, focusing on:
        
        1. Key concepts and definitions
        2. Important formulas and equations
        3. Critical information for exams or assignments
        4. Significant diagrams or visual elements and their meaning
        
        Analysis:
        {analysis}
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

    def summarize_content(self, analysis: str) -> str:
        """Summarize content from image analysis
        
        Args:
            analysis: Image analysis text
            
        Returns:
            Summary of content
        """
        prompt = f"""
        The following is an analysis of a lecture slide or image.
        Please provide a concise summary that captures the main points and significance of this content.
        
        Analysis:
        {analysis}
        """

        response = self.client.chat.completions.create(
            model=self.summary_model,
            messages=[
                {"role": "system",
                 "content": "You are an expert academic assistant that helps students understand complex lecture materials by providing clear, concise summaries."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
