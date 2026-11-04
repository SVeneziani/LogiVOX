#!/usr/bin/env python3
import subprocess, tempfile
from pathlib import Path

OUT = Path('audio_it')
OUT.mkdir(exist_ok=True)

words = {
    0:'zero', 1:'uno', 2:'due', 3:'tre', 4:'quattro', 5:'cinque',
    6:'sei', 7:'sette', 8:'otto', 9:'nove', 10:'dieci', 11:'undici',
    12:'dodici', 13:'tredici', 14:'quattordici', 15:'quindici',
    16:'sedici', 17:'diciassette', 18:'diciotto', 19:'diciannove',
    20:'venti', 30:'trenta', 40:'quaranta', 50:'cinquanta',
    60:'sessanta', 70:'settanta', 80:'ottanta', 90:'novanta',
    100:'cento', 200:'duecento', 300:'trecento', 400:'quattrocento',
    500:'cinquecento', 600:'seicento', 700:'settecento',
    800:'ottocento', 900:'novecento',
}

units = {1:'uno',2:'due',3:'tre',4:'quattro',5:'cinque',6:'sei',7:'sette',8:'otto',9:'nove'}
tens = {20:'venti',30:'trenta',40:'quaranta',50:'cinquanta',60:'sessanta',70:'settanta',80:'ottanta',90:'novanta'}
for base, ten_word in tens.items():
    for unit, unit_word in units.items():
        # Italian drops the final vowel before uno and otto.
        joiner = ten_word[:-1] if unit in (1, 8) else ten_word
        words[base + unit] = joiner + unit_word
other = {
    'AMPERES':'ampere', 'DEGREES':'gradi', 'FARADS':'farad',
    'HERTZ':'hertz', 'KILO':'chilo', 'MEGA':'mega', 'MICRO':'micro',
    'MILLI':'milli', 'MINUS':'meno', 'NANO':'nano', 'OHMS':'ohm',
    'OUT_OF_RANGE':'fuori scala', 'OPEN':'circuito aperto', 'PICO':'pico', 'POINT':'virgola',
    'VOLTS':'volt', 'ZERO':'zero', 'no_info':'misura non disponibile',
    'reset':'sistema pronto',
    'shutdown':'spegnimento in corso',
    'auto_on':'lettura automatica attiva',
    'auto_off':'lettura automatica disattivata',
}

def make(name, text):
    with tempfile.TemporaryDirectory() as td:
        aiff = Path(td) / 'voice.aiff'
        # `--` forces macOS say to treat the phrase as text, even when it
        # contains punctuation or begins with a dash.
        subprocess.run(['say', '-v', 'Alice', '-o', str(aiff), '--', text], check=True)
        if aiff.stat().st_size <= 4096:
            raise RuntimeError(f'Voce vuota per {name}: {text!r}')
        subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@16000', '-c', '1',
                        str(aiff), str(OUT / f'{name}.wav')], check=True)

if __name__ == '__main__':
    for number, text in words.items():
        make(str(number), text)
    for name, text in other.items():
        make(name, text)
    print(f'Create {len(words)+len(other)} tracce in {OUT}/')
