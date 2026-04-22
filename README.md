🔐 PixelPrison – Secure Image Message Hider

PixelPrison is a Python-based desktop application that lets you securely hide and extract secret messages inside images using LSB (Least Significant Bit) steganography. It features a clean GUI, message integrity verification, and safeguards against data loss from compressed formats.

✨ Features
🖼️ Hide secret messages inside images
🔍 Extract hidden messages
🔐 MD5 integrity check to detect corruption
⚠️ Automatic JPG → PNG conversion with warning
👁️ Image preview before processing
📏 Message size validation based on image capacity
💻 Simple and intuitive Tkinter GUI

🛠️ Tech Stack
Python
OpenCV (cv2)
NumPy
Tkinter (GUI)
Pillow (image preview)
hashlib (MD5 verification)

⚙️ How It Works
Select an image (PNG/BMP recommended)
Enter a secret message
The app encodes the message into pixel data using LSB
A checksum is added for integrity verification
Save the encoded image
To extract:
Load an encoded image
The app decodes and verifies the message automatically

🚀 Getting Started
1. Install dependencies
pip install opencv-python numpy pillow
2. Run the app
python app.py
📁 Supported Formats
✅ PNG (recommended)
✅ BMP / TIFF
⚠️ JPG (converted automatically, may reduce reliability)

⚠️ Important Notes
Avoid saving encoded images as JPG (lossy compression corrupts data)
Do not edit images after embedding a message
Message size depends on image resolution
💡 Future Improvements
🔑 Password-based encryption for messages
📦 Drag & drop support
🌙 Dark mode UI
📱 Cross-platform packaging (EXE / AppImage)

📌 Use Cases
Secure communication
Digital watermarking
Educational purposes (learning steganography)
📄 License

MIT License
