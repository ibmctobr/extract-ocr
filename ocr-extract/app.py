from flask import Flask, request
from flask_cors import CORS
from controllers import ocr_extract
import os

osrClass = ocr_extract.Extract_OCR()
app = Flask(__name__)
CORS(app)
cf_port = os.getenv('PORT')

@app.route("/verifier", methods=['POST'])
def verifier():
    data = request.get_json(force=True)
    feedback_image = osrClass.get_image(str(data['weblink']), 'bank.jpg')

    if feedback_image['status'] == '200':
        boleto = osrClass.invoke_ocr_API()
        return boleto
    else:
        return feedback_image

@app.route("/checkplate", methods=['POST'])
def checkplate():
    data = request.get_json(force=True)
    feedback_image = osrClass.get_image(str(data['weblink']), 'plate.jpg')
    if feedback_image['status'] == '200':
        return osrClass.check_plate()
    else:
        return feedback_image


if __name__ == '__main__':
    if cf_port is None:
        app.run(host='0.0.0.0', port=5000, debug=True)
    else:
        app.run(host='0.0.0.0', port=int(cf_port), debug=True)