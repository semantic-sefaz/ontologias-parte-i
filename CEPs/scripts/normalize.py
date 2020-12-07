import unicodedata
import re

def to_ascii(text):
	text = unicodedata.normalize('NFD',text).encode('ascii','ignore').decode()
	return text

def normalize_ascii(text):
	text = text.upper().strip()
	text = to_ascii(text)
	return text

def normalize_text(text):
	text = normalize_ascii(text)
	text = re.sub('[^a-zA-Z0-9]','_',text)
	return text

def normalize_number(text):
	text = re.sub('[^0-9]','',text)
	return text