import os
import io
import zipfile
import tempfile
from datetime import datetime
from typing import List

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import subprocess
import shutil

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
STATIC_FILES_FOLDER = os.path.join(BASE_DIR, 'static', 'files')
ALLOWED_EXTENSIONS = {'.pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FILES_FOLDER, exist_ok=True)

app = Flask(__name__)
app.secret_key = 'replace-this-with-a-random-secret'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB upload limit


def allowed_file(filename: str) -> bool:
	_, ext = os.path.splitext(filename.lower())
	return ext in ALLOWED_EXTENSIONS


def generate_timestamped_name(prefix: str, suffix: str) -> str:
	return f"{prefix}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S%f')}{suffix}"


def compress_pdf_pypdf2(input_path: str, output_path: str) -> None:
	reader = PdfReader(input_path)
	writer = PdfWriter()
	for page in reader.pages:
		writer.add_page(page)
	if reader.metadata:
		writer.add_metadata({k: v for k, v in reader.metadata.items() if isinstance(v, str)})
	with open(output_path, 'wb') as f_out:
		writer.write(f_out)


def compress_pdf_ghostscript(input_path: str, output_path: str, quality: int, dpi: int) -> bool:
	"""Use Ghostscript if available. Returns True if succeeded, else False."""
	gs_path = shutil.which('gs') or shutil.which('gswin64c') or shutil.which('gswin32c')
	if not gs_path:
		return False
	# Map quality to PDFSETTINGS
	# We derive a PDFSETTINGS level based on requested quality
	if quality >= 85:
		pdfsettings = '/printer'
	elif quality >= 70:
		pdfsettings = '/ebook'
	elif quality >= 55:
		pdfsettings = '/screen'
	else:
		pdfsettings = '/screen'

	cmd = [
		gs_path,
		'-sDEVICE=pdfwrite',
		'-dCompatibilityLevel=1.4',
		f'-dPDFSETTINGS={pdfsettings}',
		'-dDetectDuplicateImages=true',
		'-dDownsampleColorImages=true',
		f'-dColorImageResolution={dpi}',
		'-dDownsampleGrayImages=true',
		f'-dGrayImageResolution={dpi}',
		'-dDownsampleMonoImages=true',
		f'-dMonoImageResolution={dpi}',
		'-dNOPAUSE', '-dQUIET', '-dBATCH',
		f'-sOutputFile={output_path}',
		input_path,
	]
	try:
		subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		return True
	except subprocess.CalledProcessError:
		return False


def convert_pdf_to_jpgs(input_path: str, dpi: int = 150) -> List[str]:
	images = convert_from_path(input_path, dpi=dpi)
	output_paths: List[str] = []
	base_name = os.path.splitext(os.path.basename(input_path))[0]
	for idx, img in enumerate(images, start=1):
		jpg_name = generate_timestamped_name(f"{base_name}_page_{idx}", ".jpg")
		jpg_path = os.path.join(STATIC_FILES_FOLDER, jpg_name)
		rgb_img = img.convert('RGB') if isinstance(img, Image.Image) else img
		rgb_img.save(jpg_path, 'JPEG', quality=90, optimize=True)
		output_paths.append(jpg_path)
	return output_paths


@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')


@app.route('/compress', methods=['POST'])
def compress_route():
	if 'pdf' not in request.files:
		flash('No file part in request')
		return redirect(url_for('index'))

	file = request.files['pdf']
	if file.filename == '':
		flash('No file selected')
		return redirect(url_for('index'))

	if not allowed_file(file.filename):
		flash('Unsupported file type. Please upload a PDF.')
		return redirect(url_for('index'))

	filename = secure_filename(file.filename)
	temp_input_path = os.path.join(UPLOAD_FOLDER, generate_timestamped_name('upload', os.path.splitext(filename)[1]))
	file.save(temp_input_path)

	output_name = generate_timestamped_name('compressed', '.pdf')
	output_path = os.path.join(STATIC_FILES_FOLDER, output_name)

	try:
		compress_pdf_pypdf2(temp_input_path, output_path)
	finally:
		try:
			os.remove(temp_input_path)
		except OSError:
			pass

	return send_file(
		output_path,
		as_attachment=True,
		download_name=f"compressed_{filename}",
		mimetype='application/pdf',
		max_age=0
	)


@app.route('/convert', methods=['POST'])
def convert_route():
	if 'pdf' not in request.files:
		flash('No file part in request')
		return redirect(url_for('index'))

	file = request.files['pdf']
	if file.filename == '':
		flash('No file selected')
		return redirect(url_for('index'))

	if not allowed_file(file.filename):
		flash('Unsupported file type. Please upload a PDF.')
		return redirect(url_for('index'))

	filename = secure_filename(file.filename)
	temp_input_path = os.path.join(UPLOAD_FOLDER, generate_timestamped_name('upload', os.path.splitext(filename)[1]))
	file.save(temp_input_path)

	try:
		jpg_paths = convert_pdf_to_jpgs(temp_input_path, dpi=150)
	finally:
		try:
			os.remove(temp_input_path)
		except OSError:
			pass

	zip_buffer = io.BytesIO()
	with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for img_path in jpg_paths:
			zipf.write(img_path, arcname=os.path.basename(img_path))
	zip_buffer.seek(0)

	for img_path in jpg_paths:
		try:
			os.remove(img_path)
		except OSError:
			pass

	return send_file(
		zip_buffer,
		as_attachment=True,
		download_name=f"{os.path.splitext(filename)[0]}_images.zip",
		mimetype='application/zip',
		max_age=0
	)


@app.errorhandler(413)
def request_entity_too_large(error):
	flash('File too large. Max 100MB.')
	return redirect(url_for('index'))


if __name__ == '__main__':
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
