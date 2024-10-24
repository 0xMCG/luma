from scrapers.luma import extract_event_links, extract_event_info
from scrapers.webdriverpool import WebDriverPool
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
app = Flask(__name__)

# Initialize WebDriver pool with version or latest ChromeDriver
chrome_version = os.getenv('CHROME_VERSION')  # Get Chrome version from .env
chrome_path = os.getenv('CHROME_PATH')
driver_pool = WebDriverPool(pool_size=1, version=chrome_version, path=chrome_path)

# Endpoint to get a list of events
@app.route('/get_list', methods=['GET'])
def get_list():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is not provided"}), 400
    
    try:
        # Get a WebDriver instance from the pool
        driver = driver_pool.get_driver()
        # Extract event links using the WebDriver instance
        event_list = extract_event_links(driver, url)
        # Return the WebDriver instance back to the pool
        driver_pool.return_driver(driver)
        # Return the extracted event list as JSON
        return jsonify({"data": event_list})
    except Exception as e:
        # Handle any exception and return a 500 error
        return jsonify({"error": str(e)}), 500

# Endpoint to get detailed information about a specific event
@app.route('/get_event', methods=['GET'])
def get_event():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is not provided"}), 400

    try:
        # Get a WebDriver instance from the pool
        driver = driver_pool.get_driver()
        # Extract event info using the WebDriver instance
        event_info = extract_event_info(driver, url)
        # Return the WebDriver instance back to the pool
        driver_pool.return_driver(driver)
        # Return the extracted event info as JSON
        return jsonify({"data": event_info})
    except Exception as e:
        # Handle any exception and return a 500 error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Set the host, port, and debug mode from environment variables
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Run the Flask application
    app.run(host=host, port=port, debug=debug)
