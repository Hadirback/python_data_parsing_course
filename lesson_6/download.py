import requests

responce = requests.get('https://cdn.svyaznoy.ru/upload/iblock/7fc/4edb40d670142a57f4fad08e99324e94_thumb_4d76a05b13f4590.jpg')

with open('videocard.jpg', 'wb') as f:
    f.write(responce.content)

import wget

wget.download('https://cdn.svyaznoy.ru/upload/iblock/7fc/4edb40d670142a57f4fad08e99324e94_thumb_4d76a05b13f4590.jpg')