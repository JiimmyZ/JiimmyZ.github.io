# Donation QR Code Images

This directory is for storing QR code images for the donation feature.

## Required Files

### Required
- `qr-bank.png` - Bank transfer QR code (currently enabled in config)

### Optional (can be enabled in `hugo.toml`)
- `qr-linepay.png` - Line Pay QR code
- `qr-jkopay.png` - JKO Pay (街口支付) QR code

## How to Generate QR Codes

1. **Bank Transfer QR Code**:
   - Use your bank's mobile app to generate a transfer QR code
   - Or use online QR code generators with your bank account information
   - Save as PNG format
   - Recommended size: 300x300px or larger (will be scaled down automatically)

2. **Line Pay QR Code**:
   - Generate from Line Pay app
   - Save as PNG format

3. **JKO Pay QR Code**:
   - Generate from 街口支付 app
   - Save as PNG format

## File Naming

Make sure the file names match exactly:
- `qr-bank.png`
- `qr-linepay.png`
- `qr-jkopay.png`

## Notes

- Images will be automatically scaled to fit the display area (max-width: 300px)
- Supported formats: PNG, JPG, WebP
- For best quality, use PNG format with transparent background (if applicable)
