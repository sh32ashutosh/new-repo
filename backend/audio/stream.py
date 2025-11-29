import pyaudio
from flask import Flask, Response, request, jsonify
import audioop

app = Flask(__name__)

# Global settings (will be changed via UI)
current_settings = {
    'rate': 44100,
    'chunk': 2048,
    'channels': 1,
    'volume': 1.0,
    'device': None
}

def get_audio_devices():
    p = pyaudio.PyAudio()
    devices = []
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:
            devices.append({
                'index': i,
                'name': info['name'],
                'channels': info['maxInputChannels'],
                'rate': int(info['defaultSampleRate'])
            })
    p.terminate()
    return devices

def gen_wav_header(sample_rate, bits_per_sample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF", 'ascii')
    o += (datasize + 36).to_bytes(4, 'little')
    o += bytes("WAVE", 'ascii')
    o += bytes("fmt ", 'ascii')
    o += (16).to_bytes(4, 'little')
    o += (1).to_bytes(2, 'little')
    o += (channels).to_bytes(2, 'little')
    o += (sample_rate).to_bytes(4, 'little')
    o += (sample_rate * channels * bits_per_sample // 8).to_bytes(4, 'little')
    o += (channels * bits_per_sample // 8).to_bytes(2, 'little')
    o += (bits_per_sample).to_bytes(2, 'little')
    o += bytes("data", 'ascii')
    o += (datasize).to_bytes(4, 'little')
    return o

def audio_stream():
    rate = int(current_settings['rate'])
    chunk = int(current_settings['chunk'])
    channels = int(current_settings['channels'])
    volume = float(current_settings['volume'])
    device = current_settings['device']
    
    print(f"\n=== Starting Stream ===")
    print(f"Device: {device}")
    print(f"Rate: {rate}, Channels: {channels}, Chunk: {chunk}, Volume: {volume}x")
    
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=device,
            frames_per_buffer=chunk
        )
        
        # Send WAV header
        yield gen_wav_header(rate, 16, channels)
        
        count = 0
        while True:
            data = stream.read(chunk, exception_on_overflow=False)
            
            # Apply volume
            if volume != 1.0:
                data = audioop.mul(data, 2, volume)
            
            count += 1
            if count % 100 == 0:
                rms = audioop.rms(data, 2)
                print(f"RMS: {rms}")
            
            yield data
            
    except Exception as e:
        print(f"Stream error: {e}")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

@app.route('/')
def index():
    devices = get_audio_devices()
    return f"""
<html>
<head>
    <title>Audio Stream Tester</title>
    <style>
        body {{ font-family: Arial; margin: 20px; }}
        .control {{ margin: 15px 0; }}
        label {{ display: inline-block; width: 150px; font-weight: bold; }}
        input[type=range] {{ width: 300px; }}
        select {{ width: 400px; padding: 5px; }}
        button {{ padding: 10px 20px; font-size: 16px; margin: 10px 5px; }}
        .value {{ display: inline-block; width: 80px; text-align: right; }}
        #log {{ margin-top: 20px; padding: 10px; background: #f0f0f0; height: 150px; overflow-y: auto; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <h1>Audio Stream Configuration Tester</h1>
    
    <div class="control">
        <label>Device:</label>
        <select id="device">
            {''.join(f'<option value="{d["index"]}">{d["name"]} ({d["rate"]}Hz, {d["channels"]}ch)</option>' for d in devices)}
        </select>
    </div>
    
    <div class="control">
        <label>Sample Rate:</label>
        <select id="rate">
            <option value="8000">8000 Hz</option>
            <option value="11025">11025 Hz</option>
            <option value="16000">16000 Hz</option>
            <option value="22050">22050 Hz</option>
            <option value="44100" selected>44100 Hz</option>
            <option value="48000">48000 Hz</option>
        </select>
    </div>
    
    <div class="control">
        <label>Chunk Size:</label>
        <input type="range" id="chunk" min="512" max="8192" step="512" value="2048">
        <span class="value" id="chunk_val">2048</span>
    </div>
    
    <div class="control">
        <label>Channels:</label>
        <select id="channels">
            <option value="1" selected>1 (Mono)</option>
            <option value="2">2 (Stereo)</option>
        </select>
    </div>
    
    <div class="control">
        <label>Volume Boost:</label>
        <input type="range" id="volume" min="0.1" max="5.0" step="0.1" value="1.0">
        <span class="value" id="volume_val">1.0x</span>
    </div>
    
    <button onclick="applySettings()">APPLY SETTINGS</button>
    <button onclick="startStream()">START STREAM</button>
    <button onclick="stopStream()">STOP</button>
    
    <div>
        <audio id="player" controls></audio>
    </div>
    
    <div id="log"></div>
    
    <script>
    let audio = document.getElementById('player');
    
    // Update value displays
    document.getElementById('chunk').oninput = function() {{
        document.getElementById('chunk_val').textContent = this.value;
    }};
    document.getElementById('volume').oninput = function() {{
        document.getElementById('volume_val').textContent = this.value + 'x';
    }};
    
    function log(msg) {{
        let logDiv = document.getElementById('log');
        logDiv.innerHTML += new Date().toLocaleTimeString() + ': ' + msg + '<br>';
        logDiv.scrollTop = logDiv.scrollHeight;
        console.log(msg);
    }}
    
    function applySettings() {{
        let settings = {{
            device: parseInt(document.getElementById('device').value),
            rate: parseInt(document.getElementById('rate').value),
            chunk: parseInt(document.getElementById('chunk').value),
            channels: parseInt(document.getElementById('channels').value),
            volume: parseFloat(document.getElementById('volume').value)
        }};
        
        fetch('/settings', {{
            method: 'POST',
            headers: {{'Content-Type': 'application/json'}},
            body: JSON.stringify(settings)
        }})
        .then(r => r.json())
        .then(data => {{
            log('Settings applied: ' + JSON.stringify(settings));
        }});
    }}
    
    function startStream() {{
        stopStream();
        log('Starting stream...');
        audio.src = '/stream?t=' + Date.now();
        audio.load();
        audio.play()
            .then(() => log('Stream started'))
            .catch(err => log('ERROR: ' + err));
    }}
    
    function stopStream() {{
        audio.pause();
        audio.src = '';
        log('Stream stopped');
    }}
    
    audio.addEventListener('error', (e) => {{
        log('Audio error: ' + (e.target.error ? e.target.error.message : 'unknown'));
    }});
    
    // Apply initial settings
    applySettings();
    </script>
</body>
</html>
"""

@app.route('/settings', methods=['POST'])
def update_settings():
    global current_settings
    data = request.json
    current_settings.update(data)
    print(f"Settings updated: {current_settings}")
    return jsonify({'status': 'ok', 'settings': current_settings})

@app.route('/stream')
def stream_wav():
    return Response(audio_stream(), mimetype="audio/wav")

if __name__ == "__main__":
    print("Starting Audio Stream Tester on http://0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000, threaded=True)
