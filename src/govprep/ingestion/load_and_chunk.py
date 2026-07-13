from pypdf import PdfReader

def load_pdf(filepath):
    """
    Load text from a PDF file.
    """
    reader = PdfReader(filepath)
    text = ""
    for page_num, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks


if __name__ == "__main__":
    pdf_path = "../data/ncert_history_ch01.pdf"
    print("Loading PDF...\n")
    text = load_pdf(pdf_path)
    print(f"Loaded {len(text)} characters from PDF")
    print(f"First 500 chars:\n{text[:500]}")
    print("\n" + "="*60 + "\n")
    # Chunk it
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    print(f"Created {len(chunks)} chunks")
    print(f"\nFirst chunk:\n{chunks[0]}")
    print(f"\nSecond chunk:\n{chunks[1]}")
    print(f"\nThird chunk:\n{chunks[2]}")
