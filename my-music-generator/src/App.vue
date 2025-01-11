<template>
	<div
		class="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-violet-900 py-12 px-4 sm:px-6 lg:px-8"
	>
		<div class="max-w-4xl mx-auto">
			<!-- Header -->
			<div class="text-center mb-12">
				<h1 class="text-5xl font-bold text-white mb-4 tracking-tight">
					AI Music Generator
				</h1>
				<p class="text-xl text-purple-200">
					Transform your ideas into beautiful melodies
				</p>
			</div>

			<!-- Main Content Card -->
			<div class="bg-white/10 backdrop-blur-lg rounded-2xl p-8 shadow-2xl">
				<!-- Input Form -->
				<div class="space-y-6">
					<div>
						<label class="block text-lg font-medium text-purple-200 mb-2">
							Describe your music
						</label>
						<textarea
							v-model="prompt"
							rows="3"
							class="w-full px-4 py-3 bg-white/5 border border-purple-300/20 rounded-lg text-white placeholder-purple-300/50 focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
							placeholder="E.g., 'A peaceful piano melody with soft strings'"
						/>
					</div>

					<!-- Genre and Mood Selectors -->
					<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
						<div>
							<label class="block text-sm font-medium text-purple-200 mb-2">
								Genre (Optional)
							</label>
							<select
								v-model="genre"
								class="w-full px-4 py-3 bg-white/5 border border-purple-300/20 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							>
								<option value="">Select genre</option>
								<option v-for="g in genres" :key="g" :value="g">{{ g }}</option>
							</select>
						</div>

						<div>
							<label class="block text-sm font-medium text-purple-200 mb-2">
								Mood (Optional)
							</label>
							<select
								v-model="mood"
								class="w-full px-4 py-3 bg-white/5 border border-purple-300/20 rounded-lg text-white focus:ring-2 focus:ring-purple-500 focus:border-transparent"
							>
								<option value="">Select mood</option>
								<option v-for="m in moods" :key="m" :value="m">{{ m }}</option>
							</select>
						</div>
					</div>

					<div>
						<label class="block text-sm font-medium text-purple-200 mb-2">
							Duration: {{ duration }} seconds
						</label>
						<input
							type="range"
							min="5"
							max="30"
							v-model="duration"
							class="w-full"
						/>
					</div>

					<button
						@click="generateMusic"
						:disabled="isGenerating"
						class="w-full py-4 px-6 bg-gradient-to-r from-purple-500 to-indigo-500 hover:from-purple-600 hover:to-indigo-600 text-white text-lg font-semibold rounded-lg shadow-lg transform transition-all duration-200 hover:scale-[1.02] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
					>
						<template v-if="isGenerating">
							<svg
								class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
								xmlns="http://www.w3.org/2000/svg"
								fill="none"
								viewBox="0 0 24 24"
							>
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								></circle>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
								></path>
							</svg>
							Generating...
						</template>
						<template v-else> Generate Music </template>
					</button>
				</div>

				<!-- Audio Player -->
				<div v-if="audioUrl" class="mt-8 p-6 bg-white/5 rounded-lg">
					<div class="flex items-center justify-between mb-4">
						<h3 class="text-lg font-medium text-purple-200">
							Your Generated Music
						</h3>
						<button
							@click="downloadAudio"
							class="text-purple-200 hover:text-white"
							title="Download"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-6 w-6"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
								/>
							</svg>
						</button>
					</div>

					<div class="flex items-center space-x-4">
						<button
							@click="togglePlay"
							class="text-purple-200 hover:text-white"
						>
							<svg
								xmlns="http://www.w3.org/2000/svg"
								class="h-12 w-12"
								fill="none"
								viewBox="0 0 24 24"
								stroke="currentColor"
							>
								<path
									v-if="isPlaying"
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z"
								/>
								<path
									v-else
									stroke-linecap="round"
									stroke-linejoin="round"
									stroke-width="2"
									d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
								/>
							</svg>
						</button>

						<audio
							ref="audioPlayer"
							:src="audioUrl"
							@ended="isPlaying = false"
							class="w-full"
							controls
						/>
					</div>

					<div class="mt-4 text-sm text-purple-300 space-y-1">
						<p>Prompt: {{ prompt }}</p>
						<p v-if="genre">Genre: {{ genre }}</p>
						<p v-if="mood">Mood: {{ mood }}</p>
						<p>Duration: {{ duration }} seconds</p>
					</div>
				</div>

				<!-- Error Message -->
				<div
					v-if="error"
					class="mt-4 p-4 bg-red-500/10 border border-red-500/20 rounded-lg"
				>
					<p class="text-red-400">{{ error }}</p>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from "vue";

// Constants
const genres = [
	"Classical",
	"Jazz",
	"Rock",
	"Electronic",
	"Hip Hop",
	"Ambient",
	"Folk",
	"Pop",
];

const moods = [
	"Happy",
	"Energetic",
	"Calm",
	"Melancholic",
	"Dramatic",
	"Peaceful",
	"Epic",
];

// State
const prompt = ref("");
const duration = ref(10);
const genre = ref("");
const mood = ref("");
const isGenerating = ref(false);
const audioUrl = ref("");
const error = ref("");
const isPlaying = ref(false);
const audioPlayer = ref(null);

// Methods
const generateMusic = async () => {
	if (!prompt.value) {
		error.value = "Please enter a description for your music";
		return;
	}

	try {
		isGenerating.value = true;
		error.value = "";

		const response = await fetch("http://localhost:5000/api/generate", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				prompt: prompt.value,
				duration: duration.value,
				genre: genre.value,
				mood: mood.value,
			}),
		});

		const data = await response.json();

		if (data.error) {
			throw new Error(data.error);
		}

		// Convert base64 to blob and create URL
		const audioData = atob(data.audio);
		const arrayBuffer = new ArrayBuffer(audioData.length);
		const uintArray = new Uint8Array(arrayBuffer);

		for (let i = 0; i < audioData.length; i++) {
			uintArray[i] = audioData.charCodeAt(i);
		}

		const blob = new Blob([arrayBuffer], { type: "audio/wav" });
		const url = URL.createObjectURL(blob);

		// Revoke old URL if it exists
		if (audioUrl.value) {
			URL.revokeObjectURL(audioUrl.value);
		}

		audioUrl.value = url;
	} catch (err) {
		error.value = err.message || "Failed to generate music. Please try again.";
	} finally {
		isGenerating.value = false;
	}
};

const togglePlay = () => {
	if (audioPlayer.value) {
		if (isPlaying.value) {
			audioPlayer.value.pause();
		} else {
			audioPlayer.value.play();
		}
		isPlaying.value = !isPlaying.value;
	}
};

const downloadAudio = () => {
	if (audioUrl.value) {
		const a = document.createElement("a");
		a.href = audioUrl.value;
		a.download = `generated-music-${Date.now()}.wav`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	}
};

// Cleanup
onUnmounted(() => {
	if (audioUrl.value) {
		URL.revokeObjectURL(audioUrl.value);
	}
});
</script>
