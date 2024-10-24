from scraper.luma import init_driver, extract_event_links, extract_event_info
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

# get list of events
@app.route('/get_list', methods=['GET'])
def get_list():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is not provided"}), 400
    
    try:
        driver = init_driver()
        list = extract_event_links(driver, url)
        driver.quit()
        return jsonify({"data": list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# get a event info    
@app.route('/get_event', methods=['GET'])
def get_event():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "URL is not provided"}), 400

    try:
        driver = init_driver()
        event_info = extract_event_info(driver, url)
        print(event_info)
        driver.quit()
        return jsonify({"data": event_info})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    app.run(host=host, port=port, debug=debug)
