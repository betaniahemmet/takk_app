import os

import qrcode
from fpdf import FPDF

from app.config import Config

assert Config.BASE_URL, "❌ BASE_URL is not set. Check your .env file."


def generate_qr_pdf(tracking_id, initials, location):

    os.makedirs("instance", exist_ok=True)

    base_url = Config.BASE_URL  # now pulled from shared config

    qr_data = (
        f"{base_url}/log?tracking_id={tracking_id}"
        f"&initials={initials}&location={location}"
    )

    qr = qrcode.make(qr_data)

    temp_path = os.path.join("instance", "qr_temp.png")
    qr.save(temp_path)

    pdf = FPDF("P", "mm", "A4")
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.image(temp_path, x=60, y=40, w=90)

    pdf.set_y(140)
    pdf.cell(0, 10, f"Tracking for: {initials} at {location}", ln=True, align="C")
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, "Discard this QR if information is outdated", ln=True, align="C")

    pdf_bytes = pdf.output(dest="S").encode("latin1")
    os.remove(temp_path)

    return pdf_bytes
