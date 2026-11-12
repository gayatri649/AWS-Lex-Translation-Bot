
import json
import urllib.parse
import urllib.request

def lambda_handler(event, context):
    intent_name = event['sessionState']['intent']['name']

    try:
        slots = event['sessionState']['intent']['slots']

        input_text = slots['text']['value']['interpretedValue'].strip()
        language_slot = slots['language']['value']['interpretedValue']

        if not input_text:
            raise ValueError("Input text is empty.")

        language_codes = {
            'French': 'fr',
            'Japanese': 'ja',
            'Chinese': 'zh',
            'Spanish': 'es',
            'German': 'de',
            'Norwegian': 'no',
            'Kannada':'kn'
        }

        if language_slot not in language_codes:
            raise ValueError(f"Unsupported language: {language_slot}")

        target_code = language_codes[language_slot]

        params = urllib.parse.urlencode({
            'q': input_text,
            'langpair': f'en|{target_code}'
        })

        url = 'https://api.mymemory.translated.net/get?' + params

        request = urllib.request.Request(
            url,
            headers={'User-Agent': 'TranslateBot'}
        )

        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))

        if result.get('responseStatus') != 200:
            raise Exception(result.get('responseDetails', 'Translation failed'))

        translated_text = result['responseData']['translatedText']

        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {
                    "name": intent_name,
                    "state": "Fulfilled"
                }
            },
            "messages": [{
                "contentType": "PlainText",
                "content": translated_text
            }]
        }

    except Exception as error:
        print("Translation error:", str(error))

        return {
            "sessionState": {
                "dialogAction": {"type": "Close"},
                "intent": {
                    "name": intent_name,
                    "state": "Failed"
                }
            },
            "messages": [{
                "contentType": "PlainText",
                "content": "Translation error: " + str(error)
            }]
        }
