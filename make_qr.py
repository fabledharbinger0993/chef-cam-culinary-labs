"""
Make the QR code that opens the web form.

    python3 make_qr.py                 # default GitHub Pages address
    python3 make_qr.py https://...     # any other address

Writes web/qr.png (printable, and shown in the form's "More" menu).
Requires: pip install -r requirements.txt
"""

import sys

import qrcode

DEFAULT_URL = "https://fabledharbinger0993.github.io/chef-cam-culinary-labs/"

url = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_URL
qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=12, border=4)
qr.add_data(url)
qr.make(fit=True)
qr.make_image(fill_color="#153447", back_color="white").save("web/qr.png")
print("web/qr.png ->", url)
