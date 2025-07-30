"""
Advanced audio effects for enhanced voice transformation.
Includes emotion modulation, environmental effects, and advanced processing.
"""

import numpy as np
from scipy import signal, interpolate
from typing import Dict, List, Tuple, Optional
import random


class EmotionModulator:
    """Modulates voice to express different emotions."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize emotion modulator.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        
    def apply_happiness(self, audio_data: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """
        Apply happiness emotion to voice.
        
        Args:
            audio_data: Input audio samples
            intensity: Emotion intensity (0.0 to 2.0)
            
        Returns:
            Audio with happiness emotion applied
        """
        # Happiness: slightly higher pitch, faster tempo, brighter formants
        processed = audio_data.copy()
        
        # Pitch shift up slightly
        pitch_factor = 1.0 + (0.1 * intensity)
        processed = self._pitch_shift(processed, pitch_factor)
        
        # Add slight vibrato for liveliness
        vibrato_freq = 5.0  # Hz
        vibrato_depth = 0.02 * intensity
        t = np.arange(len(processed)) / self.sample_rate
        vibrato = 1 + vibrato_depth * np.sin(2 * np.pi * vibrato_freq * t)
        processed = processed * vibrato
        
        # Brighten the sound (boost higher frequencies)
        processed = self._apply_eq(processed, [(2000, 3.0 * intensity), (4000, 2.0 * intensity)])
        
        return processed
    
    def apply_sadness(self, audio_data: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """
        Apply sadness emotion to voice.
        
        Args:
            audio_data: Input audio samples
            intensity: Emotion intensity (0.0 to 2.0)
            
        Returns:
            Audio with sadness emotion applied
        """
        # Sadness: lower pitch, slower tempo, darker formants
        processed = audio_data.copy()
        
        # Pitch shift down
        pitch_factor = 1.0 - (0.15 * intensity)
        processed = self._pitch_shift(processed, pitch_factor)
        
        # Add tremolo for emotional effect
        tremolo_freq = 3.0  # Hz
        tremolo_depth = 0.1 * intensity
        t = np.arange(len(processed)) / self.sample_rate
        tremolo = 1 - tremolo_depth * (1 + np.sin(2 * np.pi * tremolo_freq * t)) / 2
        processed = processed * tremolo
        
        # Darken the sound (reduce higher frequencies)
        processed = self._apply_eq(processed, [(1000, -2.0 * intensity), (3000, -4.0 * intensity)])
        
        return processed
    
    def apply_anger(self, audio_data: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """
        Apply anger emotion to voice.
        
        Args:
            audio_data: Input audio samples
            intensity: Emotion intensity (0.0 to 2.0)
            
        Returns:
            Audio with anger emotion applied
        """
        # Anger: harsh formants, slight distortion, emphasized consonants
        processed = audio_data.copy()
        
        # Add slight distortion
        distortion_amount = 0.1 * intensity
        processed = np.tanh(processed * (1 + distortion_amount))
        
        # Emphasize mid frequencies (vocal formants)
        processed = self._apply_eq(processed, [(800, 4.0 * intensity), (1500, 3.0 * intensity)])
        
        # Add slight roughness with amplitude modulation
        roughness_freq = 30.0  # Hz
        roughness_depth = 0.05 * intensity
        t = np.arange(len(processed)) / self.sample_rate
        roughness = 1 + roughness_depth * np.sin(2 * np.pi * roughness_freq * t)
        processed = processed * roughness
        
        return processed
    
    def apply_fear(self, audio_data: np.ndarray, intensity: float = 1.0) -> np.ndarray:
        """
        Apply fear emotion to voice.
        
        Args:
            audio_data: Input audio samples
            intensity: Emotion intensity (0.0 to 2.0)
            
        Returns:
            Audio with fear emotion applied
        """
        # Fear: trembling, higher pitch, breathiness
        processed = audio_data.copy()
        
        # Pitch shift up with variation
        pitch_factor = 1.0 + (0.2 * intensity)
        processed = self._pitch_shift(processed, pitch_factor)
        
        # Add trembling effect
        trembling_freq = 8.0  # Hz
        trembling_depth = 0.15 * intensity
        t = np.arange(len(processed)) / self.sample_rate
        trembling = 1 + trembling_depth * np.sin(2 * np.pi * trembling_freq * t)
        processed = processed * trembling
        
        # Add breathiness (noise)
        noise_level = 0.02 * intensity
        noise = np.random.normal(0, noise_level, len(processed))
        processed = processed + noise
        
        return processed
    
    def _pitch_shift(self, audio_data: np.ndarray, factor: float) -> np.ndarray:
        """Simple pitch shifting using resampling."""
        if factor == 1.0:
            return audio_data
        
        # Resample to change pitch
        original_length = len(audio_data)
        new_length = int(original_length / factor)
        
        # Create new time indices
        old_indices = np.arange(original_length)
        new_indices = np.linspace(0, original_length - 1, new_length)
        
        # Interpolate
        shifted = np.interp(new_indices, old_indices, audio_data)
        
        # Pad or truncate to maintain original length
        if len(shifted) > original_length:
            return shifted[:original_length]
        else:
            return np.pad(shifted, (0, original_length - len(shifted)))
    
    def _apply_eq(self, audio_data: np.ndarray, eq_bands: List[Tuple[float, float]]) -> np.ndarray:
        """
        Apply equalization to audio.
        
        Args:
            audio_data: Input audio
            eq_bands: List of (frequency, gain_db) tuples
            
        Returns:
            Equalized audio
        """
        processed = audio_data.copy()
        
        for freq, gain_db in eq_bands:
            # Convert gain from dB to linear
            gain_linear = 10 ** (gain_db / 20)
            
            # Create a simple peaking filter
            nyquist = self.sample_rate / 2
            normalized_freq = freq / nyquist
            
            if 0 < normalized_freq < 1:
                # Design a peaking filter
                Q = 1.0  # Quality factor
                w0 = 2 * np.pi * normalized_freq
                alpha = np.sin(w0) / (2 * Q)
                
                # Peaking filter coefficients
                A = gain_linear
                b0 = 1 + alpha * A
                b1 = -2 * np.cos(w0)
                b2 = 1 - alpha * A
                a0 = 1 + alpha / A
                a1 = -2 * np.cos(w0)
                a2 = 1 - alpha / A
                
                # Normalize coefficients
                b = [b0/a0, b1/a0, b2/a0]
                a = [1, a1/a0, a2/a0]
                
                # Apply filter
                processed = signal.filtfilt(b, a, processed)
        
        return processed


class EnvironmentalEffects:
    """Environmental audio effects for voice transformation."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize environmental effects processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
    
    def apply_reverb(self, audio_data: np.ndarray, room_size: float = 0.5, 
                    damping: float = 0.5, wet_level: float = 0.3) -> np.ndarray:
        """
        Apply reverb effect to simulate different acoustic spaces.
        
        Args:
            audio_data: Input audio samples
            room_size: Size of the simulated room (0.0 to 1.0)
            damping: High frequency damping (0.0 to 1.0)
            wet_level: Mix level of reverb (0.0 to 1.0)
            
        Returns:
            Audio with reverb applied
        """
        # Create impulse response for reverb
        reverb_length = int(self.sample_rate * (0.1 + room_size * 2.0))  # 0.1 to 2.1 seconds
        
        # Generate exponentially decaying noise as impulse response
        t = np.arange(reverb_length) / self.sample_rate
        decay_time = 0.5 + room_size * 2.0  # Decay time based on room size
        envelope = np.exp(-t / decay_time)
        
        # Create noise and shape it
        noise = np.random.normal(0, 1, reverb_length)
        impulse_response = noise * envelope
        
        # Apply damping (low-pass filter)
        if damping > 0:
            cutoff_freq = 8000 * (1 - damping)  # Higher damping = lower cutoff
            nyquist = self.sample_rate / 2
            normalized_cutoff = cutoff_freq / nyquist
            if normalized_cutoff < 1.0:
                b, a = signal.butter(2, normalized_cutoff, btype='low')
                impulse_response = signal.filtfilt(b, a, impulse_response)
        
        # Convolve with input audio
        reverb_audio = signal.convolve(audio_data, impulse_response, mode='same')
        
        # Mix dry and wet signals
        dry_level = 1.0 - wet_level
        return dry_level * audio_data + wet_level * reverb_audio
    
    def apply_echo(self, audio_data: np.ndarray, delay_ms: float = 300, 
                  feedback: float = 0.3, wet_level: float = 0.3) -> np.ndarray:
        """
        Apply echo effect.
        
        Args:
            audio_data: Input audio samples
            delay_ms: Echo delay in milliseconds
            feedback: Echo feedback amount (0.0 to 0.9)
            wet_level: Mix level of echo (0.0 to 1.0)
            
        Returns:
            Audio with echo applied
        """
        delay_samples = int(delay_ms * self.sample_rate / 1000)
        
        if delay_samples >= len(audio_data):
            return audio_data
        
        # Create echo buffer
        echo_buffer = np.zeros(len(audio_data) + delay_samples)
        echo_buffer[:len(audio_data)] = audio_data
        
        # Apply echo with feedback
        for i in range(delay_samples, len(echo_buffer)):
            if i - delay_samples < len(audio_data):
                echo_buffer[i] += feedback * echo_buffer[i - delay_samples]
        
        # Trim to original length and mix
        echo_audio = echo_buffer[:len(audio_data)]
        dry_level = 1.0 - wet_level
        return dry_level * audio_data + wet_level * echo_audio
    
    def apply_chorus(self, audio_data: np.ndarray, depth: float = 0.5, 
                    rate: float = 1.0, wet_level: float = 0.5) -> np.ndarray:
        """
        Apply chorus effect for richer sound.
        
        Args:
            audio_data: Input audio samples
            depth: Chorus depth (0.0 to 1.0)
            rate: Chorus rate in Hz
            wet_level: Mix level of chorus (0.0 to 1.0)
            
        Returns:
            Audio with chorus applied
        """
        # Create multiple delayed and modulated copies
        num_voices = 3
        chorus_audio = np.zeros_like(audio_data)
        
        for voice in range(num_voices):
            # Different delay and modulation for each voice
            base_delay_ms = 10 + voice * 5  # 10, 15, 20 ms
            mod_depth_ms = depth * 5  # Up to 5ms modulation
            
            # Create time-varying delay
            t = np.arange(len(audio_data)) / self.sample_rate
            lfo_freq = rate * (0.8 + voice * 0.1)  # Slightly different rates
            delay_variation = mod_depth_ms * np.sin(2 * np.pi * lfo_freq * t)
            delay_ms = base_delay_ms + delay_variation
            
            # Apply time-varying delay (simplified)
            avg_delay_samples = int(np.mean(delay_ms) * self.sample_rate / 1000)
            if avg_delay_samples < len(audio_data):
                delayed_audio = np.zeros_like(audio_data)
                delayed_audio[avg_delay_samples:] = audio_data[:-avg_delay_samples]
                chorus_audio += delayed_audio / num_voices
        
        # Mix dry and wet signals
        dry_level = 1.0 - wet_level
        return dry_level * audio_data + wet_level * chorus_audio


