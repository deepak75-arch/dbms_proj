from flask import Flask, render_template, request, redirect, send_from_directory, flash, url_for
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'supersecretkey'

UPLOAD_FOLDER = 'backup_files'
ALLOWED_EXTENSIONS = {
    'sql', 'csv', 'json', 'txt', 'xml', 'jpg', 'jpeg', 'png', 'gif', 'pdf',
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'mp3', 'mp4', 'avi', 'zip', 'rar'
}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    files.sort(reverse=True)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        flash('No file chosen', 'error')
        return redirect(url_for('index'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'{filename} uploaded successfully.', 'success')
    else:
        flash('File type not supported.', 'error')

    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>', methods=['POST'])
def delete(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        flash(f'{filename} deleted.', 'info')
    else:
        flash('File not found.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
