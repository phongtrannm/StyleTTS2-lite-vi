---
license: mit
datasets:
- capleaf/viVoice
language:
- vi
- en
base_model:
- yl4579/StyleTTS2-LibriTTS
pipeline_tag: text-to-speech
---

# StyleTTS 2 - lite


> A lightweight, efficient variation of the StyleTTS 2 text‐to‐speech model, optimized for rapid integration into your applications. With a compact 90 million parameter footprint and built‐in speaker‑and‑language tagging, you can seamlessly switch voices and languages even within a single sentence.

## Online Demo  
Explore the model on Hugging Face Spaces:  
https://huggingface.co/spaces/styletts2/styletts2


## Training Details  

1. **Base Checkpoint:**  
   - Initialized from the official StyleTTS 2 LibriTTS weights.  
2. **Token Extension:**  
   - Expanded the token set to 189 symbols to ensure full Vietnamese IPA compatibility.  
3. **Training Data:**  
   - **FonosVietnam**  (extracted from the viVoice corpus)  
   - **VoizFM** (extracted from the viVoice corpus)  
4. **Training Schedule:**  
   - Trained for 120 000 steps.

## Model Architecture

| Component      | Parameters    |
| -------------- | ------------- |
| Decoder        | 54 ,289 ,492  |
| Predictor      | 16 ,194 ,612  |
| Text Encoder   | 56 ,120 ,320  |
| Style Encoder  | 13 ,845 ,440  |
| **Total**      | **89 ,941 ,576** |


##  Prerequisites  

- **Python:** Version 3.7 or higher  
- **Git:** To clone the repository  

## Installation & Setup 

1. Clone the repository

```bash

git  clone  https://huggingface.co/dangtr0408/StyleTTS2-lite-vi

cd  StyleTTS2-lite-vi

```

2. Install dependencies:

```bash

pip  install  -r  requirements.txt

```

  

3. On **Linux**, manually install espeak:

```bash

sudo  apt-get  install  espeak-ng

```

## Usage Example


## Fine-tune

COMING SOON (gotta clean the code) 

## Disclaimer  

***Before using these pre-trained models, you agree to inform the listeners that the speech samples are synthesized by the pre-trained models, unless you have the permission to use the voice you synthesize. That is, you agree to only use voices whose speakers grant the permission to have their voice cloned, either directly or by license before making synthesized voices public, or you have to publicly announce that these voices are synthesized if you do not have the permission to use these voices.***


## References

- [yl4579/StyleTTS2](https://arxiv.org/abs/2306.07691)

- [jik876/hifi-gan](https://github.com/jik876/hifi-gan)

- [capleaf/viVoice](https://huggingface.co/datasets/capleaf/viVoice)

## License

**Code: MIT License**

**Model: CC-BY-NC-SA-4.0**