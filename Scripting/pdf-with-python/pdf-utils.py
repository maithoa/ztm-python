from copy import copy
from pathlib import Path

import pypdf


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

    # Merge files
    merger = pypdf.PdfWriter()
    for pdf_file in pdf_files_list:
        merger.append(pdf_file)

    # Create output directory if it doesn't exist
    output_file_path = Path(output_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Write merged file out using context manager (best practice)
    with open(output_path, "wb") as output_file:
        merger.write(output_file)

def add_watermark(input_pdf, watermark_pdf, output_pdf):
    """
    Add a watermark to each page of the input PDF.
    
    Args:
        input_pdf: Path to the input PDF file
        watermark_pdf: Path to the watermark PDF file
        output_pdf: Path where the watermarked PDF should be saved
        
    Raises:
        FileNotFoundError: If input PDF or watermark PDF do not exist
    """
    # Validate that input files exist
    input_path = Path(input_pdf)
    watermark_path = Path(watermark_pdf)
    
    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF file not found: {input_pdf}")
    if not watermark_path.exists():
        raise FileNotFoundError(f"Watermark PDF file not found: {watermark_pdf}")
    
    input_reader = pypdf.PdfReader(input_pdf)
    watermark_reader = pypdf.PdfReader(watermark_pdf)

    # Create watermarked pages
    writer = pypdf.PdfWriter()
    for page in input_reader.pages:
        # Create a copy of watermark for each page to avoid mutation
        watermark_copy = copy(watermark_reader.pages[0])
        # Merge page ON TOP watermark so watermark appears at bottom due to the water mark page is not transparent
        watermark_copy.merge_page(page)
        # Add merged page to the output filestream
        writer.add_page(watermark_copy)

    output_file_path = Path(output_pdf)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_pdf, "wb") as f:
        writer.write(f)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="PDF utilities for combining and watermarking PDFs")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Subcommand for combine
    combine_parser = subparsers.add_parser("combine", help="Combine multiple PDFs into one")
    combine_parser.add_argument("files", nargs="+", help="PDF files to combine")
    combine_parser.add_argument("-o", "--output", default="test-files/combined.pdf", 
                                help="Output file path (default: test-files/combined.pdf)")
    
    # Subcommand for watermark
    watermark_parser = subparsers.add_parser("watermark", help="Add watermark to a PDF")
    watermark_parser.add_argument("input", help="Input PDF file")
    watermark_parser.add_argument("watermark", help="Watermark PDF file")
    watermark_parser.add_argument("-o", "--output", required=True, help="Output file path")
    
    args = parser.parse_args()
    
    if args.command == "combine":
        pdf_combiner(args.files, args.output)
        print(f"✓ Combined PDFs saved to {args.output}")
    elif args.command == "watermark":
        add_watermark(args.input, args.watermark, args.output)
        print(f"✓ Watermarked PDF saved to {args.output}")
    else:
        parser.print_help()