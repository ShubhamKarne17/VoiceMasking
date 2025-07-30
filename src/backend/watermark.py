"""
Audio watermarking module for ethical voice transformation.
Embeds inaudible watermarks to indicate transformed audio.
"""

import numpy as np
import hashlib
import time
from typing import Optional, Tuple
from scipy import signal


class AudioWatermark:
    """Audio watermarking for ethical voice transformation."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize the audio watermarking system.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.watermark_freq = 19000  # High frequency for watermark (near ultrasonic)
        self.watermark_amplitude = 0.001  # Very low amplitude to be inaudible
        self.watermark_duration = 0.1  # Duration of watermark signal in seconds
        
    def generate_watermark_signal(self, duration: float, metadata: dict = None) -> np.ndarray:
        """
        Generate a watermark signal with embedded metadata.
        
        Args:
            duration: Duration of the watermark signal in seconds
            metadata: Optional metadata to embed (timestamp, profile, etc.)
            
        Returns:
            Watermark signal as numpy array
        """
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # Base watermark frequency
        base_freq = self.watermark_freq
        
        # Encode metadata in frequency modulation if provided
        if metadata:
            # Create a simple hash of metadata for frequency offset
            metadata_str = str(sorted(metadata.items()))
            metadata_hash = hashlib.md5(metadata_str.encode()).hexdigest()
            freq_offset = int(metadata_hash[:4], 16) % 100  # 0-99 Hz offset
            base_freq += freq_offset
        
        # Generate watermark signal
        watermark = np.sin(2 * np.pi * base_freq * t) * self.watermark_amplitude
        
        # Add some phase modulation for robustness
        phase_mod = np.sin(2 * np.pi * 50 * t) * 0.1  # 50 Hz phase modulation
        watermark = np.sin(2 * np.pi * base_freq * t + phase_mod) * self.watermark_amplitude
        
        return watermark
    
    def embed_watermark(self, audio_data: np.ndarray, metadata: dict = None) -> np.ndarray:
        """
        Embed watermark into audio data.
        
        Args:
            audio_data: Input audio samples
            metadata: Optional metadata to embed
            
        Returns:
            Audio with embedded watermark
        """
        if len(audio_data) == 0:
            return audio_data
        
        # Default metadata
        if metadata is None:
            metadata = {
                'timestamp': int(time.time()),
                'type': 'voice_transformed',
                'version': '1.0'
            }
        
        # Generate watermark for the entire audio duration
        duration = len(audio_data) / self.sample_rate
        watermark = self.generate_watermark_signal(duration, metadata)
        
        # Ensure watermark length matches audio length
        if len(watermark) > len(audio_data):
            watermark = watermark[:len(audio_data)]
        elif len(watermark) < len(audio_data):
            # Repeat watermark to match audio length
            repeats = int(np.ceil(len(audio_data) / len(watermark)))
            watermark = np.tile(watermark, repeats)[:len(audio_data)]
        
        # Embed watermark by adding to original audio
        watermarked_audio = audio_data + watermark
        
        # Ensure no clipping
        max_val = np.max(np.abs(watermarked_audio))
        if max_val > 1.0:
            watermarked_audio = watermarked_audio / max_val * 0.95
        
        return watermarked_audio
    
    def detect_watermark(self, audio_data: np.ndarray) -> Tuple[bool, Optional[dict]]:
        """
        Detect if audio contains a watermark and extract metadata.
        
        Args:
            audio_data: Audio samples to analyze
            
        Returns:
            Tuple of (watermark_detected, metadata)
        """
        if len(audio_data) < self.sample_rate * 0.1:  # Need at least 0.1 seconds
            return False, None
        
        # Perform FFT to analyze frequency content
        fft = np.fft.fft(audio_data)
        freqs = np.fft.fftfreq(len(audio_data), 1/self.sample_rate)
        
        # Look for watermark frequency range
        watermark_range = (self.watermark_freq - 50, self.watermark_freq + 150)
        freq_mask = (freqs >= watermark_range[0]) & (freqs <= watermark_range[1])
        
        if not np.any(freq_mask):
            return False, None
        
        # Check for significant energy in watermark frequency range
        watermark_energy = np.sum(np.abs(fft[freq_mask])**2)
        total_energy = np.sum(np.abs(fft)**2)
        
        # If watermark energy is above threshold, consider it detected
        energy_ratio = watermark_energy / total_energy
        threshold = 1e-6  # Very low threshold since watermark is subtle
        
        if energy_ratio > threshold:
            # Try to extract metadata from frequency offset
            peak_freq_idx = np.argmax(np.abs(fft[freq_mask]))
            peak_freq = freqs[freq_mask][peak_freq_idx]
            freq_offset = int(peak_freq - self.watermark_freq)
            
            # This is a simplified metadata extraction
            # In practice, more sophisticated encoding would be used
            metadata = {
                'detected': True,
                'frequency_offset': freq_offset,
                'energy_ratio': float(energy_ratio),
                'detection_confidence': min(energy_ratio / threshold, 1.0)
            }
            
            return True, metadata
        
        return False, None
    
    def create_disclaimer_audio(self, text: str = None) -> np.ndarray:
        """
        Create an audio disclaimer that can be prepended to transformed audio.
        
        Args:
            text: Disclaimer text (if None, uses default)
            
        Returns:
            Audio samples for disclaimer
        """
        if text is None:
            text = "This audio has been processed with voice transformation technology."
        
        # For now, create a simple tone sequence as placeholder
        # In a full implementation, this would use text-to-speech
        duration = 2.0  # 2 seconds
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a sequence of tones to represent the disclaimer
        frequencies = [800, 1000, 1200, 1000]  # Simple tone sequence
        tone_duration = duration / len(frequencies)
        
        disclaimer_audio = np.zeros(num_samples)
        for i, freq in enumerate(frequencies):
            start_idx = int(i * tone_duration * self.sample_rate)
            end_idx = int((i + 1) * tone_duration * self.sample_rate)
            if end_idx > num_samples:
                end_idx = num_samples
            
            tone_samples = end_idx - start_idx
            tone_t = np.linspace(0, tone_duration, tone_samples, False)
            tone = np.sin(2 * np.pi * freq * tone_t) * 0.1
            
            # Apply fade in/out to avoid clicks
            fade_samples = int(0.01 * self.sample_rate)  # 10ms fade
            if tone_samples > 2 * fade_samples:
                tone[:fade_samples] *= np.linspace(0, 1, fade_samples)
                tone[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            disclaimer_audio[start_idx:end_idx] = tone
        
        return disclaimer_audio


class EthicalVoiceProcessor:
    """Wrapper for voice processing with ethical safeguards."""
    
    def __init__(self, audio_processor, sample_rate: int = 44100):
        """
        Initialize ethical voice processor.
        
        Args:
            audio_processor: The main audio processor instance
            sample_rate: Audio sample rate
        """
        self.audio_processor = audio_processor
        self.watermark = AudioWatermark(sample_rate)
        self.transformation_log = []
        self.require_disclaimer = True
        self.enable_watermarking = True
        
    def process_with_ethics(self, audio_data: np.ndarray, profile: str) -> np.ndarray:
        """
        Process audio with ethical safeguards.
        
        Args:
            audio_data: Input audio samples
            profile: Voice transformation profile
            
        Returns:
            Ethically processed audio
        """
        # Log the transformation
        log_entry = {
            'timestamp': time.time(),
            'profile': profile,
            'duration': len(audio_data) / self.audio_processor.sample_rate,
            'watermarked': self.enable_watermarking
        }
        self.transformation_log.append(log_entry)
        
        # Apply voice transformation
        transformed_audio = self.audio_processor.transform_audio(audio_data)
        
        # Add watermark if enabled
        if self.enable_watermarking:
            metadata = {
                'timestamp': int(time.time()),
                'profile': profile,
                'type': 'voice_transformed',
                'version': '1.0'
            }
            transformed_audio = self.watermark.embed_watermark(transformed_audio, metadata)
        
        return transformed_audio
    
    def verify_audio_integrity(self, audio_data: np.ndarray) -> dict:
        """
        Verify if audio has been processed and extract information.
        
        Args:
            audio_data: Audio to verify
            
        Returns:
            Verification results
        """
        detected, metadata = self.watermark.detect_watermark(audio_data)
        
        return {
            'is_transformed': detected,
            'metadata': metadata,
            'verification_timestamp': time.time()
        }
    
    def get_transformation_log(self) -> list:
        """Get the log of all transformations performed."""
        return self.transformation_log.copy()
    
    def clear_log(self):
        """Clear the transformation log."""
        self.transformation_log.clear()
    
    def set_ethical_settings(self, enable_watermarking: bool = True, 
                           require_disclaimer: bool = True):
        """
        Configure ethical processing settings.
        
        Args:
            enable_watermarking: Whether to embed watermarks
            require_disclaimer: Whether to require disclaimers
        """
        self.enable_watermarking = enable_watermarking
        self.require_disclaimer = require_disclaimer


if __name__ == "__main__":
    # Test the watermarking system
    watermark = AudioWatermark()
    
    # Create test audio
    duration = 1.0
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, False)
    test_audio = np.sin(2 * np.pi * 440 * t) * 0.5  # 440 Hz sine wave
    
    print("Testing audio watermarking...")
    
    # Embed watermark
    metadata = {'profile': 'test', 'timestamp': int(time.time())}
    watermarked_audio = watermark.embed_watermark(test_audio, metadata)
    
    print(f"Original audio length: {len(test_audio)}")
    print(f"Watermarked audio length: {len(watermarked_audio)}")
    
    # Detect watermark
    detected, extracted_metadata = watermark.detect_watermark(watermarked_audio)
    
    print(f"Watermark detected: {detected}")
    if detected:
        print(f"Extracted metadata: {extracted_metadata}")
    
    # Test with non-watermarked audio
    detected_clean, _ = watermark.detect_watermark(test_audio)
    print(f"Watermark detected in clean audio: {detected_clean}")
    
    print("Watermarking test completed.")

