# Import necessary modules
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import os
import secrets  # For secure filename generation

# Initialize Flask application
app = Flask(__name__)

# Set the upload folder path (modify as needed)
UPLOAD_FOLDER = '/home/pi/Desktop'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed image extensions

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')

# Route for handling file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['image']
        # Check if the file is empty
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Generate a secure filename to prevent conflicts
            filename = 'captured_img' + '.' + file.filename.rsplit('.', 1)[1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # Save the uploaded image to the specified location
            file.save(filepath)

            flash('Image uploaded successfully!')
            return redirect(url_for('index'))

        else:
            flash('Invalid file type. Allowed extensions: ' + ', '.join(ALLOWED_EXTENSIONS))
            return redirect(request.url)

    return redirect(url_for('index'))  # Redirect back to the index page

# Route for handling chosen plant
@app.route('/chosen-plant', methods=['POST'])
def chosen_plant():
    if request.method == 'POST':
        plant = request.form['plant']
        # Perform further processing with the chosen plant name here
        print(f'Chosen plant: {plant}')
        # Write the chosen plant name to the plantName.txt file
        with open('plantName.txt', 'w') as file:
            file.write(plant)
        return 'Chosen plant received successfully!', 200
    else:
        return 'Invalid request method', 405

# Route for getting moisture level
@app.route('/moisture-level', methods=['GET'])
def get_moisture_level():
    moisture_level_file_path = 'moisture_level.txt'
    # Read moisture level from file
    with open(moisture_level_file_path, 'r') as file:
        moisture_level = int(file.read())
    # Return the moisture level as JSON
    return jsonify({'moistureLevel': moisture_level})

# Run the Flask application
if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.run(debug=True, port=80, host='0.0.0.0')
