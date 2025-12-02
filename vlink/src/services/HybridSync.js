// THE ZERO TOLERANCE ENGINE
// Synchronizes Audio Blobs with Vector Data

export class HybridSyncEngine {
    constructor(socket, classId) {
        this.socket = socket;
        this.classId = classId;
        
        // Broadcast State
        this.mediaRecorder = null;
        this.vectorQueue = []; // Holds drawings waiting for next audio chunk
        this.sequence = 0;
        this.isBroadcasting = false;

        // Playback State
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        this.jitterBuffer = [];
        this.isPlaying = false;
        this.startTime = 0;
        this.bufferDelay = 300; // ms (Jitter Buffer target)
        
        // Callbacks
        this.onRemoteVector = null; // Function to draw on canvas
    }

    // --- BROADCASTER (TEACHER) ---

    startBroadcasting(stream) {
        if (this.isBroadcasting) return;
        this.isBroadcasting = true;
        this.sequence = 0;

        // 1. Setup MediaRecorder for small chunks
        // Chrome supports ~100ms timeslices well. 
        // For <50ms (Zero Tolerance), we might need AudioWorklets, but this is solid for LAN.
        const options = { mimeType: 'audio/webm;codecs=opus' };
        try {
            this.mediaRecorder = new MediaRecorder(stream, options);
        } catch (e) {
            console.error("MediaRecorder Error:", e);
            return;
        }

        this.mediaRecorder.ondataavailable = async (e) => {
            if (e.data.size > 0) {
                await this.sendPacket(e.data);
            }
        };

        // Start slicing every 100ms
        this.mediaRecorder.start(100);
    }

    stopBroadcasting() {
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        this.isBroadcasting = false;
        this.vectorQueue = [];
    }

    // Called by Whiteboard whenever user draws
    enqueueVector(tool, x, y, color, mode) {
        // Format: [[x,y], color, mode]
        this.vectorQueue.push([[x, y], color, mode]);
    }

    async sendPacket(audioBlob) {
        if (!this.socket) return;

        // 1. Snapshot current vectors and clear queue
        const currentVectors = [...this.vectorQueue];
        this.vectorQueue = [];

        // 2. Convert Blob to Buffer for cleaner transport
        const arrayBuffer = await audioBlob.arrayBuffer();

        // 3. Construct Payload
        const payload = {
            class_id: this.classId,
            seq: this.sequence++,
            ts: Date.now(),
            audio: arrayBuffer, 
            vectors: currentVectors,
            // fec: ... (Parity logic would go here)
        };

        // 4. Emit to Backend Relay
        this.socket.emit('stream_packet', payload);
    }

    // --- RECEIVER (STUDENT) ---

    startListening(onDrawVectorCallback) {
        this.onRemoteVector = onDrawVectorCallback;
        
        this.socket.on('stream_packet', async (data) => {
            // Push to Jitter Buffer
            this.jitterBuffer.push(data);
            
            // Sort by Sequence (Handle out-of-order UDP/WS packets)
            this.jitterBuffer.sort((a, b) => a.seq - b.seq);
            
            if (!this.isPlaying && this.jitterBuffer.length > 3) {
                this.playNextPacket();
            }
        });
    }

    async playNextPacket() {
        if (this.jitterBuffer.length === 0) {
            this.isPlaying = false;
            return;
        }

        this.isPlaying = true;
        const packet = this.jitterBuffer.shift();

        // 1. Execute Drawings Immediately (or sync with audio time)
        // For "Zero Tolerance" responsiveness, we draw immediately upon processing the packet
        if (packet.vectors && this.onRemoteVector) {
            packet.vectors.forEach(vec => {
                // vec structure: [[x,y], color, mode]
                this.onRemoteVector(vec);
            });
        }

        // 2. Decode and Play Audio
        try {
            const audioBuffer = await this.audioContext.decodeAudioData(packet.audio);
            const source = this.audioContext.createBufferSource();
            source.buffer = audioBuffer;
            source.connect(this.audioContext.destination);
            
            source.onended = () => {
                this.playNextPacket();
            };

            source.start();
        } catch (e) {
            console.error("Audio Decode Error:", e);
            this.playNextPacket(); // Skip bad packet
        }
    }

    cleanup() {
        this.stopBroadcasting();
        if (this.socket) {
            this.socket.off('stream_packet');
        }
        if (this.audioContext) {
            this.audioContext.close();
        }
    }
}