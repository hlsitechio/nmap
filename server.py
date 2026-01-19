from flask import Flask, request, jsonify
import subprocess
import shlex
import re

app = Flask(__name__)

@app.route('/scan', methods=['POST'])
def scan():
    data = request.json or {}
    target = data.get('target', '')
    args = data.get('args', '-sV')

    # Basic validation
    if not target:
        return jsonify({'error': 'target required'}), 400

    # Sanitize target (IP or hostname only)
    target = shlex.quote(target)

    # Allowed safe arguments
    safe_args = re.sub(r'[;&|`$]', '', args)

    cmd = f"nmap {safe_args} {target}"

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        return jsonify({
            'command': cmd,
            'output': result.stdout,
            'error': result.stderr,
            'code': result.returncode
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'scan timeout (300s)'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/quick', methods=['POST'])
def quick_scan():
    """Quick scan - top 100 ports"""
    data = request.json or {}
    target = shlex.quote(data.get('target', ''))

    if not target:
        return jsonify({'error': 'target required'}), 400

    cmd = f"nmap -T4 --top-ports 100 {target}"

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
        return jsonify({
            'output': result.stdout,
            'error': result.stderr
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/version', methods=['GET'])
def version():
    result = subprocess.run(['nmap', '--version'], capture_output=True, text=True)
    return jsonify({'version': result.stdout.split('\n')[0]})

@app.route('/health', methods=['GET'])
def health():
    return 'ok'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
