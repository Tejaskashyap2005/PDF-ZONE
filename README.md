# PDF Tool

A simple web application to compress PDFs and convert PDFs to JPG images. Built with Flask and designed to work offline or online.

## Features

- **Compress PDF**: Reduce PDF file size using PyPDF2
- **Convert PDF to JPG**: Convert each page to separate JPG images (zipped download)
- **Drag & Drop**: Easy file upload with drag-and-drop support
- **Responsive Design**: Works on desktop and mobile devices
- **Auto-cleanup**: Temporary files are automatically deleted after processing

## Live Demo

🌐 **Try it online**: [Your Render URL will be here]

## Local Development

### Prerequisites

- Python 3.9+
- Poppler (required for pdf2image)
  - macOS: `brew install poppler`
  - Ubuntu/Debian: `sudo apt-get install poppler-utils`
  - Windows: Download from [poppler-windows](https://github.com/oschwartz10612/poppler-windows)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pdf-tool.git
   cd pdf-tool
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   - http://127.0.0.1:5000/

## Usage

1. **Upload PDF**: Drag and drop a PDF file or click "Choose File"
2. **Compress PDF**: Click "Compress PDF" to reduce file size
3. **Convert to JPG**: Click "Convert to JPG" to get images of each page
4. **Download**: Files will automatically download when processing is complete

## Technical Details

- **Backend**: Flask with PyPDF2 and pdf2image
- **Frontend**: HTML, CSS, JavaScript (no frameworks)
- **File Processing**: Temporary files are cleaned up automatically
- **Security**: File type validation, size limits (100MB max)
- **Deployment**: Dockerized for easy hosting

## Deployment

This app is designed to be deployed on platforms like:
- Render (recommended)
- Railway
- Fly.io
- DigitalOcean App Platform
- AWS/GCP/Azure

The included `Dockerfile` handles all dependencies including Poppler.

## File Structure

```
pdf_tool/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── static/
│   ├── css/
│   │   └── styles.css    # Styling
│   └── files/            # Temporary file storage
├── templates/
│   ├── index.html        # Main page
│   └── result.html       # Result page
└── uploads/              # Temporary upload storage
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use this project for personal or commercial purposes.

## Support

If you encounter any issues:
1. Check that Poppler is installed correctly
2. Ensure your PDF file is not corrupted
3. Try with a smaller PDF file first
4. Check the browser console for JavaScript errors

---

**Made with ❤️ using Flask and modern web technologies**