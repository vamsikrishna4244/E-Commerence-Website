from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Default to port 5000 if not specified in environment
    port = int(os.environ.get('PORT', 5000))
    # In production, set debug to False
    app.run(host='0.0.0.0', port=port, debug=True)
