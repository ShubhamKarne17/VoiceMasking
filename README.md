# Voice Privacy Masking System

A comprehensive real-time voice transformation system that protects user identity during live communication using AI-powered voice conversion technology.

## 🎯 Project Overview

The Voice Privacy Masking System is an innovative application that transforms a speaker's voice in real-time to conceal their identity during live communication. The system provides natural-sounding voice transformations while maintaining speech intelligibility and emotional expression.

### Key Features

- **Real-time Voice Transformation**: Low-latency voice processing for live communication
- **Multiple Voice Profiles**: Pre-configured profiles for different voice characteristics
- **Emotion Modulation**: Express emotions while maintaining voice privacy
- **Privacy-First Design**: All processing happens locally - no voice data leaves your device
- **Ethical Safeguards**: Built-in watermarking and usage tracking
- **Professional UI**: Modern web-based interface for easy control
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Node.js 20.x or higher
- Audio input/output devices (microphone and speakers/headphones)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd voice_masking_system
   ```

2. **Set up Python environment**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Install system dependencies** (Linux/Ubuntu)
   ```bash
   sudo apt-get update
   sudo apt-get install build-essential portaudio19-dev python3.11-dev
   ```

4. **Set up frontend**
   ```bash
   cd src/frontend/voice-masking-ui
   npm install
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd src/backend
   source ../../venv/bin/activate
   python api_server.py
   ```

2. **Start the frontend** (in a new terminal)
   ```bash
   cd src/frontend/voice-masking-ui
   npm run dev
   ```

3. **Open your browser**
   Navigate to `http://localhost:5173` to access the application.

## 🎙️ How It Works

### Voice Transformation Pipeline

1. **Audio Capture**: Real-time microphone input capture
2. **Pre-processing**: Noise reduction and audio normalization
3. **Voice Conversion**: AI-powered transformation using:
   - Pitch shifting algorithms
   - Formant frequency modification
   - Spectral envelope manipulation
4. **Post-processing**: Audio enhancement and watermarking
5. **Audio Output**: Real-time playback through speakers or virtual audio device

### Voice Profiles

The system includes several pre-configured voice profiles:

#### Human Voices
- **Original Voice**: No transformation applied
- **Deep Male Voice**: Lower pitch with masculine characteristics
- **High Female Voice**: Higher pitch with feminine characteristics
- **Child Voice**: Higher pitch with youthful characteristics
- **Elderly Voice**: Slightly lower pitch with age-related modifications

#### Character Voices
- **Robot Voice**: Vocoder-based robotic transformation
- **Alien Voice**: Otherworldly effects with reverb and modulation
- **Monster Voice**: Deep, intimidating voice with distortion

#### Professional Voices
- **Whisper Voice**: Soft, intimate voice transformation
- **Radio Announcer**: Professional broadcast-quality voice

## 🛡️ Privacy & Ethics

### Privacy Protection
- **Local Processing**: All voice transformation happens on your device
- **No Data Transmission**: Original voice data never leaves your computer
- **Secure by Design**: No cloud dependencies for core functionality

### Ethical Safeguards
- **Audio Watermarking**: Transformed audio includes inaudible watermarks
- **Usage Logging**: Optional tracking of transformations for accountability
- **Disclaimer System**: Built-in warnings about ethical use

### Recommended Use Cases
- Online gaming and streaming privacy
- Anonymous reporting and whistleblowing
- Therapy and counseling sessions
- Voice-over work and content creation
- Protection from voice-based tracking
- Educational demonstrations

## 🔧 Technical Architecture

### Backend Components

- **Audio Processor** (`audio_processor.py`): Core real-time audio processing
- **Voice Profiles** (`voice_profiles.py`): Profile management and configuration
- **API Server** (`api_server.py`): REST API for frontend communication
- **Advanced Effects** (`advanced_effects.py`): Emotion and environmental effects
- **Watermarking** (`watermark.py`): Ethical audio watermarking system
- **Demo Generator** (`demo_generator.py`): Sample audio generation for testing

### Frontend Components

- **React Application**: Modern web-based user interface
- **Real-time Controls**: Voice profile selection and processing controls
- **Audio Device Management**: Input/output device configuration
- **Status Monitoring**: Real-time processing status and audio levels

### API Endpoints

- `GET /api/health` - Health check
- `GET /api/devices` - Get available audio devices
- `GET /api/profiles` - Get voice profiles
- `POST /api/processing/start` - Start voice processing
- `POST /api/processing/stop` - Stop voice processing
- `POST /api/processing/profile` - Change voice profile
- `GET /api/processing/status` - Get processing status

## 🎨 Advanced Features

### Emotion Modulation

The system can apply emotional characteristics to transformed voices:

