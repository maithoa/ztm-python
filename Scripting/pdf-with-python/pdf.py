import pypdf

with open("test-files/sample.pdf", "rb") as f:
    reader = pypdf.PdfReader(f)
    page = reader.get_page(0)
    page.rotate(90)
    with open ("test-files/sample_rotated.pdf", "wb") as out_f:
        writer = pypdf.PdfWriter()
        writer.add_page(page)
        writer.write(out_f)