class AdvancedVoiceEffects:
    """Advanced voice transformation effects."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize advanced voice effects processor.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.emotion_modulator = EmotionModulator(sample_rate)
        self.environmental_effects = EnvironmentalEffects(sample_rate)
    
    def apply_vocoder(self, audio_data: np.ndarray, carrier_freq: float = 200) -> np.ndarray:
        """
        Apply vocoder effect for robotic voice.
        
        Args:
            audio_data: Input audio samples
            carrier_freq: Carrier frequency in Hz
            
        Returns:
            Vocoded audio
        """
        # Generate carrier signal
        t = np.arange(len(audio_data)) / self.sample_rate
        carrier = signal.square(2 * np.pi * carrier_freq * t)
        
        # Extract envelope from original signal
        analytic_signal = signal.hilbert(audio_data)
        envelope = np.abs(analytic_signal)
        
        # Apply envelope to carrier
        vocoded = carrier * envelope * 0.5
        
        # Apply band-pass filtering to make it sound more natural
        nyquist = self.sample_rate / 2
        low_freq = 300 / nyquist
        high_freq = 3000 / nyquist
        
        if low_freq < 1.0 and high_freq < 1.0:
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            vocoded = signal.filtfilt(b, a, vocoded)
        
        return vocoded
    
    def apply_whisper_effect(self, audio_data: np.ndarray, intensity: float = 0.5) -> np.ndarray:
        """
        Apply whisper effect by adding noise and reducing amplitude.
        
        Args:
            audio_data: Input audio samples
            intensity: Whisper intensity (0.0 to 1.0)
            
        Returns:
            Whispered audio
        """
        # Reduce amplitude
        whispered = audio_data * (1.0 - intensity * 0.7)
        
        # Add filtered noise
        noise = np.random.normal(0, 0.1 * intensity, len(audio_data))
        
        # Filter noise to match speech spectrum
        nyquist = self.sample_rate / 2
        low_freq = 500 / nyquist
        high_freq = 4000 / nyquist
        
        if low_freq < 1.0 and high_freq < 1.0:
            b, a = signal.butter(2, [low_freq, high_freq], btype='band')
            noise = signal.filtfilt(b, a, noise)
        
        # Mix original and noise
        whispered = whispered + noise
        
        # Apply high-pass filter to remove low frequencies
        high_pass_freq = 200 / nyquist
        if high_pass_freq < 1.0:
            b, a = signal.butter(2, high_pass_freq, btype='high')
            whispered = signal.filtfilt(b, a, whispered)
        
        return whispered
    
    def apply_telephone_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply telephone/radio effect with band-pass filtering.
        
        Args:
            audio_data: Input audio samples
            
        Returns:
            Audio with telephone effect
        """
        # Band-pass filter to simulate telephone frequency response
        nyquist = self.sample_rate / 2
        low_freq = 300 / nyquist
        high_freq = 3400 / nyquist
        
        if low_freq < 1.0 and high_freq < 1.0:
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            filtered = signal.filtfilt(b, a, audio_data)
        else:
            filtered = audio_data
        
        # Add slight distortion
        filtered = np.tanh(filtered * 2) * 0.7
        
        # Add some noise
        noise = np.random.normal(0, 0.01, len(filtered))
        filtered = filtered + noise
        
        return filtered
    
    def apply_alien_effect(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply alien voice effect with pitch modulation and reverb.
        
        Args:
            audio_data: Input audio samples
            
        Returns:
            Audio with alien effect
        """
        # Apply pitch modulation
        t = np.arange(len(audio_data)) / self.sample_rate
        pitch_mod_freq = 3.0  # Hz
        pitch_mod_depth = 0.3
        pitch_mod = 1 + pitch_mod_depth * np.sin(2 * np.pi * pitch_mod_freq * t)
        
        # Simple pitch modulation by amplitude modulation
        modulated = audio_data * pitch_mod
        
        # Apply reverb for spacey effect
        reverb_audio = self.environmental_effects.apply_reverb(
            modulated, room_size=0.8, damping=0.3, wet_level=0.6
        )
        
        # Apply chorus for richness
        alien_audio = self.environmental_effects.apply_chorus(
            reverb_audio, depth=0.7, rate=0.5, wet_level=0.4
        )
        
        return alien_audio


if __name__ == "__main__":
    # Test the advanced effects
    sample_rate = 44100
    duration = 2.0
    num_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, num_samples, False)
    
    # Create test audio (speech-like signal)
    fundamental = 150  # Hz
    test_audio = (np.sin(2 * np.pi * fundamental * t) * 0.3 +
                 np.sin(2 * np.pi * fundamental * 2 * t) * 0.2 +
                 np.sin(2 * np.pi * fundamental * 3 * t) * 0.1)
    
    print("Testing advanced voice effects...")
    
    # Test emotion modulation
    emotion_mod = EmotionModulator(sample_rate)
    happy_audio = emotion_mod.apply_happiness(test_audio, intensity=1.0)
    sad_audio = emotion_mod.apply_sadness(test_audio, intensity=1.0)
    
    print(f"Original audio RMS: {np.sqrt(np.mean(test_audio**2)):.4f}")
    print(f"Happy audio RMS: {np.sqrt(np.mean(happy_audio**2)):.4f}")
    print(f"Sad audio RMS: {np.sqrt(np.mean(sad_audio**2)):.4f}")
    
    # Test environmental effects
    env_effects = EnvironmentalEffects(sample_rate)
    reverb_audio = env_effects.apply_reverb(test_audio, room_size=0.7, wet_level=0.5)
    echo_audio = env_effects.apply_echo(test_audio, delay_ms=200, feedback=0.4)
    
    print(f"Reverb audio RMS: {np.sqrt(np.mean(reverb_audio**2)):.4f}")
    print(f"Echo audio RMS: {np.sqrt(np.mean(echo_audio**2)):.4f}")
    
    # Test advanced effects
    advanced_effects = AdvancedVoiceEffects(sample_rate)
    vocoder_audio = advanced_effects.apply_vocoder(test_audio, carrier_freq=200)
    alien_audio = advanced_effects.apply_alien_effect(test_audio)
    
    print(f"Vocoder audio RMS: {np.sqrt(np.mean(vocoder_audio**2)):.4f}")
    print(f"Alien audio RMS: {np.sqrt(np.mean(alien_audio**2)):.4f}")
    
    print("Advanced effects testing completed.")

