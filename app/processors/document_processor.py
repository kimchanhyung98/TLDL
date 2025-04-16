import re
from pathlib import Path
from typing import List, Dict, Any

from app.services.document.pdf_processor import PDFProcessor
from app.services.image.image_analyzer import ImageAnalyzer
from app.utils.integrator import ContentIntegrator


class DocumentProcessor:
    """Main class for processing documents (PDFs and images)"""

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.pdf_processor = PDFProcessor()
        self.image_analyzer = ImageAnalyzer()
        self.integrator = ContentIntegrator()

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file (PDF or image)
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dict containing processing results
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Determine file type
        if file_path.suffix.lower() in ['.pdf']:
            return self.process_pdf(file_path)
        elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            return self.process_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

    def process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict containing processing results
        """
        return self.pdf_processor.process_pdf(pdf_path, self.output_dir)

    def process_image(self, image_path: str) -> Dict[str, Any]:
        """Process an image file
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dict containing processing results
        """
        return self.image_analyzer.process_image(image_path, self.output_dir)

    def consolidate_pdf_content(self, pdf_name: str) -> Dict[str, Any]:
        """Consolidate content from a processed PDF
        
        Args:
            pdf_name: Name of the PDF (without extension)
            
        Returns:
            Dict containing consolidation results
        """
        pdf_dir = self.output_dir / f"pdf-{pdf_name}"

        if not pdf_dir.exists():
            raise FileNotFoundError(f"PDF directory not found: {pdf_dir}")

        return self.integrator.process_pdf_directory(pdf_dir, self.output_dir)

    def consolidate_lecture_content(self, lecture_name: str) -> Dict[str, Any]:
        """Consolidate content from lecture images
        
        Args:
            lecture_name: Lecture name (prefix of image files)
            
        Returns:
            Dict containing consolidation results
        """
        return self.integrator.process_lecture_images(lecture_name, self.output_dir, self.output_dir)

    def process_all_files(self, directory: str = "data") -> List[Dict[str, Any]]:
        """Process all files in a directory
        
        Args:
            directory: Directory containing files to process
            
        Returns:
            List of processing results
        """
        directory = Path(directory)

        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        results = []

        # Process all PDF files
        for pdf_file in directory.glob("*.pdf"):
            try:
                result = self.process_pdf(pdf_file)
                results.append(result)
                print(f"Processed PDF: {pdf_file.name}")
            except Exception as e:
                print(f"Error processing PDF {pdf_file.name}: {str(e)}")

        # Process all image files
        for ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
            for image_file in directory.glob(f"*{ext}"):
                try:
                    result = self.process_image(image_file)
                    results.append(result)
                    print(f"Processed image: {image_file.name}")
                except Exception as e:
                    print(f"Error processing image {image_file.name}: {str(e)}")

        # Consolidate PDF content
        pdf_dirs = [d for d in self.output_dir.iterdir() if d.is_dir() and d.name.startswith("pdf-")]
        for pdf_dir in pdf_dirs:
            try:
                pdf_name = pdf_dir.name[4:]  # Remove 'pdf-' prefix
                result = self.consolidate_pdf_content(pdf_name)
                results.append(result)
                print(f"Consolidated PDF content: {pdf_name}")
            except Exception as e:
                print(f"Error consolidating PDF content {pdf_dir.name}: {str(e)}")

        # Consolidate lecture content
        # Find all lecture prefixes
        lecture_prefixes = set()
        lecture_pattern = re.compile(r"(.+)-\d+")

        for item in self.output_dir.iterdir():
            if item.is_dir():
                match = lecture_pattern.match(item.name)
                if match:
                    lecture_prefixes.add(match.group(1))

        for lecture_name in lecture_prefixes:
            try:
                result = self.consolidate_lecture_content(lecture_name)
                results.append(result)
                print(f"Consolidated lecture content: {lecture_name}")
            except Exception as e:
                print(f"Error consolidating lecture content {lecture_name}: {str(e)}")

        return results
