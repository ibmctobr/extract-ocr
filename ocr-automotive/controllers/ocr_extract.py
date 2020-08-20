import json, os, time, requests, cv2, numpy as np

class Extract_OCR():
    def __init__(self):
        self.apiKey_ocrSpace = "YOUR_APIKEY_HERE"
        self.url_ocrSpace = "https://api.ocr.space/parse/image"

    def invoke_ocr_API(self):
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','bank.jpg')
        with open(filename, 'rb') as f:
            response = requests.post(self.url_ocrSpace,
                            files={filename: f},
                            data={"apikey": self.apiKey_ocrSpace,
                                  "language": "por", 'isOverlayRequired': False})
        if response.status_code == 200:
            result = json.loads(response.content.decode())
            text_detected = str(result["ParsedResults"][0]['ParsedText']).replace('\r','|').replace('\n','|').split('||')
            try:
                #default bradesco
                num_boleto = text_detected[2].replace('.', '').replace(' ','')
                valor = text_detected[16].split('RS')[1].replace(' ', '')
                return {'status':'200','message':[num_boleto,valor]}
            except IndexError:
                #switch other banks
                if text_detected[1] == 'Nu S.A.':
                    num_boleto = str(text_detected[10] + text_detected[16]).replace('.','').replace(' ','').strip()
                    valor = text_detected[50]
                    return {'status': '200', 'message': [num_boleto, valor]}
                elif 'Banco Itaú' in text_detected[1] or text_detected[0]:
                    if 'Banco Itaú' in text_detected[0]:
                        num_boleto = text_detected[0][19:].replace('.','').replace(' ','')
                        valor = text_detected[-4]
                        return {'status': '200', 'message': [num_boleto, valor]}
                    else:
                        num_boleto = text_detected[0][6:-16].replace('.','').replace(' ','')
                        valor = text_detected[-4].replace('R$ ','')
                        return {'status': '200', 'message': [num_boleto, valor]}

    def get_image(self, link, name):
        response = requests.get(link)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'images',name),'wb') as image:
            image.write(response.content)
        time.sleep(5)
        if response.status_code == 200:
            return {'status':'200', 'message':'image saved'}
        else:
            return {'status':f'{response.status_code}', 'message':response.text}

    def check_plate(self):

        def image_update():
            filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images', 'automotive.jpg')
            image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)

            scale_percent = 40  # percent of original size
            width = int(image.shape[1] * scale_percent / 100)
            height = int(image.shape[0] * scale_percent / 100)
            dim = (width, height)
            # resize image
            resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            # apply thresholding to preprocess the image
            gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            gray = cv2.dilate(gray, np.ones((4, 4), np.uint8))

            gray = cv2.erode(gray, np.ones((2, 2), np.uint8))

            # save the processed image in the /static/uploads directory
            ofilename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new.png')
            cv2.imwrite(ofilename, gray)
            return

        #try:
        image_update()
        #return {'message':'Sorry, try again later!'}

        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'new.png')
        with open(filename, 'rb') as f:
            response = requests.post(self.url_ocrSpace,
                                     files={filename: f},
                                     data={"apikey": self.apiKey_ocrSpace,
                                           "language": "por", 'isOverlayRequired': False})
        if response.status_code == 200:
            result = json.loads(response.content.decode())
            try:
                text_extract = str(result["ParsedResults"][0]['ParsedText']).replace('\r','').replace('\n','').replace(' ','')
            except IndexError:
                return {'status':'200', 'message':'It was not possible to extract the characters from the image. Please insert a closer image of the plate.'}

            peace1 = text_extract.replace(' ','')[:3]
            peace2 = text_extract.replace(' ','')[4:].replace('S','6').replace('B','8')
            if len(peace2) == 3:
                peace2 = text_extract.replace(' ', '')[3:].replace('S','6').replace('B','8')
            #check peaces
            for char in peace1:
                if char.isnumeric() == False:
                    continue
                else:
                    return {'status':'200',
                                'message':'It was not possible to extract the characters from the image. Please insert a closer image of the plate.'}
            for char in peace2:
                if char.isnumeric() == True:
                    continue
                else:
                    return {'status': '200',
                                'message': 'It was not possible to extract the characters from the image. Please insert a closer image of the plate.'}

            return {'status':'200', 'message':peace1+peace2}

    def check_doc(self):
        def checkpeace(text):
            peace1 = text.replace(' ', '')[:3].replace('ó','P').replace('l','I')
            peace2 = text.replace(' ', '')[4:].replace('S', '6').replace('B', '8')
            if len(peace2) == 3:
                peace2 = text.replace(' ', '')[3:].replace('S', '6').replace('B', '8')
            # check peaces
            for char in peace1:
                if char.isnumeric() == False:
                    continue
                else:
                    return {''}
            for char in peace2:
                if char.isnumeric() == True:
                    continue
                else:
                    return {''}

            return peace1+peace2

        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','automotive.jpg')
        with open(filename, 'rb') as f:
            response = requests.post(self.url_ocrSpace,
                                     files={filename: f},
                                     data={"apikey": self.apiKey_ocrSpace,
                                           "language": "por", 'isOverlayRequired': False})
        if response.status_code == 200:
            result = json.loads(response.content.decode())
            try:
                text_extract = str(result["ParsedResults"][0]['ParsedText']).replace('\r', '').split('\n')
                if len(text_extract[5].replace('\n', '').replace(' ','').replace('-','')) == 7:
                    parse = text_extract[5].replace('\n', '').replace(' ','').replace('-','')
                    tratament = checkpeace(parse)
                    if tratament != '':
                        return {'status': '200', 'message': tratament}

                elif len(text_extract[8].replace('\n', '').replace(' ','').replace('-','')) == 7:
                    parse = text_extract[8].replace('\n', '').replace(' ','').replace('-','')
                    tratament = checkpeace(parse)
                    if tratament != '':
                        return {'status': '200', 'message': tratament}

                else:
                    for string in text_extract:
                        if len(string.replace('\n', '').replace(' ','').replace('-','')) == 7:
                            parse = checkpeace(string.replace('\n', '').replace(' ','').replace('-',''))
                            tratament = checkpeace(parse)
                            if tratament != '':
                                return {'status': '200', 'message': tratament}
                            else:
                                continue
                        else:
                            continue
                    return {'status': '200',
                            'message': 'Plate number not found. Please insert a closer image of the plate.'}
            except IndexError:
                return {'status': '200',
                        'message': 'It was not possible to extract the characters from the image. Please insert a closer image of the plate.'}

    def check_char(self):
        try:
            plate = Extract_OCR.check_plate(self)
            if plate['message'] == '':
                return Extract_OCR.check_doc(self)
            return plate
        except Exception:
            return {'status':'500', 'message':'Sorry, try again later!'}
