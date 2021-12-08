from flask import Flask, json, request, jsonify
import os
import urllib.request
from werkzeug.utils import secure_filename
import cv2
import sys
from flask import Flask, send_from_directory, abort


app = Flask(__name__)

app.secret_key = "caircocoders-ednalan"

UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def main():
    return 'Homepage'


@app.route('/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'files[]' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp

    files = request.files.getlist('files[]')

    errors = {}
    success = False
    PATHS = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            PATHS.append(filename)
            success = True
        else:
            errors[file.filename] = 'File type is not allowed'

    if success and errors:
        errors['message'] = 'File(s) successfully uploaded'
        resp = jsonify(errors)
        resp.status_code = 500
        return resp
    if success:

        imagePath = (os.path.join(app.config['UPLOAD_FOLDER'], filename))

        image = cv2.imread(imagePath)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faceCascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.66,
            minNeighbors=3,
            minSize=(30, 30)
        )
        pic = ""
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 0), 0)
            roi_color = image[y-38:y + h+35, x-15:x + w+15]
            print("[INFO] Object found. Saving locally.")
            cv2.imwrite("face/"+str(w) + str(h) +
                        '_faces.jpg', roi_color)
            pic = str(w) + str(h) + '_faces.jpg'

        resp = jsonify({'message': 'Files successfully uploaded'})
        resp.status_code = 201
        return send_from_directory("face", pic, as_attachment=True)
    else:
        resp = jsonify(errors)
        resp.status_code = 500
        return resp


if __name__ == '__main__':
    app.run(debug=True)
