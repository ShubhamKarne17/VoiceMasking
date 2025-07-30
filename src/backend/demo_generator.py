"""
Demo audio generator for testing voice transformation effects.
Creates sample audio files to demonstrate the voice masking capabilities.
"""

import numpy as np
import wave
import os
from typing import List, Tuple
from audio_processor import AudioProcessor
from voice_profiles import VoiceProfileManager
from advanced_effects import AdvancedVoiceEffects, EmotionModulator
from watermark import AudioWatermark


class DemoAudioGenerator:
    """Generates demo audio files for testing and demonstration."""
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize demo audio generator.
        
        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self.audio_processor = AudioProcessor(sample_rate)
        self.profile_manager = VoiceProfileManager()
        self.advanced_effects = AdvancedVoiceEffects(sample_rate)
        self.watermark = AudioWatermark(sample_rate)
        
    def generate_test_speech(self, duration: float = 3.0, 
                           fundamental_freq: float = 150) -> np.ndarray:
        """
        Generate synthetic speech-like audio for testing.
        
        Args:
            duration: Duration in seconds
            fundamental_freq: Fundamental frequency in Hz
            
        Returns:
            Synthetic speech audio
        """
        num_samples = int(duration * self.sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # Create speech-like signal with multiple harmonics
        speech = np.zeros(num_samples)
        
        # Add fundamental and harmonics with varying amplitudes
        harmonics = [1, 2, 3, 4, 5, 6, 7, 8]
        amplitudes = [0.5, 0.3, 0.2, 0.15, 0.1, 0.08, 0.06, 0.04]
        
        for harmonic, amplitude in zip(harmonics, amplitudes):
            freq = fundamental_freq * harmonic
            # Add some frequency modulation for naturalness
            freq_mod = 1 + 0.02 * np.sin(2 * np.pi * 5 * t)  # 5 Hz vibrato
            speech += amplitude * np.sin(2 * np.pi * freq * freq_mod * t)
        
        # Add formant-like resonances
        formant_freqs = [800, 1200, 2400]  # Typical vowel formants
        for formant_freq in formant_freqs:
            formant_amplitude = 0.1
            speech += formant_amplitude * np.sin(2 * np.pi * formant_freq * t)
        
        # Apply envelope to simulate speech patterns
        # Create segments with pauses
        segment_duration = 0.5  # seconds
        pause_duration = 0.1   # seconds
        
        envelope = np.ones(num_samples)
        current_time = 0
        
        while current_time < duration:
            # Speech segment
            segment_start = int(current_time * self.sample_rate)
            segment_end = int(min((current_time + segment_duration) * self.sample_rate, num_samples))
            
            # Apply fade in/out to segment
            segment_length = segment_end - segment_start
            if segment_length > 0:
                fade_length = int(0.05 * self.sample_rate)  # 50ms fade
                if segment_length > 2 * fade_length:
                    envelope[segment_start:segment_start + fade_length] *= np.linspace(0, 1, fade_length)
                    envelope[segment_end - fade_length:segment_end] *= np.linspace(1, 0, fade_length)
            
            current_time += segment_duration
            
            # Pause segment
            pause_start = int(current_time * self.sample_rate)
            pause_end = int(min((current_time + pause_duration) * self.sample_rate, num_samples))
            envelope[pause_start:pause_end] = 0
            
            current_time += pause_duration
        
        # Apply envelope and normalize
        speech = speech * envelope
        
        # Add some noise for realism
        noise_level = 0.01
        noise = np.random.normal(0, noise_level, num_samples)
        speech = speech + noise
        
        # Normalize
        max_val = np.max(np.abs(speech))
        if max_val > 0:
            speech = speech / max_val * 0.8
        
        return speech
    
    def save_audio_to_wav(self, audio_data: np.ndarray, filename: str):
        """
        Save audio data to WAV file.
        
        Args:
            audio_data: Audio samples
            filename: Output filename
        """
        # Ensure audio is in the right format
        audio_int16 = (audio_data * 32767).astype(np.int16)
        
        with wave.open(filename, 'w') as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(audio_int16.tobytes())
    
    def generate_profile_demos(self, output_dir: str = "demo_audio"):
        """
        Generate demo audio files for all voice profiles.
        
        Args:
            output_dir: Directory to save demo files
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate base speech audio
        print("Generating base speech audio...")
        base_speech = self.generate_test_speech(duration=4.0, fundamental_freq=150)
        
        # Save original
        original_path = os.path.join(output_dir, "00_original.wav")
        self.save_audio_to_wav(base_speech, original_path)
        print(f"Saved: {original_path}")
        
        # Generate demos for each profile
        profiles = self.profile_manager.get_all_profiles()
        
        for i, (profile_name, profile) in enumerate(profiles.items(), 1):
            print(f"Generating demo for profile: {profile.display_name}")
            
            # Set the profile
            self.audio_processor.set_voice_profile(profile_name)
            
            # Transform the audio
            transformed_audio = self.audio_processor.transform_audio(base_speech)
            
            # Add watermark
            watermarked_audio = self.watermark.embed_watermark(
                transformed_audio, 
                {'profile': profile_name, 'demo': True}
            )
            
            # Save transformed audio
            filename = f"{i:02d}_{profile_name}.wav"
            output_path = os.path.join(output_dir, filename)
            self.save_audio_to_wav(watermarked_audio, output_path)
            print(f"Saved: {output_path}")
    
    def generate_emotion_demos(self, output_dir: str = "demo_audio"):
        """
        Generate demo audio files for emotion effects.
        
        Args:
            output_dir: Directory to save demo files
        """
        emotions_dir = os.path.join(output_dir, "emotions")
        os.makedirs(emotions_dir, exist_ok=True)
        
        # Generate base speech
        base_speech = self.generate_test_speech(duration=3.0, fundamental_freq=180)
        
        emotion_modulator = EmotionModulator(self.sample_rate)
        
        emotions = [
            ("happy", emotion_modulator.apply_happiness),
            ("sad", emotion_modulator.apply_sadness),
            ("angry", emotion_modulator.apply_anger),
            ("fearful", emotion_modulator.apply_fear)
        ]
        
        for emotion_name, emotion_func in emotions:
            print(f"Generating {emotion_name} emotion demo...")
            
            # Apply emotion with different intensities
            for intensity in [0.5, 1.0, 1.5]:
                emotional_audio = emotion_func(base_speech, intensity)
                
                # Add watermark
                watermarked_audio = self.watermark.embed_watermark(
                    emotional_audio,
                    {'emotion': emotion_name, 'intensity': intensity, 'demo': True}
                )
                
                filename = f"{emotion_name}_intensity_{intensity:.1f}.wav"
                output_path = os.path.join(emotions_dir, filename)
                self.save_audio_to_wav(watermarked_audio, output_path)
                print(f"Saved: {output_path}")
    
    def generate_effects_demos(self, output_dir: str = "demo_audio"):
        """
        Generate demo audio files for special effects.
        
        Args:
            output_dir: Directory to save demo files
        """
        effects_dir = os.path.join(output_dir, "effects")
        os.makedirs(effects_dir, exist_ok=True)
        
        # Generate base speech
        base_speech = self.generate_test_speech(duration=3.0, fundamental_freq=160)
        
        effects = [
            ("vocoder", lambda x: self.advanced_effects.apply_vocoder(x, 200)),
            ("whisper", lambda x: self.advanced_effects.apply_whisper_effect(x, 0.7)),
            ("telephone", self.advanced_effects.apply_telephone_effect),
            ("alien", self.advanced_effects.apply_alien_effect),
            ("reverb", lambda x: self.advanced_effects.environmental_effects.apply_reverb(
                x, room_size=0.8, wet_level=0.6)),
            ("echo", lambda x: self.advanced_effects.environmental_effects.apply_echo(
                x, delay_ms=250, feedback=0.4, wet_level=0.5))
        ]
        
        for effect_name, effect_func in effects:
            print(f"Generating {effect_name} effect demo...")
            
            try:
                effect_audio = effect_func(base_speech)
                
                # Add watermark
                watermarked_audio = self.watermark.embed_watermark(
                    effect_audio,
                    {'effect': effect_name, 'demo': True}
                )
                
                filename = f"{effect_name}_effect.wav"
                output_path = os.path.join(effects_dir, filename)
                self.save_audio_to_wav(watermarked_audio, output_path)
                print(f"Saved: {output_path}")
                
            except Exception as e:
                print(f"Error generating {effect_name} effect: {e}")
    
    def generate_comparison_demo(self, output_dir: str = "demo_audio"):
        """
        Generate a comparison demo with multiple transformations of the same audio.
        
        Args:
            output_dir: Directory to save demo files
        """
        comparison_dir = os.path.join(output_dir, "comparison")
        os.makedirs(comparison_dir, exist_ok=True)
        
        # Generate longer speech sample
        base_speech = self.generate_test_speech(duration=5.0, fundamental_freq=140)
        
        # Save original
        original_path = os.path.join(comparison_dir, "original.wav")
        self.save_audio_to_wav(base_speech, original_path)
        
        # Apply different transformations
        transformations = [
            ("male_deep", "male_deep"),
            ("female_high", "female_high"),
            ("child", "child"),
            ("robot", "robot"),
            ("alien_effect", None)  # Special effect, not a profile
        ]
        
        for transform_name, profile_name in transformations:
            print(f"Generating comparison demo: {transform_name}")
            
            if profile_name:
                # Use voice profile
                self.audio_processor.set_voice_profile(profile_name)
                transformed_audio = self.audio_processor.transform_audio(base_speech)
            else:
                # Use special effect
                if transform_name == "alien_effect":
                    transformed_audio = self.advanced_effects.apply_alien_effect(base_speech)
            
            # Add watermark
            watermarked_audio = self.watermark.embed_watermark(
                transformed_audio,
                {'transformation': transform_name, 'comparison_demo': True}
            )
            
            filename = f"{transform_name}.wav"
            output_path = os.path.join(comparison_dir, filename)
            self.save_audio_to_wav(watermarked_audio, output_path)
            print(f"Saved: {output_path}")
    
    def generate_all_demos(self, output_dir: str = "demo_audio"):
        """
        Generate all demo audio files.
        
        Args:
            output_dir: Directory to save demo files
        """
        print("=== Voice Masking System Demo Generator ===")
        print(f"Output directory: {output_dir}")
        print()
        
        try:
            # Generate profile demos
            print("1. Generating voice profile demos...")
            self.generate_profile_demos(output_dir)
            print()
            
            # Generate emotion demos
            print("2. Generating emotion effect demos...")
            self.generate_emotion_demos(output_dir)
            print()
            
            # Generate effects demos
            print("3. Generating special effects demos...")
            self.generate_effects_demos(output_dir)
            print()
            
            # Generate comparison demo
            print("4. Generating comparison demos...")
            self.generate_comparison_demo(output_dir)
            print()
            
            print("=== Demo generation completed! ===")
            print(f"All demo files saved to: {os.path.abspath(output_dir)}")
            
        except Exception as e:
            print(f"Error during demo generation: {e}")
            raise


if __name__ == "__main__":
    # Generate all demo audio files
    demo_generator = DemoAudioGenerator()
    demo_generator.generate_all_demos("demo_audio")
    
    print("\nDemo audio files generated successfully!")
    print("You can use these files to test the voice masking system.")
    print("Each file demonstrates different voice transformation capabilities.")

