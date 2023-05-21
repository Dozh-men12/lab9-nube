from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import boto3
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.static_folder = 'static'
app.config['S3_BUCKET'] = 'lab9-oscar'  # Reemplaza con el nombre de tu bucket de S3
app.config['S3_REGION'] = 'us-east-1'  # Reemplaza con la región de tu bucket de S3

ALLOWED_EXTENSIONS = {'jpg', 'png'}

# Configuración de AWS
s3 = boto3.client('s3',
                   aws_access_key_id='AKIAUFERXWX2JZCN4ZEE',
                   aws_secret_access_key='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',
                   region_name=app.config['S3_REGION']
                   )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ruta principal
@app.route('/')
def index():
    # Obtener la lista de imágenes desde S3
    response = s3.list_objects_v2(Bucket=app.config['S3_BUCKET'])
    images = []
    if 'Contents' in response:
        for obj in response['Contents']:
            images.append(obj['Key'])

    # Renderizar el template index.html y pasar la lista de imágenes
    return render_template('index.html', images=images)

# Ruta para subir una imagen
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['image']
    
    # Verificar si el archivo tiene un nombre y una extensión válidos
    if file.filename == '' or not allowed_file(file.filename):
        return 'Archivo no permitido. Solo se aceptan archivos JPG y PNG.', 400

    filename = file.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Subir la imagen a S3
    s3.upload_file(filepath, app.config['S3_BUCKET'], filename)

    # Eliminar el archivo local
    os.remove(filepath)

    # Redireccionar a la página principal
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>')
def get_image(filename):
    return redirect(s3.generate_presigned_url('get_object', Params={'Bucket': app.config['S3_BUCKET'], 'Key': filename}))

if __name__ == '__main__':
    app.run(debug=True)