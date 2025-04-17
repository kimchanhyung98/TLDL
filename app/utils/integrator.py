import re
from openai import OpenAI
from pathlib import Path
from typing import Dict, Any

from app.config import OPENAI_API_KEY, SUMMARY_MODEL


class ContentIntegrator:
    """Class for integrating and consolidating content from multiple sources"""

    def __init__(self, api_key=OPENAI_API_KEY):
        self.client = OpenAI(api_key=api_key)
        self.summary_model = SUMMARY_MODEL

    def process_pdf_directory(self, directory_path: Path, output_dir: Path) -> Dict[str, Any]:
        """Process a PDF directory and consolidate important content
        
        Args:
            directory_path: Path to the PDF directory (pdf-*)
            output_dir: Output directory for consolidated content
            
        Returns:
            Dict containing processing results
        """
        directory_path = Path(directory_path)

        # Check if this is a PDF directory
        if not directory_path.name.startswith("pdf-"):
            raise ValueError(f"Not a PDF directory: {directory_path}")

        file_name = directory_path.name[4:]  # Remove 'pdf-' prefix

        # Collect important content from all pages
        important_file = directory_path / "important_content.txt"
        if not important_file.exists():
            # Try to find important content in analysis directory
            important_contents = []
            analysis_dir = directory_path / "analysis"
            if analysis_dir.exists():
                for analysis_file in sorted(analysis_dir.glob("page_*_analysis.txt")):
                    with open(analysis_file, "r", encoding="utf-8") as f:
                        important_contents.append(f"--- From {analysis_file.name} ---\n{f.read()}")

            if not important_contents:
                raise ValueError(f"No important content found in {directory_path}")

            combined_important = "\n\n".join(important_contents)
        else:
            with open(important_file, "r", encoding="utf-8") as f:
                combined_important = f.read()

        # Consolidate important content
        consolidated_important = self.consolidate_important_content(combined_important, file_name)

        # Save as markdown
        markdown_file = output_dir / f"{file_name}.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(f"# {file_name} - Important Content\n\n")
            f.write(consolidated_important)

        return {
            "file_name": file_name,
            "markdown_file": markdown_file,
            "content": consolidated_important
        }

    def process_lecture_images(self, lecture_name: str, output_dir: Path, base_dir: Path) -> Dict[str, Any]:
        """Process lecture images and consolidate important content
        
        Args:
            lecture_name: Lecture name (prefix of image files)
            output_dir: Output directory for consolidated content
            base_dir: Base directory containing image directories
            
        Returns:
            Dict containing processing results
        """
        # Find all directories for this lecture
        lecture_pattern = re.compile(f"{re.escape(lecture_name)}-\\d+")
        lecture_dirs = []

        for item in base_dir.iterdir():
            if item.is_dir() and lecture_pattern.match(item.name):
                lecture_dirs.append(item)

        if not lecture_dirs:
            raise ValueError(f"No directories found for lecture: {lecture_name}")

        # Sort directories by page number
        lecture_dirs.sort(key=lambda d: int(d.name.split('-')[-1]))

        # Collect important content from all pages
        important_contents = []

        for dir_path in lecture_dirs:
            important_file = dir_path / "important_content.txt"
            if important_file.exists():
                with open(important_file, "r", encoding="utf-8") as f:
                    important_contents.append(f"--- From {dir_path.name} ---\n{f.read()}")
            else:
                # Try to use analysis file instead
                analysis_file = dir_path / "analysis.txt"
                if analysis_file.exists():
                    with open(analysis_file, "r", encoding="utf-8") as f:
                        important_contents.append(f"--- From {dir_path.name} ---\n{f.read()}")

        if not important_contents:
            raise ValueError(f"No important content found for lecture: {lecture_name}")

        combined_important = "\n\n".join(important_contents)

        # Consolidate important content
        consolidated_important = self.consolidate_important_content(combined_important, lecture_name)

        # Save as markdown
        markdown_file = output_dir / f"{lecture_name}.md"
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write(f"# {lecture_name} - Important Content\n\n")
            f.write(consolidated_important)

        return {
            "lecture_name": lecture_name,
            "markdown_file": markdown_file,
            "content": consolidated_important
        }

    def consolidate_important_content(self, content: str, title: str) -> str:
        """Consolidate important content from multiple pages
        
        Args:
            content: Combined important content from multiple pages
            title: Title or name of the content
            
        Returns:
            Consolidated important content in markdown format
        """
        prompt = f"""
        The following contains important content extracted from multiple pages of lecture material titled "{title}".
        Please consolidate this into a well-structured, comprehensive document that:
        
        1. Organizes information by topic rather than by page
        2. Eliminates redundancy while preserving all important points
        3. Presents information in a logical, hierarchical structure
        4. Uses markdown formatting for better readability (headings, lists, etc.)
        5. Highlights key concepts, formulas, and exam-relevant information
        
        Content:
        {content[:25000]}  # Limit content length to avoid token limits
        """

        response = self.client.chat.completions.create(
            model=self.summary_model,
            messages=[
                {"role": "system",
                 "content": "You are an expert academic assistant that helps organize and structure lecture content in a clear, comprehensive manner using markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        return response.choices[0].message.content
