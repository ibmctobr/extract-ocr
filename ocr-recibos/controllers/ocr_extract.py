import json, os, time, requests

class Extract_OCR():
    def __init__(self):
        self.apiKey_ocrSpace = "YOUR_APIKEY_HERE"
        self.url_ocrSpace = "https://api.ocr.space/parse/image"

    def get_image(self, link, name):
        response = requests.get(link)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),'images',name),'wb') as image:
            image.write(response.content)
        time.sleep(5)
        if response.status_code == 200:
            return {'status':'200', 'message':'image saved'}
        else:
            return {'status':f'{response.status_code}', 'message':response.text}

    def check_recibo(self):
        products = []
        filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images','recibo.jpg')
        with open(filename, 'rb') as f:
            response = requests.post(self.url_ocrSpace,
                                     files={filename: f},
                                     data={"apikey": self.apiKey_ocrSpace,
                                           "language": "por", 'isOverlayRequired': False})
        if response.status_code == 200:
            result = json.loads(response.content.decode())
            text_extract = result['ParsedResults'][0]['ParsedText'].replace('\r','').split('\n')
            for text in text_extract:
                if text == 'Descricao Uni tario':
                    first_iten = text_extract.index(text)+1
                    for itens in range(first_iten, len(text_extract)):
                        item = text_extract[itens].replace(',','').lower()
                        if item.isnumeric() != True:
                            products.append(item)
                            continue
                        else:
                            break
        if products == []:
            return {'status':'200', 'message':'No products found'}
        else:
            return {'status':'200', 'message':products}