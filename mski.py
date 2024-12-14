import os
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__, static_folder="static", template_folder="templates")

MEDIA_FOLDER = "media"
SUBFOLDERS = ["images", "videos", "audio"]
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "mp4", "mp3", "wav", "ogg"}
app.config["MEDIA_FOLDER"] = MEDIA_FOLDER

def create_media_folders():
    if not os.path.exists(MEDIA_FOLDER):
        os.makedirs(MEDIA_FOLDER)
    for subfolder in SUBFOLDERS:
        path = os.path.join(MEDIA_FOLDER, subfolder)
        if not os.path.exists(path):
            os.makedirs(path)

create_media_folders()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template("home.html")
    
    return render_template('stats.html', total_files=total_files, total_size=total_size, most_downloaded=most_downloaded)
@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = safe_join('uploads', filename)  # Ensure secure file paths
        return send_from_directory('uploads', filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            return render_template("admin_dashboard.html", success=True)
        else:
            return render_template("admin_login.html", error="Invalid credentials!")
    return render_template("admin_login.html")

@app.route('/upload/<media_type>', methods=['POST'])
def upload_file(media_type):
    if media_type not in SUBFOLDERS:
        return jsonify({"error": "Invalid media type."}), 400

    if 'file' not in request.files:
        return jsonify({"error": "No file part."}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file."}), 400

    if file and allowed_file(file.filename):
        filename = file.filename
        save_path = os.path.join(MEDIA_FOLDER, media_type, filename)
        file.save(save_path)
        return jsonify({"message": f"File {filename} uploaded successfully!"}), 200
    else:
        return jsonify({"error": "File type not allowed."}), 400

@app.route('/media/<media_type>/<filename>', methods=['GET'])
def serve_file(media_type, filename):
    if media_type not in SUBFOLDERS:
        return jsonify({"error": "Invalid media type."}), 400

    directory = os.path.join(MEDIA_FOLDER, media_type)
    return send_from_directory(directory, filename)

@app.route('/browse', methods=['GET', 'POST'])
def browse_media():
    search_query = request.form.get("search_query", "").lower()
    media_files = {}
    for subfolder in SUBFOLDERS:
        path = os.path.join(MEDIA_FOLDER, subfolder)
        files = os.listdir(path) if os.path.exists(path) else []
        if search_query:
            files = [f for f in files if search_query in f.lower()]
        media_files[subfolder] = files
    return render_template("browse_media.html", media_files=media_files, subfolders=SUBFOLDERS, search_query=search_query)

if __name__ == "__main__":
    app.run(debug=True)
