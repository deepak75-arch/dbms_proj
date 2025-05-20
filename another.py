from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import mysql.connector
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="934424@.",
    database="file_backup"
)

# Create table if not exists
def create_table():
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INT AUTO_INCREMENT PRIMARY KEY,
            filename VARCHAR(255),
            filetype VARCHAR(50),
            filesize INT,
            upload_date DATETIME
        )
    """)
    conn.commit()

create_table()

@app.route('/', methods=['GET', 'POST'])
def index():
    cursor = conn.cursor()
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            filetype = filename.split('.')[-1]
            filesize = os.path.getsize(filepath)
            upload_date = datetime.now()

            cursor.execute("""
                INSERT INTO files (filename, filetype, filesize, upload_date)
                VALUES (%s, %s, %s, %s)
            """, (filename, filetype, filesize, upload_date))
            conn.commit()

    cursor.execute("SELECT id, filename, filetype, filesize, upload_date FROM files")
    files = cursor.fetchall()
    return render_template('index.html', files=files)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_file(id):
    cursor = conn.cursor()
    cursor.execute("SELECT filename FROM files WHERE id = %s", (id,))
    result = cursor.fetchone()
    if result:
        filename = result[0]
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        cursor.execute("DELETE FROM files WHERE id = %s", (id,))
        conn.commit()
    return redirect(url_for('index'))

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