- **Happiness**: Brighter formants, slight pitch increase, vibrato
- **Sadness**: Darker formants, pitch decrease, tremolo effects
- **Anger**: Harsh formants, distortion, emphasized consonants
- **Fear**: Trembling effects, higher pitch, breathiness

### Environmental Effects

- **Reverb**: Simulate different acoustic spaces
- **Echo**: Add echo effects with configurable delay and feedback
- **Chorus**: Create richer, fuller sound with multiple voices

### Special Effects

- **Vocoder**: Classic robotic voice effect
- **Telephone**: Simulate phone/radio quality
- **Whisper**: Soft, intimate voice transformation
- **Alien**: Otherworldly voice with modulation and reverb

## 📊 Performance Specifications

- **Latency**: < 50ms for real-time processing
- **Sample Rate**: 44.1 kHz (CD quality)
- **Bit Depth**: 16-bit audio processing
- **CPU Usage**: Optimized for real-time performance
- **Memory**: Minimal memory footprint with streaming processing

## 🧪 Testing & Demo

### Generate Demo Audio

```bash
cd src/backend
python demo_generator.py
```

This creates sample audio files demonstrating all voice transformation capabilities.

### Test Voice Profiles

```bash
cd src/backend
python voice_profiles.py
```

### Test Audio Processing

```bash
cd src/backend
python audio_processor.py
```

## 🔧 Configuration

### Audio Settings

- **Sample Rate**: 44100 Hz (configurable)
- **Block Size**: 1024 samples (configurable)
- **Input Device**: Selectable microphone
- **Output Device**: Selectable speakers/headphones

### Voice Profile Customization

Create custom voice profiles by modifying `voice_profiles.py`:

```python
custom_profile = manager.create_custom_profile(
    name="my_custom_voice",
    display_name="My Custom Voice",
    description="A custom voice transformation",
    pitch_shift=1.2,
    formant_shift=1.1,
    special_effects=["reverb"],
    emotion_modifiers={"confidence": 1.3}
)
```

## 🚀 Deployment

### Local Desktop Application

The system runs as a local desktop application with web-based UI.

### Virtual Audio Device Integration

For integration with communication platforms:

1. Install virtual audio cable software
2. Route system output to virtual input
3. Use virtual output in communication apps

## 🛠️ Development

### Project Structure

```
voice_masking_system/
├── src/
│   ├── backend/
│   │   ├── audio_processor.py      # Core audio processing
│   │   ├── voice_profiles.py       # Voice profile management
│   │   ├── api_server.py          # Flask API server
│   │   ├── advanced_effects.py    # Advanced audio effects
│   │   ├── watermark.py           # Ethical watermarking
│   │   └── demo_generator.py      # Demo audio generation
│   └── frontend/
│       └── voice-masking-ui/      # React frontend application
├── docs/                          # Documentation
├── tests/                         # Test files
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### Adding New Voice Profiles

1. Define profile parameters in `voice_profiles.py`
2. Implement transformation logic in `audio_processor.py`
3. Add UI elements in the React frontend
4. Test with demo audio generation

### Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests and documentation
5. Submit a pull request

## 📋 Requirements

### Python Dependencies

- `pyaudio`: Audio input/output
- `sounddevice`: Cross-platform audio I/O
- `numpy`: Numerical computing
- `scipy`: Scientific computing
- `flask`: Web framework
- `flask-cors`: Cross-origin resource sharing

### System Requirements

- **CPU**: Multi-core processor recommended for real-time processing
- **RAM**: 4GB minimum, 8GB recommended
- **Audio**: Full-duplex audio interface (microphone + speakers)
- **OS**: Windows 10+, macOS 10.14+, or Linux (Ubuntu 18.04+)

## 🔍 Troubleshooting

### Common Issues

1. **Audio Device Not Found**
   - Check microphone/speaker connections
   - Verify device permissions
   - Try different audio devices

2. **High Latency**
   - Reduce block size in settings
   - Close other audio applications
   - Use ASIO drivers on Windows

3. **Backend Connection Failed**
   - Ensure Flask server is running on port 5000
   - Check firewall settings
   - Verify Python dependencies are installed

### Performance Optimization

- Use dedicated audio interface for best results
- Close unnecessary applications during use
- Adjust block size based on system performance
- Use wired headphones to prevent feedback

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Voice transformation algorithms inspired by academic research
- UI design using modern React and Tailwind CSS
- Audio processing powered by NumPy and SciPy
- Real-time audio handling with PyAudio and SoundDevice

## 📞 Support

For support, questions, or feature requests:

1. Check the troubleshooting section
2. Review existing issues in the repository
3. Create a new issue with detailed information
4. Include system specifications and error logs

---

**Voice Privacy Masking System v1.0.0**  
*Protecting your voice identity in real-time communication*

