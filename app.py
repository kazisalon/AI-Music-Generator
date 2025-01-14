
# utils.py
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import numpy as np
import io
import scipy.io.wavfile
import base64

class MusicGenerator:
    def __init__(self):
        self.processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        self.model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
        if torch.cuda.is_available():
            self.model = self.model.to("cuda")

    def generate(self, prompt, duration=10, genre=None, mood=None):
        # Enhance prompt with genre and mood if provided
        enhanced_prompt = prompt
        if genre:
            enhanced_prompt += f" in {genre} style"
        if mood:
            enhanced_prompt += f" with {mood} mood"

        # Process input
        inputs = self.processor(
            text=[enhanced_prompt],
            padding=True,
            return_tensors="pt",
        )
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}

        # Generate audio
        audio_values = self.model.generate(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            guidance_scale=3.0,
            temperature=0.7
        )

        # Process output
        audio_data = audio_values.cpu().numpy().squeeze()
        audio_data = np.int16(audio_data * 32767)
        
        # Convert to WAV format
        buffer = io.BytesIO()
        scipy.io.wavfile.write(buffer, 22050, audio_data)
        buffer.seek(0)
        
        return base64.b64encode(buffer.read()).decode('utf-8')

# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from utils import MusicGenerator
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize music generator
generator = MusicGenerator()

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/generate', methods=['POST'])
def generate_music():
    try:
        data = request.json
        prompt = data.get('prompt')
        duration = int(data.get('duration', 10))
        genre = data.get('genre')
        mood = data.get('mood')

        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if duration < 5 or duration > 30:
            return jsonify({'error': 'Duration must be between 5 and 30 seconds'}), 400

        audio_base64 = generator.generate(prompt, duration, genre, mood)

        return jsonify({
            'success': True,
            'audio': audio_base64,
            'metadata': {
                'prompt': prompt,
                'duration': duration,
                'genre': genre,
                'mood': mood,
                'timestamp': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')