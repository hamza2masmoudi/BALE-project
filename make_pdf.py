from reportlab.pdfgen import canvas
def create_pdf(path):
c = canvas.Canvas(path)
c.drawString(100, 750, "COMMERCIAL CONTRACT")
c.drawString(100, 700, "1. JURISDICTION")
c.drawString(100, 680, "This agreement shall be governed by the laws of England and Wales.")
c.save()
if __name__ == "__main__":
create_pdf("dummy_contract.pdf")
