# This is a _very simple_ example of a web service that recognizes faces in uploaded images.
# Upload an image file and it will check if the image contains the same face as another image.
# The result is returned as json. For example:
#
# $ curl -XPOST -F "file_1=@obama1.jpg" -F "file_2=@obama2.jpg" http://127.0.0.1:5001
#
# Returns:
#
# {
#  "face_found_in_image": true,
#  "is_same_person": true
# }
#
# This example is based on the Flask file upload example: http://flask.pocoo.org/docs/0.12/patterns/fileuploads/

# NOTE: This example requires flask to be installed! You can install it with pip:
# $ pip3 install flask

import face_recognition
from flask import Flask, jsonify, request, redirect

# You can change this to any folder on your system
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_image():
    print("we are entering upload image")
    # Check if a valid image file was uploaded
    print(request)
    if request.method == 'POST':
        print("the request method was POST")
        if 'file_1' not in request.files or 'file_2' not in request.files:
            print("either file_1 or file_2 was not included in the request")
            return redirect(request.url)

        file_1 = request.files['file_1']
        file_2 = request.files['file_2']

        if file_1.filename == '' or file_2.filename == '':
            print("one of the filenames was empty")
            return redirect(request.url)

        if file_1 and allowed_file(file_1.filename) and file_2 and allowed_file(file_2.filename):
            print("the file type is an allowed type")
            # The image file seems valid! Detect faces and return the result.
            return detect_faces_in_image(file_1, file_2)

    print("no valid image file was uploaded")
    # If no valid image file was uploaded, show the file upload form:
    return '''
    <!doctype html>
    <title>Are these the same picture?</title>
    <h1>Upload pictures and see if they are the same person!</h1>
    <form method="POST" enctype="multipart/form-data">
      <input type="file" name="file_1">
      <input type="file" name="file_2">
      <input type="submit" value="Upload">
    </form>
    '''


def detect_faces_in_image(file_stream_1, file_stream_2):
    # Pre-calculated face encoding of file_1 generated with face_recognition.face_encodings(known_face_image)
    img_1 = face_recognition.load_image_file(file_stream_1)
    known_face_encodings = face_recognition.face_encodings(img_1)

    # Load the uploaded image file
    img_2 = face_recognition.load_image_file(file_stream_2)
    # Get face encodings for any faces in the uploaded image
    unknown_face_encodings = face_recognition.face_encodings(img_2)

    face_found = False
    is_same = False

    if len(unknown_face_encodings) > 0 and len(known_face_encodings) > 0:
        face_found = True
        # See if the first face in the uploaded image matches the known face
        match_results = face_recognition.compare_faces([known_face_encodings[0]], unknown_face_encodings[0])
        if match_results[0]:
            is_same = True

    # Return the result as json
    result = {
        "faces_found_in_images": face_found,
        "is_same_person": is_same
    }
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True)
