from PIL import Image, ImageDraw, ImageFont
import os

def create_dummy_image():
    # Create a white image
    img = Image.new('RGB', (800, 600), color='white')
    d = ImageDraw.Draw(img)

    # Attempt to load a default font, else use default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        header_font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    # Add some "Contract" text
    d.text((50, 50), "CONFIDENTIAL CONTRACT", fill='black', font=header_font)
    d.text((50, 120), "Date: November 20, 2025", fill='black', font=font)
    d.text((50, 160), "Parties: Acme Corp & Beta Ltd", fill='black', font=font)
    d.text((50, 220), "SECTION 1: PAYMENT TERMS", fill='black', font=header_font)
    d.text((50, 280), "1.1 The Payer agrees to pay $50,000 upon completion.", fill='black', font=font)
    d.text((50, 320), "1.2 Late fees of 5% apply after 30 days.", fill='black', font=font)
    d.text((50, 400), "[Signature Placeholder]", fill='blue', font=font)

    # Save it
    img.save('test_scan.png')
    print("✅ Created 'test_scan.png' successfully.")

if __name__ == "__main__":
    create_dummy_image()