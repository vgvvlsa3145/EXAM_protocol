import os
import sys
from waitress import serve
from config.wsgi import application

# Add the current directory to the sys.path so 'config' can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("--------------------------------------------------")
    print("🚀 Starting Production Server (Waitress)")
    print("--------------------------------------------------")
    print("Server is running on: http://0.0.0.0:8000")
    print("Press Ctrl+C to stop.")
    print("--------------------------------------------------")
    
    # Run the Waitress server
    # threads=10 allows 10 concurrent requests to be handled simultaneously
    serve(application, host='0.0.0.0', port=8000, threads=10)
