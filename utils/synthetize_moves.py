from gtts import gTTS
import tqdm

LANG = 'en'


if __name__ == '__main__':

    root = '../data/synthetized_moves/'

    tts = gTTS(text='resign', lang='en')
    tts.save(root + "resign.wav")

    tts = gTTS(text='pass', lang='en')
    tts.save(root + "pass.wav")

    tts = gTTS(text='move', lang='en')
    tts.save(root + "move.wav")

    for letter in tqdm.tqdm('ABCDEFGHJKLMNOPQRST'):
        for i in range(1, 20):
            tts = gTTS(text=f'{letter} {i}', lang=LANG)
            tts.save(root + f"{letter}{i}.wav")
