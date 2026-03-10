from flask import Flask, request, jsonify, render_template
from engine import obfuscate, ObfuscationError
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024  # 2MB max

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/obfuscate', methods=['POST'])
def obfuscate_endpoint():
    data = request.get_json()
    if not data or 'source' not in data:
        return jsonify({'error': 'No source provided'}), 400

    source = data['source']
    if not source.strip():
        return jsonify({'error': 'Empty source'}), 400

    if len(source) > 500_000:
        return jsonify({'error': 'Source too large (max 500KB)'}), 400

    options = {
        'dead_code': data.get('dead_code', True),
        'watermark': data.get('watermark', True),
    }

    try:
        result = obfuscate(source, options)
        return jsonify({
            'success': True,
            'result': result,
            'original_size': len(source),
            'obfuscated_size': len(result),
        })
    except ObfuscationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
