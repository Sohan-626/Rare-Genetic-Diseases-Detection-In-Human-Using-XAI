from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from werkzeug.utils import secure_filename
import analyze_medical_image
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'input_images'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Server configuration
HOST = '127.0.0.1'  # Localhost only
PORT = 5000         # Default port
SERVER_URL = f"http://{HOST}:{PORT}"

# Ensure required directories exist
required_dirs = ['input_images', 'output/visualizations', 'output/reports']
for directory in required_dirs:
    os.makedirs(directory, exist_ok=True)
    logger.info(f"Verified directory: {directory}")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve visualization files from the output/visualizations directory"""
    try:
        return send_from_directory('output/visualizations', filename)
    except Exception as e:
        logger.error(f"Error serving file {filename}: {str(e)}")
        return jsonify({'error': 'File not found'}), 404

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'file' not in request.files:
            logger.error("No file part in request")
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.error("No selected file")
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            logger.error(f"Invalid file type: {file.filename}")
            return jsonify({'error': 'Invalid file type. Allowed types are: PNG, JPG, JPEG'}), 400
        
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        logger.info(f"Saving file to: {filepath}")
        file.save(filepath)
        
        # Analyze the image
        logger.info(f"Starting analysis of: {filepath}")
        try:
            result = analyze_medical_image.analyze_image(filepath)
            if not result:
                raise ValueError("Analysis returned no results")
            logger.info("Analysis completed successfully")
            logger.info(f"Disease detected: {result.get('disease_name', 'Unknown')}")
        except Exception as analysis_error:
            logger.error(f"Error during image analysis: {str(analysis_error)}", exc_info=True)
            return jsonify({
                'error': 'Image analysis failed',
                'details': str(analysis_error),
                'message': 'Please ensure the image is a valid medical image and try again.'
            }), 500
        
        # Get base name for file paths
        base_name = os.path.splitext(filename)[0]
        
        # Update visualization paths to be relative to the server
        visualizations = {
            'detailed': f'/uploads/{base_name}_visualization.png',
            'simple': f'/uploads/viz_{base_name}.jpg'
        }
        
        # Verify visualization files exist
        viz_files_exist = True
        for viz_type, viz_path in visualizations.items():
            full_path = os.path.join('output/visualizations', os.path.basename(viz_path))
            if not os.path.exists(full_path):
                logger.warning(f"Visualization file not found: {full_path}")
                viz_files_exist = False
                visualizations[viz_type] = None
        
        if not viz_files_exist:
            logger.warning("Some visualization files are missing")
        
        # Prepare response data
        response_data = {
            'visualizations': visualizations,
            'disease_name': result.get('disease_name', 'Unknown Disease'),
            'disease_summary': result.get('disease_summary', 'No summary available'),
            'symptoms': result.get('symptoms', []),
            'genes': result.get('genes', []),
            'accuracy': result.get('accuracy', 0.0),
            'precision': result.get('precision', 0.0),
            'recall': result.get('recall', 0.0),
            'f1_score': result.get('f1_score', 0.0),
            'inference_time': result.get('inference_time', 0.0),
            'recommendations': result.get('recommendations', []),
            'report_content': result.get('report_content', 'No report available')
        }
        
        logger.info("Sending response data")
        logger.info(f"Disease: {response_data['disease_name']}")
        logger.info(f"Visualizations: {response_data['visualizations']}")
        logger.info(f"Number of symptoms: {len(response_data['symptoms'])}")
        logger.info(f"Number of genes: {len(response_data['genes'])}")
        logger.info(f"Number of recommendations: {len(response_data['recommendations'])}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An error occurred while processing the image',
            'details': str(e),
            'message': 'Please try again with a different image or contact support if the problem persists.'
        }), 500

if __name__ == '__main__':
    logger.info("Starting Flask application")
    logger.info("=" * 50)
    logger.info(f"Server will be available at: {SERVER_URL}")
    logger.info("=" * 50)
    logger.info("Press CTRL+C to stop the server")
    logger.info("=" * 50)
    app.run(debug=True, host=HOST, port=PORT) 