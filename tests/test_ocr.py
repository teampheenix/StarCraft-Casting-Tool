import PIL
import pytesseract

from scctool.tasks.sc2ClientInteraction import cropImage, ocr, ocr_new


def test_orc():
    data = list()
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_36_59.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_02.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_03.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_04.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_05.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_06.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_07.jpg"})
    data.append({'players': ['mrtea', 'pressure'],
                 'swap': True,
                 'file': "tests\\data\\Screenshot2018-04-14 08_43_03.jpg"})
    crop_regions = []
    crop_regions.append((0.3, 0.7, 0.0, 0.08))
    crop_regions.append((0.3, 0.7, 0.0, 0.14))
    crop_regions.append((0.12, 0.35, 0.88, 1.0))
    crop_regions.append((0.1, 0.4, 0.8, 1.0))
    crop_regions.append((0.12, 0.35, 0.88, 1.0))
    crop_regions.append((0.1, 0.4, 0.8, 1.0))
    crop_regions.append((0.3, 0.7, 0.0, 0.08))
    crop_regions.append((0.0, 1.0, 0.0, 1.0))
    tesseract = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd = tesseract
    for item in data:
        full_img = PIL.Image.open(item['file']).convert('L')

        for crop_region in crop_regions:
            img = cropImage(full_img, crop_region)
            found, swap = ocr(item['players'], img, tesseract)
            print(f'{found} {crop_region}')
            if found:
                break
        assert found
        assert swap == item['swap']


def test_orc_new():
    data = list()
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_36_59.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_02.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_03.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_04.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_05.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_06.jpg"})
    data.append({'players': ['Xaoras', 'DERASTAT'],
                 'swap': False,
                 'file': "tests\\data\\Screenshot2018-04-07 16_37_07.jpg"})
    data.append({'players': ['mrtea', 'pressure'],
                 'swap': True,
                 'file': "tests\\data\\Screenshot2018-04-14 08_43_03.jpg"})

    crop_regions = []
    crop_regions.append((0.3, 0.7, 0.0, 0.08))
    crop_regions.append((0.3, 0.7, 0.0, 0.14))
    crop_regions.append((0.12, 0.35, 0.88, 1.0))
    crop_regions.append((0.1, 0.4, 0.8, 1.0))
    crop_regions.append((0.12, 0.35, 0.88, 1.0))
    crop_regions.append((0.1, 0.4, 0.8, 1.0))
    crop_regions.append((0.3, 0.7, 0.0, 0.08))
    crop_regions.append((0.0, 1.0, 0.0, 1.0))

    for item in data:
        print(item['file'])
        full_img = PIL.Image.open(item['file']).convert('L')
        from tesserocr import PyTessBaseAPI
        api = PyTessBaseAPI(init=False)
        api.InitFull(path='D:\\tessdata', configs=['D:\\config.txt'])

        for crop_region in crop_regions:
            found, swap = ocr_new(item['players'], full_img, api, crop_region)
            print(f'{found} {crop_region}')
            if found:
                break
        assert found
        assert swap == item['swap']


if __name__ == '__main__':
    test_orc()
    print('----------------')
    test_orc_new()
