import speech_recognition as sr

print("Speak something...")

r = sr.Recognizer()

with sr.Microphone() as source:
    audio = r.listen(source)

try:
    text = r.recognize_google(audio)
    print("You said:", text)

except Exception as e:
    print("Error:", e)