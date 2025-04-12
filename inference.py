import numpy as np
import torch

import yaml
from munch import Munch
import unicodedata
import re
import torchaudio

from nltk.tokenize import word_tokenize
import nltk
nltk.download('punkt_tab')

import librosa
import noisereduce as nr

from models import ProsodyPredictor, TextEncoder, StyleEncoder
from Modules.hifigan import Decoder


import phonemizer

# For windows bro
# from phonemizer.backend.espeak.wrapper import EspeakWrapper
# import espeakng_loader
# EspeakWrapper.set_library(espeakng_loader.get_library_path())

def espeak_phn(text, lang):
    try:
        my_phonemizer = phonemizer.backend.EspeakBackend(language=lang, preserve_punctuation=True,  with_stress=True, language_switch='remove-flags')
        return my_phonemizer.phonemize([text])[0]
    except Exception as e:
        print(e)

# IPA Phonemizer: https://github.com/bootphon/phonemizer
# Total including extend chars 187

_pad = "$"
_punctuation = ';:,.!?¡¿—…"«»“” '
_letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
_letters_ipa = "ɑɐɒæɓʙβɔɕçɗɖðʤəɘɚɛɜɝɞɟʄɡɠɢʛɦɧħɥʜɨɪʝɭɬɫɮʟɱɯɰŋɳɲɴøɵɸθœɶʘɹɺɾɻʀʁɽʂʃʈʧʉʊʋⱱʌɣɤʍχʎʏʑʐʒʔʡʕʢǀǁǂǃˈˌːˑʼʴʰʱʲʷˠˤ˞↓↑→↗↘'̩'ᵻ"
_extend = "∫̆ăη͡123456"

# Export all symbols:
symbols = [_pad] + list(_punctuation) + list(_letters) + list(_letters_ipa) + list(_extend)

dicts = {}
for i in range(len((symbols))):
    dicts[symbols[i]] = i

class TextCleaner:
    def __init__(self, dummy=None):
        self.word_index_dictionary = dicts
        #print(len(dicts))
    def __call__(self, text):
        indexes = []
        for char in text:
            try:
                indexes.append(self.word_index_dictionary[char])
            except KeyError as e:
                #print(char)
                continue
        return indexes

class Preprocess:
    def __text_normalize(self, text):
        punctuation = ["，", "、", "،", ";", "(", "．", "。", "…", "!", "–", ":"]
        map_to = "."
        punctuation_pattern = re.compile(f"[{''.join(re.escape(p) for p in punctuation)}]")
        #ensure consistency.
        text = unicodedata.normalize('NFKC', text)
        #replace punctuation that acts like a comma or period
        #text = re.sub(r'\.{2,}', '.', text)
        text = punctuation_pattern.sub(map_to, text)
        #remove or replace special chars except . , { } ? ' -  \ % $ & /
        text = re.sub(r'[^\w\s.,{}?\'\-\[\]\%\$\&\/]', ' ', text)
        #replace consecutive whitespace chars with a single space and strip leading/trailing spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    def __merge_fragments(self, texts, n):
        merged = []
        i = 0
        while i < len(texts):
            fragment = texts[i]
            j = i + 1
            while len(fragment.split()) < n and j < len(texts):
                fragment += ", " + texts[j]
                j += 1
            merged.append(fragment)
            i = j
        if len(merged[-1].split()) < n and len(merged) > 1: #handle last sentence
            merged[-2] = merged[-2] + ", " + merged[-1]
            del merged[-1]
        else:
            merged[-1] = merged[-1]
        return merged
    def wave_preprocess(self, wave):
        to_mel = torchaudio.transforms.MelSpectrogram(n_mels=80, n_fft=2048, win_length=1200, hop_length=300)
        mean, std = -4, 4
        wave_tensor = torch.from_numpy(wave).float()
        mel_tensor = to_mel(wave_tensor)
        mel_tensor = (torch.log(1e-5 + mel_tensor.unsqueeze(0)) - mean) / std
        return mel_tensor
    def text_preprocess(self, text, n_merge=12):
        text_norm = self.__text_normalize(text).replace(",", ".").split(".")#split.
        text_norm = [s.strip() for s in text_norm]
        text_norm = list(filter(lambda x: x != '', text_norm)) #filter empty index
        text_norm = self.__merge_fragments(text_norm, n=n_merge) #merge if a sentence has less that n 
        return text_norm
    def length_to_mask(self, lengths):
        mask = torch.arange(lengths.max()).unsqueeze(0).expand(lengths.shape[0], -1).type_as(lengths)
        mask = torch.gt(mask+1, lengths.unsqueeze(1))
        return mask

