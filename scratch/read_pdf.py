import pypdf

reader = pypdf.PdfReader("PANTALLAS DEL PROYECTO  VFINAL.pdf")
print("Number of pages:", len(reader.pages))

text_out = []
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    text_out.append(f"--- PAGE {i+1} ---")
    text_out.append(text)

with open("scratch/pdf_text.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(text_out))

print("Successfully written to scratch/pdf_text.txt")
