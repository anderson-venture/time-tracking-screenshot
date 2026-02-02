import os
import tempfile
from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
from config import ServerConfig
from storage_handler import StorageHandler

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = ServerConfig.MAX_UPLOAD_SIZE

storage_handler = StorageHandler()

def verify_token():
    """Verify API token from request headers"""
    token = request.headers.get('X-API-Token')
    return token == ServerConfig.API_TOKEN

def check_ip_whitelist():
    """Check if client IP is whitelisted (if whitelist is enabled)"""
    if not ServerConfig.ALLOWED_IPS:
        return True  # No whitelist, allow all
    
    client_ip = request.remote_addr
    # Simple IP check (could be enhanced with proper CIDR matching)
    return any(client_ip.startswith(allowed.split('/')[0]) for allowed in ServerConfig.ALLOWED_IPS)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'service': 'monitoring-server',
        'version': '1.0'
    })

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload from client computers"""
    # Check IP whitelist
    if not check_ip_whitelist():
        return jsonify({'error': 'IP not allowed'}), 403
    
    # Verify authentication
    if not verify_token():
        return jsonify({'error': 'Invalid API token'}), 401
    
    # Check if file is present
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400
    
    # Get computer ID
    computer_id = request.form.get('computer_id', 'unknown')
    
    # Save file temporarily
    temp_fd, temp_path = tempfile.mkstemp(suffix='.zip')
    try:
        os.close(temp_fd)
        file.save(temp_path)
        
        # Process and store the file
        success = storage_handler.save_upload(temp_path, computer_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'File uploaded and processed',
                'computer_id': computer_id
            }), 200
        else:
            return jsonify({'error': 'Failed to process file'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temporary file
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get storage statistics (requires authentication)"""
    if not verify_token():
        return jsonify({'error': 'Invalid API token'}), 401
    
    stats = storage_handler.get_statistics()
    return jsonify(stats)

@app.route('/', methods=['GET'])
def dashboard():
    """Simple web dashboard"""
    if not verify_token():
        # Require token even for dashboard
        return "Authentication required. Add X-API-Token header.", 401
    
    stats = storage_handler.get_statistics()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Monitoring Server Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 40px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }
            .stat-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 6px;
                border-left: 4px solid #007bff;
            }
            .stat-value {
                font-size: 32px;
                font-weight: bold;
                color: #007bff;
            }
            .stat-label {
                color: #666;
                font-size: 14px;
                margin-top: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #007bff;
                color: white;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Monitoring Server Dashboard</h1>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{{ total_computers }}</div>
                    <div class="stat-label">Total Computers</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ total_size_mb }} MB</div>
                    <div class="stat-label">Total Storage Used</div>
                </div>
            </div>
            
            <h2>Computer Details</h2>
            <table>
                <thead>
                    <tr>
                        <th>Computer ID</th>
                        <th>File Count</th>
                        <th>Storage (MB)</th>
                    </tr>
                </thead>
                <tbody>
                    {% for computer_id, data in computers.items() %}
                    <tr>
                        <td>{{ computer_id }}</td>
                        <td>{{ data.file_count }}</td>
                        <td>{{ data.size_mb }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(html, **stats)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    """Manually trigger cleanup of old data"""
    if not verify_token():
        return jsonify({'error': 'Invalid API token'}), 401
    
    try:
        storage_handler.cleanup_old_data()
        return jsonify({'status': 'success', 'message': 'Cleanup completed'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
