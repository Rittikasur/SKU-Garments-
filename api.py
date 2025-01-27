from flask import Flask, jsonify,request
from flask_cors import CORS
from upload_pipeline import project_creation,convert_pdf_to_jpg,upload_images_from_folder,preprocess_inputs,logging
from model_training import train_and_store_model,load_and_infer
from export_pipeline import export_annotation
import os
import sqlite3
from flask import g
import tempfile
import shutil

path = os.environ['PATH']
os.environ["PATH"] = "D:/Rohit/GarmentsSKU/SKU-Garments-/Release-24.07.0-0/poppler-24.07.0/Library/bin" + ';' + path
DATABASE = 'application.db'
PROJECT_PATH = "D:/Rohit/GarmentsSKU/SKU-Garments-"
app = Flask(__name__)
CORS(app)

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Flask app with CORS enabled!"})

@app.route('/create_project', methods=['POST'])
def createProject():
    data = request.get_json()

    title = data.get('title')
    description = data.get('description')
    items = data.get('items')
    project_title,project_desc,project_labels = preprocess_inputs(title,description,items)
    logging.info(project_title)
    logging.info(project_desc)
    logging.info(project_labels)
    project_id = project_creation( project_title,project_desc,project_labels)
    # Process the data as needed
    return jsonify({"projectID":project_id})

@app.route('/upload_data', methods=['POST'])
def uploadData():
    project_name = request.form.get("project_name")
    project_id = request.form.get("project_id")
    output_dir = os.path.join(PROJECT_PATH,"raw_data",project_name)
    print(output_dir,project_id)
    print(request.files)
    if 'files' not in request.files or project_id is None or output_dir is None :
        return 'No file part or project ID or Output Directory'
    

    files = request.files.getlist('files')
    if len(files) > 10:
        return 'Too many files. Maximum 10 allowed.'

    for file in files:
        extension = file.filename.split(".")[1].lower()
        if(extension != "pdf"):
            return jsonify({"message": "Files not all pdf"})
    
    try:
        temp_dir = tempfile.mkdtemp()
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)

        print("Converting Images to Images")
        convert_pdf_to_jpg(temp_dir, output_dir)
        print("Uploading images to Label Studio")
        upload_images_from_folder(output_dir, project_id)
        print("Cleaning temporary upload folder")
        print(os.environ["PATH"])
        shutil.rmtree(temp_dir)
    except Exception as e:
        return jsonify({"error": e})

    return jsonify({"message": "Files uploaded successfully"})


@app.route('/export_data', methods=['POST'])
def exportData():
    data = request.get_json()
    project_name = data.get('project_name')
    project_id = data.get('project_id')
    export_annotation(project_name,project_id)
    return jsonify({"message": "Annotations Exported successfully"})

@app.route('/train_model', methods=['POST'])
def trainModel():
    data = request.get_json()
    project_name = data.get('project_name')
    train_and_store_model(project_name)
    return jsonify({"message": "Model Trained successfully"})

@app.route('/infer', methods=['POST'])
def inferModel():
    key = None
    project_name = request.form.get("project_name")
    if 'file' not in request.files:
        return 'No file provided'
    
    file = request.files['file']
    filename = file.filename.split(".")[1].lower()
    if(filename == "pdf"):
        key = "PDF"
    elif(filename in ["jpeg","jpg","png"]):
        key = "IMG"
    else:
        return "Not valid file"
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, file.filename)
    file.save(file_path)

    load_and_infer(project_name,file_path,key)
    return jsonify({"message": "Model Trained successfully"})


if __name__ == '__main__':
    app.run(debug=True)
