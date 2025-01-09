// App.vue
<template>
	<main class="app">
		<div class="container">
			<h1>AI Music Generator</h1>

			<div class="form-group">
				<label>Genre</label>
				<select v-model="genre">
					<option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
				</select>
			</div>

			<div class="form-group">
				<label>Mood</label>
				<select v-model="mood">
					<option v-for="m in moods" :key="m" :value="m">{{ m }}</option>
				</select>
			</div>

			<div class="form-group">
				<label>Tempo: {{ tempo }} BPM</label>
				<input type="range" v-model="tempo" min="60" max="180" />
			</div>

			<div class="form-group">
				<label>Hugging Face API Key</label>
				<input type="password" v-model="apiKey" />
			</div>

			<button
				@click="generateMusic"
				:disabled="isGenerating"
				class="generate-btn"
			>
				{{ isGenerating ? "Generating..." : "Generate Music" }}
			</button>

			<audio v-if="audioUrl" controls :src="audioUrl"></audio>
			<div v-if="error" class="error">{{ error }}</div>
		</div>
	</main>
</template>

<script>
import axios from "axios";

export default {
	name: "App",
	data() {
		return {
			genres: ["Classical", "Jazz", "Rock", "Electronic"],
			moods: ["Happy", "Sad", "Energetic", "Calm"],
			genre: "Classical",
			mood: "Happy",
			tempo: 120,
			apiKey: "",
			audioUrl: null,
			isGenerating: false,
			error: null,
		};
	},
	methods: {
		async generateMusic() {
			if (!this.apiKey) {
				this.error = "Please enter an API key";
				return;
			}

			this.isGenerating = true;
			this.error = null;

			try {
				const response = await axios.post(
					"https://api-inference.huggingface.co/models/facebook/musicgen-small",
					{
						inputs: `Generate a ${this.mood.toLowerCase()} ${this.genre.toLowerCase()} piece at ${
							this.tempo
						} BPM`,
					},
					{
						headers: {
							Authorization: `Bearer ${this.apiKey}`,
						},
						responseType: "blob",
					}
				);

				this.audioUrl = URL.createObjectURL(response.data);
			} catch (err) {
				this.error = "Error generating music. Please try again.";
				console.error(err);
			} finally {
				this.isGenerating = false;
			}
		},
	},
};
</script>

<style>
* {
	margin: 0;
	padding: 0;
	box-sizing: border-box;
}

.app {
	min-height: 100vh;
	background: #f5f5f5;
	padding: 20px;
}

.container {
	max-width: 600px;
	margin: 0 auto;
	padding: 20px;
	background: white;
	border-radius: 8px;
	box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

h1 {
	text-align: center;
	color: #333;
	margin-bottom: 30px;
}

.form-group {
	margin-bottom: 20px;
}

label {
	display: block;
	margin-bottom: 8px;
	font-weight: bold;
	color: #555;
}

select,
input[type="password"] {
	width: 100%;
	padding: 10px;
	border: 1px solid #ddd;
	border-radius: 4px;
	font-size: 16px;
}

input[type="range"] {
	width: 100%;
	margin: 10px 0;
}

.generate-btn {
	width: 100%;
	padding: 12px;
	background: #4caf50;
	color: white;
	border: none;
	border-radius: 4px;
	font-size: 16px;
	cursor: pointer;
	transition: background 0.3s;
}

.generate-btn:hover {
	background: #45a049;
}

.generate-btn:disabled {
	background: #cccccc;
	cursor: not-allowed;
}

audio {
	width: 100%;
	margin-top: 20px;
}

.error {
	color: #ff0000;
	margin-top: 10px;
	text-align: center;
}
</style>
