from fpdf import FPDF
import os
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'test_suite')
os.makedirs(DATA_DIR, exist_ok=True)
class LegalPDF(FPDF):
def header(self):
self.set_font('Arial', 'B', 12)
self.cell(0, 10, 'CONFIDENTIAL LEGAL AGREEMENT', 0, 1, 'C')
self.ln(10)
def create_conflict_pdf():
pdf = LegalPDF()
pdf.add_page()
pdf.set_font("Arial", size=11)
text = """
AGREEMENT ON TEXTILE SUPPLY
Section 12: Termination and Force Majeure
12.1 The Supplier may terminate this Agreement immediately upon any "Force Majeure" event.
12.2 "Force Majeure" shall mean any event beyond reasonable control, including but not limited to labor strikes, weather conditions, or simple economic hardship.
Article 1218 (Code Civil Applicable)
Il y a force majeure en matière contractuelle lorsqu'un événement échappant au contrôle du débiteur, qui ne pouvait être raisonnablement prévu lors de la conclusion du contrat et dont les effets ne peuvent être évités par des mesures appropriées, empêche l'exécution de son obligation par le débiteur.
(Note: Civil law requires unpredictability and irresistibility, whereas Section 12.2 includes 'simple economic hardship' which is typically REJECTED in French courts as Force Majeure.)
"""
pdf.multi_cell(0, 10, text)
filename = os.path.join(DATA_DIR, "contract_conflict.pdf")
pdf.output(filename)
print(f"Generated: {filename}")
def create_harmonized_pdf():
pdf = LegalPDF()
pdf.add_page()
pdf.set_font("Arial", size=11)
text = """
MUTUAL NON-DISCLOSURE AGREEMENT
Section 5: Term
5.1 This Agreement shall remain in effect for a period of 5 years.
Article L. 110-1 (Commercial Code Reference)
Les obligations nées à l'occasion de leur commerce entre commerçants ou entre commerçants et non-commerçants se prescrivent par cinq ans si elles ne sont pas soumises à des prescriptions plus courtes spéciales.
(Note: Both clauses align on a 5-year prescription/term period. No conflict.)
"""
pdf.multi_cell(0, 10, text)
filename = os.path.join(DATA_DIR, "contract_harmonized.pdf")
pdf.output(filename)
print(f"Generated: {filename}")
def create_complex_pdf():
pdf = LegalPDF()
pdf.add_page()
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 10, "COMPLEX MULTI-JURISDICTIONAL CLAUSES\n\n")
for i in range(1, 4):
pdf.set_font("Arial", 'B', 11)
pdf.cell(0, 10, f"Clause {i}: Jurisdiction", 0, 1)
pdf.set_font("Arial", '', 11)
pdf.multi_cell(0, 10, "This agreement shall be governed by the laws of England and Wales.\n")
pdf.ln(5)
pdf.set_font("Arial", 'B', 11)
pdf.cell(0, 10, f"Article {100+i} (Code de Commerce)", 0, 1)
pdf.set_font("Arial", '', 11)
pdf.multi_cell(0, 10, "Toute clause attributive de juridiction est réputée non écrite si elle n'a pas été convenue entre des commerçants.\n")
pdf.ln(5)
filename = os.path.join(DATA_DIR, "contract_complex.pdf")
pdf.output(filename)
print(f"Generated: {filename}")
if __name__ == "__main__":
create_conflict_pdf()
create_harmonized_pdf()
create_complex_pdf()
