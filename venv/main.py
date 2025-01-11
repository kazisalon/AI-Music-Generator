from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import torch
import base64
import io
import scipy.io.wavfile
import numpy as np
from dotenv import load_dotenv
import os
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the model and processor
try:
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
    if torch.cuda.is_available():
        model = model.to("cuda")
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

class AudioGenerator:
    @staticmethod
    def generate(prompt, duration=10, genre=None, mood=None):
        try:
            # Enhance prompt with genre and mood if provided
            enhanced_prompt = prompt
            if genre:
                enhanced_prompt += f" in {genre} style"
            if mood:
                enhanced_prompt += f" with {mood} mood"

            inputs = processor(
                text=[enhanced_prompt],
                padding=True,
                return_tensors="pt",
            )
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}

            # Generate audio
            audio_values = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=True,
                guidance_scale=3.0,
                temperature=0.7
            )

            # Convert to numpy array
            audio_data = audio_values.cpu().numpy().squeeze()
            
            # Normalize audio
            audio_data = np.int16(audio_data * 32767)
            
            # Save to bytes buffer
            buffer = io.BytesIO()
            scipy.io.wavfile.write(buffer, 22050, audio_data)
            buffer.seek(0)
            
            return base64.b64encode(buffer.read()).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

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

        audio_base64 = AudioGenerator.generate(prompt, duration, genre, mood)

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
        logger.error(f"API error: {e}")
        return jsonify({'error': 'Generation failed', 'details': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true')