#For inference only
class StyleTTS2(torch.nn.Module):
    def __init__(self, config_path, models_path):
        super().__init__()
        self.register_buffer("get_device", torch.empty(0))
        self.preprocess = Preprocess()

        config = yaml.safe_load(open(config_path))
        args = self.__recursive_munch(config['model_params'])

        assert args.decoder.type in ['hifigan'], 'Decoder type unknown'

        self.decoder            = Decoder(dim_in=args.hidden_dim, style_dim=args.style_dim, dim_out=args.n_mels,
                                        resblock_kernel_sizes = args.decoder.resblock_kernel_sizes,
                                        upsample_rates = args.decoder.upsample_rates,
                                        upsample_initial_channel=args.decoder.upsample_initial_channel,
                                        resblock_dilation_sizes=args.decoder.resblock_dilation_sizes,
                                        upsample_kernel_sizes=args.decoder.upsample_kernel_sizes)
        self.predictor           = ProsodyPredictor(style_dim=args.style_dim, d_hid=args.hidden_dim, nlayers=args.n_layer, max_dur=args.max_dur, dropout=args.dropout)
        self.text_encoder        = TextEncoder(channels=args.hidden_dim, kernel_size=5, depth=args.n_layer, n_symbols=args.n_token)
        self.style_encoder       = StyleEncoder(dim_in=args.dim_in, style_dim=args.style_dim, max_conv_dim=args.hidden_dim)# acoustic style encoder

        self.__load_models(models_path)

        self.ref_s_speakers = None
        self.speakers = None
    
    def __recursive_munch(self, d):
        if isinstance(d, dict):
            return Munch((k, self.__recursive_munch(v)) for k, v in d.items())
        elif isinstance(d, list):
            return [self.__recursive_munch(v) for v in d]
        else:
            return d
        
    def __init_replacement_func(self, replacements):
        replacement_iter = iter(replacements)
        def replacement(match):
            return next(replacement_iter)
        return replacement
        
    def __load_models(self, models_path):
        module_params = []
        model = {'decoder':self.decoder, 'predictor':self.predictor, 'text_encoder':self.text_encoder, 'style_encoder':self.style_encoder}

        params_whole = torch.load(models_path, map_location='cpu')
        params = params_whole['net']
        params = {key: value for key, value in params.items() if key in model.keys()}

        for key in model:
            try:
                model[key].load_state_dict(params[key])
            except:
                from collections import OrderedDict
                state_dict = params[key]
                new_state_dict = OrderedDict()
                for k, v in state_dict.items():
                    name = k[7:] # remove `module.`
                    new_state_dict[name] = v
                model[key].load_state_dict(new_state_dict, strict=False)

            total_params = sum(p.numel() for p in model[key].parameters())
            print(key,":",total_params)
            module_params.append(total_params)

        print('\nTotal',":",sum(module_params))

    def __compute_style(self, path, denoise, split_dur):
        device = self.get_device.device
        denoise = min(denoise, 1)
        if split_dur != 0: split_dur = max(int(split_dur), 1)
        max_samples = 24000*30 #max 30 seconds ref audio
        print("Computing the style for:", path)
        
        wave, sr = librosa.load(path, sr=24000)
        audio, index = librosa.effects.trim(wave, top_db=30)
        if sr != 24000:
            audio = librosa.resample(audio, sr, 24000)
        if len(audio) > max_samples:
            audio = audio[:max_samples]
        
        if denoise > 0.0:
            audio_denoise = nr.reduce_noise(y=audio, sr=sr, n_fft=2048, win_length=1200, hop_length=300)
            audio = audio*(1-denoise) + audio_denoise*denoise

        with torch.no_grad():
            if split_dur>0 and len(audio)/sr>split_dur:
                #This option will split the ref audio to multiple parts, calculate styles and average them
                count = 0
                ref_s = None
                jump = sr*split_dur
                total_len = len(audio)
                
                #Need to init before the loop
                mel_tensor = self.preprocess.wave_preprocess(audio[0:jump]).to(device)
                ref_s = self.style_encoder(mel_tensor.unsqueeze(1))
                count += 1
                for i in range(jump, total_len, jump):
                    if i+jump >= total_len:
                        left_dur = (total_len-i)/sr
                        if left_dur >= 0.5: #Still count if left over dur is >= 0.5s
                            mel_tensor = self.preprocess.wave_preprocess(audio[i:total_len]).to(device)
                            ref_s += self.style_encoder(mel_tensor.unsqueeze(1))
                            count += 1
                        continue
                    mel_tensor = self.preprocess.wave_preprocess(audio[i:i+jump]).to(device)
                    ref_s += self.style_encoder(mel_tensor.unsqueeze(1))
                    count += 1
                ref_s /= count
            else:
                mel_tensor = self.preprocess.wave_preprocess(audio).to(device)
                ref_s = self.style_encoder(mel_tensor.unsqueeze(1))

        return ref_s
        
    def __inference(self, phonem, ref_s, speed=1, prev_d_mean=0, t=0.1):
        device = self.get_device.device
        speed = min(max(speed, 0.0001), 2) #speed range [0, 2]
        
        phonem = ' '.join(word_tokenize(phonem))
        tokens = TextCleaner()(phonem)
        tokens.insert(0, 0)
        tokens.append(0)
        tokens = torch.LongTensor(tokens).to(device).unsqueeze(0)
        
        with torch.no_grad():
            input_lengths = torch.LongTensor([tokens.shape[-1]]).to(device)
            text_mask = self.preprocess.length_to_mask(input_lengths).to(device)

            # encode
            t_en = self.text_encoder(tokens, input_lengths, text_mask)
            s = ref_s.to(device)
        
            # cal alignment
            d = self.predictor.text_encoder(t_en, s, input_lengths, text_mask)
            x, _ = self.predictor.lstm(d)
            duration = self.predictor.duration_proj(x) / speed
            duration = torch.sigmoid(duration).sum(axis=-1)

            if prev_d_mean != 0:#Stabilize speaking speed
                dur_stats = torch.empty(duration.shape).normal_(mean=prev_d_mean, std=duration.std()).to(device)
            else:
                dur_stats = torch.empty(duration.shape).normal_(mean=duration.mean(), std=duration.std()).to(device)
            duration = duration*(1-t) + dur_stats*t
                
            pred_dur = torch.round(duration.squeeze()).clamp(min=1)
            pred_aln_trg = torch.zeros(input_lengths, int(pred_dur.sum().data))
            c_frame = 0
            for i in range(pred_aln_trg.size(0)):
                pred_aln_trg[i, c_frame:c_frame + int(pred_dur[i].data)] = 1
                c_frame += int(pred_dur[i].data)
            alignment = pred_aln_trg.unsqueeze(0).to(device)

            # encode prosody
            en = (d.transpose(-1, -2) @ alignment)
            F0_pred, N_pred = self.predictor.F0Ntrain(en, s)
            asr = (t_en @ pred_aln_trg.unsqueeze(0).to(device))

            out = self.decoder(asr, F0_pred, N_pred, s)
        
        return out.squeeze().cpu().numpy(), duration.mean()
    
    def __get_styles(self, speakers, denoise, split_dur):
        self.ref_s_speakers = {}
        self.speakers = speakers
        for id in speakers:
            ref_s = self.__compute_style(speakers[id]['path'], denoise=denoise, split_dur=split_dur)
            self.ref_s_speakers[id] = ref_s

    def generate(self, text, speakers, avg_style=False, stabilize=False, denoise=0.3, n_merge=14, default_speaker= "[id_1]"):
        if avg_style:   split_dur = 3
        else:           split_dur = 0

        if stabilize:   smooth_dur=0.2
        else:           smooth_dur=0    

        self.__get_styles(speakers, denoise, split_dur)
        
        list_wav        = []
        prev_d_mean     = 0
        lang_pattern    = r'\[([^\]]+)\]\{([^}]+)\}'

        text = re.sub(r'[\n\r\t\f\v]', '', text)
        #fix lang tokens span to multiple sents
        find_lang_tokens = re.findall(lang_pattern, text)
        if find_lang_tokens:
            cus_text = []
            for lang, t in find_lang_tokens:
                parts = self.preprocess.text_preprocess(t, n_merge=0)
                parts = ".".join([f"[{lang}]" + f"{{{p}}}"for p in parts])
                cus_text.append(parts)
            replacement_func = self.__init_replacement_func(cus_text)
            text = re.sub(lang_pattern, replacement_func, text)

        texts = re.split(r'(\[id_\d+\])', text) #split the text by speaker ids while keeping the ids.
        if len(texts) <= 1:
            texts.insert(0, default_speaker)
        texts = list(filter(lambda x: x != '', texts))

        print("Generating Audio...")
        for i in texts:
            if bool(re.match(r'(\[id_\d+\])', i)):
                #Set up env for matched speaker
                speaker_id = i.strip('[]')
                current_ref_s = self.ref_s_speakers[speaker_id]
                speed = self.speakers[speaker_id]['speed']
                continue
            text_norm = self.preprocess.text_preprocess(i, n_merge=n_merge)
            for sentence in text_norm:
                cus_phonem = []
                find_lang_tokens = re.findall(lang_pattern, sentence)
                if find_lang_tokens:
                    for lang, t in find_lang_tokens:
                        try:
                            phonem = espeak_phn(t, lang)
                            cus_phonem.append(phonem)
                        except Exception as e:
                            print(e)
                        
                replacement_func = self.__init_replacement_func(cus_phonem)
                phonem =  espeak_phn(sentence, self.speakers[speaker_id]['lang'])
                phonem = re.sub(lang_pattern, replacement_func, phonem)

                wav, prev_d_mean = self.__inference(phonem, current_ref_s, speed=speed, prev_d_mean=prev_d_mean, t=smooth_dur)
                wav = wav[4000:-4000] #Remove weird pulse and silent tokens
                list_wav.append(wav)
        
        final_wav = np.concatenate(list_wav)
        final_wav = np.concatenate([np.zeros([12000]), final_wav, np.zeros([12000])], axis=0) # 0.5 second padding
        return final_wav