import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import cv2
import numpy as np

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hitung_prosentase_warna(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return 0
    ambang_putih = np.array([240, 240, 240])
    mask_non_putih = np.any(img < ambang_putih, axis=2)
    jumlah_non_putih = np.sum(mask_non_putih)
    total_pixel = img.shape[0] * img.shape[1]
    return (jumlah_non_putih / total_pixel) * 100

def prediksi_harga(persen):
    if persen < 10:
        return 1000
    elif persen < 25:
        return 1500
    elif persen < 50:
        return 2000
    elif persen < 75:
        return 2500
    else:
        return 3000

@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = []
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path_pdf = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_pdf)

            # Convert PDF ke gambar
            pages = convert_from_path(path_pdf, dpi=150)
            for i, page in enumerate(pages):
                img_path = os.path.join(app.config['UPLOAD_FOLDER'], f"page_{i}.png")
                page.save(img_path, 'PNG')

                persen = hitung_prosentase_warna(img_path)
                harga = prediksi_harga(persen)

                hasil.append({
                    'halaman': i + 1,
                    'warna': f"{persen:.2f}%",
                    'harga': f"Rp {harga:,}"
                })

    return render_template("index.html", hasil=hasil)

if __name__ == '__main__':
    app.run(debug=True)
