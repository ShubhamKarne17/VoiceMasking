"""
Voice profiles management for the voice masking system.
Defines different voice transformation profiles and their parameters.
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict


@dataclass
class VoiceProfile:
    """Voice transformation profile configuration."""
    name: str
    display_name: str
    description: str
    pitch_shift: float
    formant_shift: float
    special_effects: List[str]
    emotion_modifiers: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VoiceProfile':
        """Create profile from dictionary."""
        return cls(**data)


class VoiceProfileManager:
    """Manages voice transformation profiles."""
    
    def __init__(self, profiles_file: str = None):
        """
        Initialize the voice profile manager.
        
        Args:
            profiles_file: Path to JSON file containing voice profiles
        """
        self.profiles_file = profiles_file
        self.profiles: Dict[str, VoiceProfile] = {}
        self._load_default_profiles()
        
        if profiles_file and os.path.exists(profiles_file):
            self.load_profiles(profiles_file)
    
    def _load_default_profiles(self):
        """Load default voice profiles."""
        default_profiles = [
            VoiceProfile(
                name="original",
                display_name="Original Voice",
                description="No transformation applied",
                pitch_shift=1.0,
                formant_shift=1.0,
                special_effects=[],
                emotion_modifiers={}
            ),
            VoiceProfile(
                name="male_deep",
                display_name="Deep Male Voice",
                description="Transform to a deeper male voice",
                pitch_shift=0.7,
                formant_shift=0.85,
                special_effects=[],
                emotion_modifiers={"confidence": 1.2, "authority": 1.3}
            ),
            VoiceProfile(
                name="female_high",
                display_name="High Female Voice",
                description="Transform to a higher female voice",
                pitch_shift=1.4,
                formant_shift=1.15,
                special_effects=[],
                emotion_modifiers={"friendliness": 1.2, "enthusiasm": 1.1}
            ),
            VoiceProfile(
                name="child",
                display_name="Child Voice",
                description="Transform to sound like a child",
                pitch_shift=1.6,
                formant_shift=1.25,
                special_effects=["brightness"],
                emotion_modifiers={"playfulness": 1.5, "innocence": 1.3}
            ),
            VoiceProfile(
                name="elderly",
                display_name="Elderly Voice",
                description="Transform to sound like an elderly person",
                pitch_shift=0.9,
                formant_shift=0.95,
                special_effects=["tremolo", "roughness"],
                emotion_modifiers={"wisdom": 1.3, "calmness": 1.2}
            ),
            VoiceProfile(
                name="robot",
                display_name="Robot Voice",
                description="Robotic voice transformation",
                pitch_shift=1.0,
                formant_shift=1.0,
                special_effects=["vocoder", "metallic"],
                emotion_modifiers={"monotone": 2.0}
            ),
            VoiceProfile(
                name="alien",
                display_name="Alien Voice",
                description="Otherworldly alien voice",
                pitch_shift=1.2,
                formant_shift=1.3,
                special_effects=["reverb", "chorus", "pitch_modulation"],
                emotion_modifiers={"mystery": 1.5, "otherworldly": 2.0}
            ),
            VoiceProfile(
                name="monster",
                display_name="Monster Voice",
                description="Scary monster voice",
                pitch_shift=0.6,
                formant_shift=0.8,
                special_effects=["distortion", "growl"],
                emotion_modifiers={"intimidation": 2.0, "fear": 1.8}
            ),
            VoiceProfile(
                name="whisper",
                display_name="Whisper Voice",
                description="Soft whisper transformation",
                pitch_shift=0.95,
                formant_shift=1.05,
                special_effects=["noise_reduction", "softness"],
                emotion_modifiers={"intimacy": 1.5, "secrecy": 1.3}
            ),
            VoiceProfile(
                name="announcer",
                display_name="Radio Announcer",
                description="Professional radio announcer voice",
                pitch_shift=0.85,
                formant_shift=0.9,
                special_effects=["compression", "eq_boost"],
                emotion_modifiers={"professionalism": 1.5, "clarity": 1.4}
            )
        ]
        
        for profile in default_profiles:
            self.profiles[profile.name] = profile
    
    def get_profile(self, name: str) -> VoiceProfile:
        """
        Get a voice profile by name.
        
        Args:
            name: Profile name
            
        Returns:
            VoiceProfile object
            
        Raises:
            KeyError: If profile doesn't exist
        """
        if name not in self.profiles:
            raise KeyError(f"Voice profile '{name}' not found")
        return self.profiles[name]
    
    def get_all_profiles(self) -> Dict[str, VoiceProfile]:
        """Get all available voice profiles."""
        return self.profiles.copy()
    
    def get_profile_names(self) -> List[str]:
        """Get list of all profile names."""
        return list(self.profiles.keys())
    
    def add_profile(self, profile: VoiceProfile):
        """
        Add a new voice profile.
        
        Args:
            profile: VoiceProfile to add
        """
        self.profiles[profile.name] = profile
    
    def remove_profile(self, name: str):
        """
        Remove a voice profile.
        
        Args:
            name: Profile name to remove
        """
        if name in self.profiles:
            del self.profiles[name]
    
    def save_profiles(self, filename: str):
        """
        Save profiles to JSON file.
        
        Args:
            filename: Path to save file
        """
        profiles_data = {
            name: profile.to_dict() 
            for name, profile in self.profiles.items()
        }
        
        with open(filename, 'w') as f:
            json.dump(profiles_data, f, indent=2)
    
    def load_profiles(self, filename: str):
        """
        Load profiles from JSON file.
        
        Args:
            filename: Path to load file
        """
        with open(filename, 'r') as f:
            profiles_data = json.load(f)
        
        for name, data in profiles_data.items():
            profile = VoiceProfile.from_dict(data)
            self.profiles[name] = profile
    
    def create_custom_profile(self, name: str, display_name: str, description: str,
                            pitch_shift: float = 1.0, formant_shift: float = 1.0,
                            special_effects: List[str] = None,
                            emotion_modifiers: Dict[str, float] = None) -> VoiceProfile:
        """
        Create a custom voice profile.
        
        Args:
            name: Internal profile name
            display_name: Human-readable name
            description: Profile description
            pitch_shift: Pitch shift factor
            formant_shift: Formant shift factor
            special_effects: List of special effects to apply
            emotion_modifiers: Emotion modification parameters
            
        Returns:
            Created VoiceProfile
        """
        if special_effects is None:
            special_effects = []
        if emotion_modifiers is None:
            emotion_modifiers = {}
        
        profile = VoiceProfile(
            name=name,
            display_name=display_name,
            description=description,
            pitch_shift=pitch_shift,
            formant_shift=formant_shift,
            special_effects=special_effects,
            emotion_modifiers=emotion_modifiers
        )
        
        self.add_profile(profile)
        return profile
    
    def get_profiles_by_category(self) -> Dict[str, List[VoiceProfile]]:
        """
        Get profiles organized by category.
        
        Returns:
            Dictionary with categories as keys and profile lists as values
        """
        categories = {
            "Human": [],
            "Character": [],
            "Effects": [],
            "Professional": []
        }
        
        # Categorize profiles based on their characteristics
        for profile in self.profiles.values():
            if profile.name in ["original", "male_deep", "female_high", "child", "elderly"]:
                categories["Human"].append(profile)
            elif profile.name in ["robot", "alien", "monster"]:
                categories["Character"].append(profile)
            elif profile.name in ["whisper", "announcer"]:
                categories["Professional"].append(profile)
            else:
                categories["Effects"].append(profile)
        
        return categories
    
    def search_profiles(self, query: str) -> List[VoiceProfile]:
        """
        Search profiles by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching profiles
        """
        query = query.lower()
        matches = []
        
        for profile in self.profiles.values():
            if (query in profile.name.lower() or 
                query in profile.display_name.lower() or 
                query in profile.description.lower()):
                matches.append(profile)
        
        return matches


# Emotion processing utilities
class EmotionProcessor:
    """Processes emotional modifications to voice."""
    
    @staticmethod
    def apply_emotion_modifiers(audio_data, emotion_modifiers: Dict[str, float]):
        """
        Apply emotion-based modifications to audio.
        
        Args:
            audio_data: Input audio samples
            emotion_modifiers: Dictionary of emotion parameters
            
        Returns:
            Modified audio samples
        """
        # This is a placeholder for emotion processing
        # In a full implementation, this would apply various audio effects
        # based on the emotion parameters
        
        modified_audio = audio_data.copy()
        
        # Example emotion processing (simplified)
        if "confidence" in emotion_modifiers:
            # Boost mid frequencies for confidence
            confidence_factor = emotion_modifiers["confidence"]
            modified_audio *= confidence_factor
        
        if "playfulness" in emotion_modifiers:
            # Add slight pitch variation for playfulness
            playfulness_factor = emotion_modifiers["playfulness"]
            # This would involve more complex processing in practice
        
        return modified_audio


if __name__ == "__main__":
    # Test the voice profile manager
    manager = VoiceProfileManager()
    
    print("Available voice profiles:")
    for name, profile in manager.get_all_profiles().items():
        print(f"- {profile.display_name}: {profile.description}")
    
    print("\nProfiles by category:")
    categories = manager.get_profiles_by_category()
    for category, profiles in categories.items():
        print(f"\n{category}:")
        for profile in profiles:
            print(f"  - {profile.display_name}")
    
    # Create a custom profile
    custom_profile = manager.create_custom_profile(
        name="custom_test",
        display_name="Test Custom Voice",
        description="A test custom voice profile",
        pitch_shift=1.2,
        formant_shift=1.1,
        special_effects=["reverb"],
        emotion_modifiers={"excitement": 1.3}
    )
    
    print(f"\nCreated custom profile: {custom_profile.display_name}")
    
    # Save profiles to file
    manager.save_profiles("voice_profiles.json")
    print("Profiles saved to voice_profiles.json")

