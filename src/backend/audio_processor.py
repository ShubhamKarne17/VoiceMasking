"""
Audio processing module for real-time voice masking.
Handles audio capture, processing, and output.
"""

import numpy as np
import sounddevice as sd
import threading
import queue
import time
from typing import Callable, Optional
from scipy import signal


class AudioProcessor:
    """Real-time audio processor for voice masking."""
    
    def __init__(self, sample_rate: int = 44100, block_size: int = 1024):
        """
        Initialize the audio processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
            block_size: Number of samples per audio block
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.is_running = False
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.processing_thread = None
        self.voice_transformer = None
        
        # Audio stream objects
        self.input_stream = None
        self.output_stream = None
        
        # Voice transformation parameters
        self.pitch_shift = 1.0  # 1.0 = no change, 0.5 = octave down, 2.0 = octave up
        self.formant_shift = 1.0  # Formant frequency scaling
        self.voice_profile = "original"
        
    def set_voice_profile(self, profile: str):
        """
        Set the voice transformation profile.
        
        Args:
            profile: Voice profile name ('male', 'female', 'child', 'robot', etc.)
        """
        self.voice_profile = profile
        
        # Define transformation parameters for different profiles
        profiles = {
            "original": {"pitch_shift": 1.0, "formant_shift": 1.0},
            "male": {"pitch_shift": 0.8, "formant_shift": 0.9},
            "female": {"pitch_shift": 1.3, "formant_shift": 1.1},
            "child": {"pitch_shift": 1.5, "formant_shift": 1.2},
            "robot": {"pitch_shift": 1.0, "formant_shift": 1.0},  # Will add robotic effects
            "elderly": {"pitch_shift": 0.9, "formant_shift": 0.95},
        }
        
        if profile in profiles:
            self.pitch_shift = profiles[profile]["pitch_shift"]
            self.formant_shift = profiles[profile]["formant_shift"]
    
    def pitch_shift_audio(self, audio_data: np.ndarray, shift_factor: float) -> np.ndarray:
        """
        Apply pitch shifting to audio data using phase vocoder technique.
        
        Args:
            audio_data: Input audio samples
            shift_factor: Pitch shift factor (1.0 = no change)
            
        Returns:
            Pitch-shifted audio samples
        """
        if shift_factor == 1.0:
            return audio_data
            
        # Simple pitch shifting using resampling (basic implementation)
        # For production, consider using more sophisticated algorithms like PSOLA
        original_length = len(audio_data)
        
        # Resample to change pitch
        new_length = int(original_length / shift_factor)
        indices = np.linspace(0, original_length - 1, new_length)
        shifted_audio = np.interp(indices, np.arange(original_length), audio_data)
        
        # Pad or truncate to maintain original length
        if len(shifted_audio) > original_length:
            shifted_audio = shifted_audio[:original_length]
        else:
            shifted_audio = np.pad(shifted_audio, (0, original_length - len(shifted_audio)))
            
        return shifted_audio
    
    def apply_formant_shift(self, audio_data: np.ndarray, shift_factor: float) -> np.ndarray:
        """
        Apply formant shifting to change vocal tract characteristics.
        
        Args:
            audio_data: Input audio samples
            shift_factor: Formant shift factor (1.0 = no change)
            
        Returns:
            Formant-shifted audio samples
        """
        if shift_factor == 1.0:
            return audio_data
            
        # Simple formant shifting using spectral envelope modification
        # This is a basic implementation; more sophisticated methods exist
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        
        # Shift formant frequencies
        shifted_fft = np.zeros_like(fft)
        for i, freq in enumerate(freqs):
            if freq > 0:
                new_freq_idx = int(i * shift_factor)
                if new_freq_idx < len(shifted_fft):
                    shifted_fft[new_freq_idx] = fft[i]
        
        return np.real(np.fft.ifft(shifted_fft))
    
    def apply_robot_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply robotic voice effect using vocoder-like processing.
        
        Args:
            audio_data: Input audio samples
            
        Returns:
            Robot-processed audio samples
        """
        # Generate carrier signal (square wave for robotic effect)
        t = np.arange(len(audio_data)) / self.sample_rate
        carrier_freq = 200  # Hz
        carrier = signal.square(2 * np.pi * carrier_freq * t)
        
        # Apply amplitude modulation
        modulated = audio_data * carrier * 0.5
        
        # Add some filtering to make it sound more robotic
        b, a = signal.butter(4, [300, 3000], btype='band', fs=self.sample_rate)
        filtered = signal.filtfilt(b, a, modulated)
        
        return filtered
    
    def transform_audio(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply voice transformation based on current profile.
        
        Args:
            audio_data: Input audio samples
            
        Returns:
            Transformed audio samples
        """
        transformed = audio_data.copy()
        
        # Apply pitch shifting
        if self.pitch_shift != 1.0:
            transformed = self.pitch_shift_audio(transformed, self.pitch_shift)
        
        # Apply formant shifting
        if self.formant_shift != 1.0:
            transformed = self.apply_formant_shift(transformed, self.formant_shift)
        
        # Apply special effects for specific profiles
        if self.voice_profile == "robot":
            transformed = self.apply_robot_effect(transformed)
        
        # Normalize to prevent clipping
        max_val = np.max(np.abs(transformed))
        if max_val > 0:
            transformed = transformed / max_val * 0.8
        
        return transformed
    
    def audio_input_callback(self, indata, frames, time, status):
        """Callback for audio input stream."""
        if status:
            print(f"Input stream status: {status}")
        
        # Convert to mono if stereo
        if indata.shape[1] > 1:
            audio_data = np.mean(indata, axis=1)
        else:
            audio_data = indata[:, 0]
        
        # Add to processing queue
        try:
            self.input_queue.put_nowait(audio_data.copy())
        except queue.Full:
            print("Input queue full, dropping audio frame")
    
    def audio_output_callback(self, outdata, frames, time, status):
        """Callback for audio output stream."""
        if status:
            print(f"Output stream status: {status}")
        
        try:
            # Get processed audio from queue
            audio_data = self.output_queue.get_nowait()
            outdata[:, 0] = audio_data
            if outdata.shape[1] > 1:  # Stereo output
                outdata[:, 1] = audio_data
        except queue.Empty:
            # No audio available, output silence
            outdata.fill(0)
    
    def processing_worker(self):
        """Worker thread for audio processing."""
        while self.is_running:
            try:
                # Get audio from input queue
                audio_data = self.input_queue.get(timeout=0.1)
                
                # Transform the audio
                transformed_audio = self.transform_audio(audio_data)
                
                # Add to output queue
                try:
                    self.output_queue.put_nowait(transformed_audio)
                except queue.Full:
                    print("Output queue full, dropping processed frame")
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Processing error: {e}")
    
    def start(self):
        """Start real-time audio processing."""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.processing_worker)
        self.processing_thread.start()
        
        # Start audio streams
        try:
            self.input_stream = sd.InputStream(
                callback=self.audio_input_callback,
                channels=1,
                samplerate=self.sample_rate,
                blocksize=self.block_size
            )
            
            self.output_stream = sd.OutputStream(
                callback=self.audio_output_callback,
                channels=2,  # Stereo output
                samplerate=self.sample_rate,
                blocksize=self.block_size
            )
            
            self.input_stream.start()
            self.output_stream.start()
            
            print("Audio processing started")
            
        except Exception as e:
            print(f"Error starting audio streams: {e}")
            self.stop()
    
    def stop(self):
        """Stop real-time audio processing."""
        self.is_running = False
        
        # Stop audio streams
        if self.input_stream:
            self.input_stream.stop()
            self.input_stream.close()
            self.input_stream = None
        
        if self.output_stream:
            self.output_stream.stop()
            self.output_stream.close()
            self.output_stream = None
        
        # Wait for processing thread to finish
        if self.processing_thread:
            self.processing_thread.join()
            self.processing_thread = None
        
        # Clear queues
        while not self.input_queue.empty():
            try:
                self.input_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
        
        print("Audio processing stopped")
    
    def get_available_devices(self):
        """Get list of available audio devices."""
        devices = sd.query_devices()
        return devices
    
    def set_input_device(self, device_id: int):
        """Set the input audio device."""
        sd.default.device[0] = device_id
    
    def set_output_device(self, device_id: int):
        """Set the output audio device."""
        sd.default.device[1] = device_id


if __name__ == "__main__":
    # Test the audio processor
    processor = AudioProcessor()
    
    print("Available audio devices:")
    devices = processor.get_available_devices()
    print(devices)
    
    print("\nStarting voice masking with 'female' profile...")
    processor.set_voice_profile("female")
    processor.start()
    
    try:
        # Run for 10 seconds
        time.sleep(10)
    except KeyboardInterrupt:
        pass
    finally:
        processor.stop()

