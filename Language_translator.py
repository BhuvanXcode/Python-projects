from googletrans import Translator

# create an instance of the translator
translator = Translator()

translation = translator.translate("Hello, world!", dest="spanish")
# print the translated text
print(translation.text)
