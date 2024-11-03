from flask import Flask, request, jsonify
import asyncio
import requests
from utility.script.script_generator import generate_script
from utility.audio.audio_generator import generate_audio
from utility.captions.timed_captions_generator import generate_timed_captions
from utility.video.background_video_generator import generate_video_url
from utility.render.render_engine import get_output_media
from utility.video.video_search_query_generator import getVideoSearchQueriesTimed, merge_empty_intervals

app = Flask(__name__)

@app.route('/generate-video', methods=['POST'])
def generate_video():
    data = request.get_json()
    topic = data.get("topic")
    if not topic:
        return jsonify({"error": "Topic is required"}), 400

    try:
        SAMPLE_FILE_NAME = "audio_tts.wav"
        VIDEO_SERVER = "pexel"

        # Processamento do script
        response = generate_script(topic)
        print("script:", response)

        # Gerar áudio
        asyncio.run(generate_audio(response, SAMPLE_FILE_NAME))

        # Gerar legendas
        timed_captions = generate_timed_captions(SAMPLE_FILE_NAME)
        print(timed_captions)

        # Gerar URLs dos vídeos de fundo
        search_terms = getVideoSearchQueriesTimed(response, timed_captions)
        background_video_urls = generate_video_url(search_terms, VIDEO_SERVER) if search_terms else []
        background_video_urls = merge_empty_intervals(background_video_urls)

        # Renderizar o vídeo final
        if background_video_urls:
            video = get_output_media(SAMPLE_FILE_NAME, timed_captions, background_video_urls, VIDEO_SERVER)
            return jsonify({"message": "Video generated", "video_url": video})
        else:
            return jsonify({"message": "No background video available"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# Código para enviar requisição para a API
def send_video_request(topic):
    url = "http://localhost:5000/generate-video"  # Altere para a URL correta se estiver em produção
    payload = {
        "topic": topic
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print("Video URL:", data.get("video_url"))
    else:
        print("Error:", response.json().get("error"))

# Exemplo de uso
# send_video_request("seu_tópico_desejado")
