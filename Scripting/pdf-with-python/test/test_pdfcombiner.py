import pytest
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import importlib.util
import pypdf

# Import pdf_combiner function from pdf-combiner.py (with dash in name)
pdf_combiner_path = Path(__file__).parent.parent / "pdf-combiner.py"
spec = importlib.util.spec_from_file_location("pdf_combiner_module", pdf_combiner_path)
pdf_combiner_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pdf_combiner_module)
pdf_combiner = pdf_combiner_module.pdf_combiner


class TestPdfCombiner:
    """Test suite for pdf_combiner function."""

    @pytest.fixture
    def test_files_dir(self):
        """Get the path to test files directory."""
        return Path(__file__).parent.parent / "test-files"

    @pytest.fixture
    def sample_pdfs(self, test_files_dir):
        """Get paths to sample PDF files."""
        return [
            str(test_files_dir / "sample.pdf"),
            str(test_files_dir / "sample-3-pages.pdf"),
        ]

    @pytest.fixture
    def temp_output_file(self):
        """Create a temporary file for output."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if Path(temp_path).exists():
            Path(temp_path).unlink()

    def test_pdf_combiner_with_valid_files(self, sample_pdfs, temp_output_file):
        """Test combining valid PDF files."""
        pdf_combiner(sample_pdfs, temp_output_file)
        # Verify the output file was created
        assert Path(temp_output_file).exists()

    def test_pdf_combiner_creates_valid_pdf(self, sample_pdfs, temp_output_file):
        """Test that the output is a valid PDF file."""
        pdf_combiner(sample_pdfs, temp_output_file)
        
        # Verify the output file is a valid PDF
        with open(temp_output_file, "rb") as f:
            assert f.read(4) == b"%PDF"  # PDF magic number

    def test_pdf_combiner_with_single_file(self, test_files_dir, temp_output_file):
        """Test combining a single PDF file."""
        single_pdf = [str(test_files_dir / "sample.pdf")]
        pdf_combiner(single_pdf, temp_output_file)
        assert Path(temp_output_file).exists()

    def test_pdf_combiner_with_empty_list(self, temp_output_file):
        """Test combining with an empty list of PDFs."""
        # This should create an empty PDF or handle gracefully
        with patch("pypdf.PdfWriter") as mock_merger:
            mock_instance = MagicMock()
            mock_merger.return_value = mock_instance
            
            pdf_combiner([], temp_output_file)
            
            # Verify write was called
            mock_instance.write.assert_called_once()

    def test_pdf_combiner_with_nonexistent_file(self, temp_output_file):
        """Test combining with non-existent PDF file."""
        nonexistent_pdfs = ["nonexistent_file.pdf"]
        
        with pytest.raises(FileNotFoundError):
            pdf_combiner(nonexistent_pdfs, temp_output_file)

    def test_pdf_combiner_output_location(self, sample_pdfs, temp_output_file):
        """Test that combined PDF is written to correct location."""
        pdf_combiner(sample_pdfs, temp_output_file)
        
        output_path = Path(temp_output_file)
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_pdf_combiner_file_size(self, sample_pdfs, temp_output_file):
        """Test that combined PDF has reasonable file size."""
        pdf_combiner(sample_pdfs, temp_output_file)
        
        output_path = Path(temp_output_file)
        # Check that the file size is reasonable (not empty)
        file_size = output_path.stat().st_size
        assert file_size > 100  # PDF files should be more than 100 bytes

    def test_pdf_combiner_with_rotated_pdf(self, test_files_dir, temp_output_file):
        """Test combining with a rotated PDF file."""
        pdfs = [
            str(test_files_dir / "sample.pdf"),
            str(test_files_dir / "sample_rotated.pdf"),
        ]
        pdf_combiner(pdfs, temp_output_file)
        assert Path(temp_output_file).exists()

    @patch("pypdf.PdfWriter.append")
    def test_pdf_combiner_calls_append_for_each_file(self, mock_append, sample_pdfs, temp_output_file):
        """Test that append is called for each PDF file."""
        with patch("pypdf.PdfWriter.write"):
            pdf_combiner(sample_pdfs, temp_output_file)
            
            # append should be called for each file
            assert mock_append.call_count == len(sample_pdfs)

    @patch("pypdf.PdfWriter.write")
    def test_pdf_combiner_calls_write(self, mock_write, sample_pdfs, temp_output_file):
        """Test that write is called to save the combined PDF."""
        with patch("pypdf.PdfWriter.append"):
            pdf_combiner(sample_pdfs, temp_output_file)
            
            # write should be called once
            mock_write.assert_called_once()

    def test_pdf_combiner_multiple_combinations(self, sample_pdfs, temp_output_file):
        """Test running pdf_combiner multiple times produces valid output each time."""
        for _ in range(2):
            pdf_combiner(sample_pdfs, temp_output_file)
            assert Path(temp_output_file).exists()


class TestPdfCombinerIntegration:
    """Integration tests for pdf_combiner with actual PDF files."""

    @pytest.fixture
    def test_files_dir(self):
        """Get the path to test files directory."""
        return Path(__file__).parent.parent / "test-files"

    @pytest.fixture
    def temp_output_file(self):
        """Create a temporary file for output."""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_path = f.name
        yield temp_path
        # Cleanup
        if Path(temp_path).exists():
            Path(temp_path).unlink()

    def test_combined_pdf_readable(self, test_files_dir, temp_output_file):
        """Test that the combined PDF can be read by pypdf."""
        pdfs = [
            str(test_files_dir / "sample.pdf"),
            str(test_files_dir / "sample-3-pages.pdf"),
        ]
        pdf_combiner(pdfs, temp_output_file)
        
        # Try reading the combined PDF
        with open(temp_output_file, "rb") as f:
            reader = pypdf.PdfReader(f)
            # Should have pages from both PDFs
            assert len(reader.pages) > 0

    def test_combined_pdf_has_content_from_all_inputs(self, test_files_dir, temp_output_file):
        """Test that combined PDF contains content from all input PDFs."""
        pdfs = [
            str(test_files_dir / "sample.pdf"),
            str(test_files_dir / "sample-3-pages.pdf"),
        ]
        pdf_combiner(pdfs, temp_output_file)
        
        # Get page counts from individual PDFs
        page_counts = []
        for pdf_path in pdfs:
            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                page_counts.append(len(reader.pages))
        
        # Check combined PDF has all pages
        with open(temp_output_file, "rb") as f:
            reader = pypdf.PdfReader(f)
            combined_page_count = len(reader.pages)
            # Total pages should be sum of input pages
            assert combined_page_count == sum(page_counts)

