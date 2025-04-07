import os
import wave
import subprocess
import ffmpeg
from flask import Flask, request, jsonify
from coqui_stt import Model

app = Flask(__name__)
model_path = "models/coqui"  # Path to Coqui model
model = Model(model_path)

@app.route("/transcribe", methods=["POST"])
def transcribe():
    # Lấy file âm thanh từ form
    audio_file = request.files["audio_data"]
    audio_path = "temp_audio_input"
    
    # Lưu file âm thanh gốc
    audio_file.save(audio_path)

    # Chuyển đổi file âm thanh sang định dạng WAV, mono, 16-bit PCM, 16000Hz
    converted_audio_path = "temp_audio.wav"
    try:
        # Sử dụng ffmpeg để chuyển đổi định dạng và lấy audio với các thông số yêu cầu
        ffmpeg.input(audio_path).output(converted_audio_path, ac=1, ar='16000', format='wav').run()
    except ffmpeg.Error as e:
        return jsonify({"error": f"Không thể chuyển đổi file: {str(e)}"}), 400
    
    # Xử lý file âm thanh WAV đã chuyển đổi
    try:
        wf = wave.open(converted_audio_path, "rb")
        
        if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getframerate() != 16000:
            return jsonify({"error": "Audio phải là WAV, mono, 16-bit PCM, 16000Hz"}), 400
        
        # Thực hiện nhận diện giọng nói
        rec = model.stt(wf.readframes(wf.getnframes()))
        os.remove(audio_path)  # Xóa file âm thanh gốc
        os.remove(converted_audio_path)  # Xóa file WAV sau khi xử lý

        return jsonify({"text": rec})
    except Exception as e:
        return jsonify({"error": f"Xảy ra lỗi khi nhận diện giọng nói: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
