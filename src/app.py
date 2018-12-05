from flask import Flask, request, jsonify, render_template, make_response, send_file,  url_for, flash, redirect, send_from_directory
from flask_pymongo import PyMongo
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = set(['ics', 'json', 'bson'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file - это то что показывала тебе
            #filename - просто имя файла.
            return file
            '''file_contents = file.read()
            response = make_response(file_contents)
            response.headers["Cache-Control"] = "must-revalidate"
            response.headers["Pragma"] = "must-revalidate"
            response.headers["Content-type"] = "application/ics"
            print(file)
            return str(response)

            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))'''

    return render_template('main.html')

@app.route('/tmp/<filename>')
def uploaded_file(filename):
    return send_file(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/statistics')
def statistics():
    return render_template('statistics.html')

@app.route('/lovelyFriend')
def lovelyFriend():
    return render_template('lovelyFriend.html')

@app.route('/organizedEvents')
def solvedProblems():
    return render_template('/organizedEvents.html')

@app.route('/employment')
def employment():
    return render_template('/employment.html')

@app.route('/synchronization')
def synchronization():
    return render_template('/synchronization.html')

if __name__ == '__main__':
    app.run(debug=True)
