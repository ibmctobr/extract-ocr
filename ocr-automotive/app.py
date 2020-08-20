from flask import Flask, request
from flask_cors import CORS
from controllers import ocr_extract
import os

ocrClass = ocr_extract.Extract_OCR()
app = Flask(__name__)
CORS(app)
cf_port = os.getenv('PORT')

@app.route("/", methods=['POST'])
def check_automotive():
    data = request.get_json(force=True)
    feedback_image = ocrClass.get_image(str(data['weblink']), 'automotive.jpg')
    if feedback_image['status'] == '200':
        return ocrClass.check_char()
    else:
        return feedback_image

if __name__ == '__main__':
    if cf_port is None:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=int(cf_port), debug=True)