from gtts import gTTS
import tqdm

LANG = 'en'


if __name__ == '__main__':

    root = '../data/synthesized_moves/'

    tts = gTTS(text='resign', lang='en')
    tts.save(root + "resign.mp3")

    tts = gTTS(text='pass', lang='en')
    tts.save(root + "pass.mp3")

    tts = gTTS(text='move', lang='en')
    tts.save(root + "move.mp3")

    tts = gTTS(text='error', lang='en')
    tts.save(root + "error.mp3")

    tts = gTTS(text='undo', lang='en')
    tts.save(root + "undo.mp3")

    tts = gTTS(text='many colors added', lang='en')
    tts.save(root + "many.mp3")

    tts = gTTS(text='regular move', lang='en')
    tts.save(root + "regular.mp3")

    tts = gTTS(text='stones disappeared', lang='en')
    tts.save(root + "disappeared.mp3")

    tts = gTTS(text='resetting S G F', lang='en')
    tts.save(root + "reset.mp3")

    for letter in tqdm.tqdm('ABCDEFGHJKLMNOPQRST'):
        for i in range(1, 20):
            tts = gTTS(text=f'{letter} {i}', lang=LANG)
            tts.save(root + f"{letter}{i}.mp3")
