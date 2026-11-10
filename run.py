import sys
import os
from pathlib import Path

# Add project directory to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from truthlens_ai.app import app

if __name__ == '__main__':
    print("=" * 65)
    print(" TruthLens AI — AI-Powered Fake News Detection & Verification ")
    print("=" * 65)
    print(" Server running locally at: http://127.0.0.1:5000")
    print(" Press CTRL+C to stop.")
    print("=" * 65)
    app.run(host='127.0.0.1', port=5000, debug=True)
