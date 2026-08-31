import pypdf
import sys
from pathlib import Path


def pdf_combiner(pdf_files_list, output_path="test-files/combined.pdf"):
    """
    Combine multiple PDF files into a single PDF.
    
    Args:
        pdf_files_list: List of paths to PDF files to combine
        output_path: Path where the combined PDF should be saved (default: test-files/combined.pdf)
        
    Raises:
        FileNotFoundError: If any of the input PDF files do not exist
    """
    # Validate that all input files exist
    for pdf_file in pdf_files_list:
        pdf_path = Path(pdf_file)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_file}")
    
    merger = pypdf.PdfWriter()
    for pdf_file in pdf_files_list:
        merger.append(pdf_file)

    # Create output directory if it doesn't exist
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    merger.write(output_path)


if __name__ == "__main__":
    inputs = sys.argv[1:]
    pdf_combiner(inputs)