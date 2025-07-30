"""
Flask API server for the voice masking system.
Provides REST API endpoints for voice transformation control.
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import threading
import time
import os
import json
from audio_processor import AudioProcessor
from voice_profiles import VoiceProfileManager
import sounddevice as sd


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global instances
audio_processor = AudioProcessor()
profile_manager = VoiceProfileManager()

# Server state
server_state = {
    "is_processing": False,
    "current_profile": "original",
    "latency_ms": 0,
    "input_device": None,
    "output_device": None
}


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    })


@app.route('/api/devices', methods=['GET'])
def get_audio_devices():
    """Get available audio input and output devices."""
    try:
        devices = sd.query_devices()
        device_list = []
        
        for i, device in enumerate(devices):
            device_info = {
                "id": i,
                "name": device['name'],
                "max_input_channels": device['max_input_channels'],
                "max_output_channels": device['max_output_channels'],
                "default_samplerate": device['default_samplerate'],
                "hostapi": device['hostapi']
            }
            device_list.append(device_info)
        
        return jsonify({
            "devices": device_list,
            "default_input": sd.default.device[0],
            "default_output": sd.default.device[1]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/devices/input', methods=['POST'])
def set_input_device():
    """Set the input audio device."""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if device_id is None:
            return jsonify({"error": "device_id is required"}), 400
        
        audio_processor.set_input_device(device_id)
        server_state["input_device"] = device_id
        
        return jsonify({
            "message": "Input device set successfully",
            "device_id": device_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/devices/output', methods=['POST'])
def set_output_device():
    """Set the output audio device."""
    try:
        data = request.get_json()
        device_id = data.get('device_id')
        
        if device_id is None:
            return jsonify({"error": "device_id is required"}), 400
        
        audio_processor.set_output_device(device_id)
        server_state["output_device"] = device_id
        
        return jsonify({
            "message": "Output device set successfully",
            "device_id": device_id
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/profiles', methods=['GET'])
def get_voice_profiles():
    """Get all available voice profiles."""
    try:
        profiles = profile_manager.get_all_profiles()
        profiles_data = {}
        
        for name, profile in profiles.items():
            profiles_data[name] = profile.to_dict()
        
        categories = profile_manager.get_profiles_by_category()
        categories_data = {}
        for category, profile_list in categories.items():
            categories_data[category] = [p.to_dict() for p in profile_list]
        
        return jsonify({
            "profiles": profiles_data,
            "categories": categories_data,
            "current_profile": server_state["current_profile"]
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/profiles/<profile_name>', methods=['GET'])
def get_voice_profile(profile_name):
    """Get a specific voice profile."""
    try:
        profile = profile_manager.get_profile(profile_name)
        return jsonify(profile.to_dict())
    
    except KeyError:
        return jsonify({"error": f"Profile '{profile_name}' not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/profiles', methods=['POST'])
def create_voice_profile():
    """Create a new custom voice profile."""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'display_name', 'description']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"'{field}' is required"}), 400
        
        profile = profile_manager.create_custom_profile(
            name=data['name'],
            display_name=data['display_name'],
            description=data['description'],
            pitch_shift=data.get('pitch_shift', 1.0),
            formant_shift=data.get('formant_shift', 1.0),
            special_effects=data.get('special_effects', []),
            emotion_modifiers=data.get('emotion_modifiers', {})
        )
        
        return jsonify({
            "message": "Profile created successfully",
            "profile": profile.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/profiles/<profile_name>', methods=['DELETE'])
def delete_voice_profile(profile_name):
    """Delete a voice profile."""
    try:
        if profile_name == "original":
            return jsonify({"error": "Cannot delete the original profile"}), 400
        
        profile_manager.remove_profile(profile_name)
        
        # If the deleted profile was active, switch to original
        if server_state["current_profile"] == profile_name:
            server_state["current_profile"] = "original"
            audio_processor.set_voice_profile("original")
        
        return jsonify({"message": f"Profile '{profile_name}' deleted successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/processing/start', methods=['POST'])
def start_processing():
    """Start voice processing."""
    try:
        if server_state["is_processing"]:
            return jsonify({"message": "Processing is already running"})
        
        data = request.get_json() or {}
        profile_name = data.get('profile', 'original')
        
        # Set voice profile
        audio_processor.set_voice_profile(profile_name)
        server_state["current_profile"] = profile_name
        
        # Start processing
        audio_processor.start()
        server_state["is_processing"] = True
        
        return jsonify({
            "message": "Voice processing started",
            "profile": profile_name,
            "timestamp": time.time()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/processing/stop', methods=['POST'])
def stop_processing():
    """Stop voice processing."""
    try:
        if not server_state["is_processing"]:
            return jsonify({"message": "Processing is not running"})
        
        audio_processor.stop()
        server_state["is_processing"] = False
        
        return jsonify({
            "message": "Voice processing stopped",
            "timestamp": time.time()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/processing/status', methods=['GET'])
def get_processing_status():
    """Get current processing status."""
    return jsonify({
        "is_processing": server_state["is_processing"],
        "current_profile": server_state["current_profile"],
        "latency_ms": server_state["latency_ms"],
        "input_device": server_state["input_device"],
        "output_device": server_state["output_device"],
        "timestamp": time.time()
    })


@app.route('/api/processing/profile', methods=['POST'])
def change_voice_profile():
    """Change the current voice profile."""
    try:
        data = request.get_json()
        profile_name = data.get('profile')
        
        if not profile_name:
            return jsonify({"error": "profile name is required"}), 400
        
        # Validate profile exists
        try:
            profile_manager.get_profile(profile_name)
        except KeyError:
            return jsonify({"error": f"Profile '{profile_name}' not found"}), 404
        
        # Update audio processor
        audio_processor.set_voice_profile(profile_name)
        server_state["current_profile"] = profile_name
        
        return jsonify({
            "message": f"Voice profile changed to '{profile_name}'",
            "profile": profile_name,
            "timestamp": time.time()
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/settings', methods=['GET'])
def get_settings():
    """Get current system settings."""
    return jsonify({
        "sample_rate": audio_processor.sample_rate,
        "block_size": audio_processor.block_size,
        "pitch_shift": audio_processor.pitch_shift,
        "formant_shift": audio_processor.formant_shift,
        "voice_profile": audio_processor.voice_profile
    })


@app.route('/api/settings', methods=['POST'])
def update_settings():
    """Update system settings."""
    try:
        data = request.get_json()
        
        # Update audio processor settings
        if 'sample_rate' in data:
            audio_processor.sample_rate = data['sample_rate']
        
        if 'block_size' in data:
            audio_processor.block_size = data['block_size']
        
        # Note: Changing these settings requires restarting the audio processor
        if server_state["is_processing"]:
            return jsonify({
                "message": "Settings updated (restart processing to apply changes)",
                "restart_required": True
            })
        else:
            return jsonify({
                "message": "Settings updated successfully",
                "restart_required": False
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/profiles/search', methods=['GET'])
def search_profiles():
    """Search voice profiles."""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({"error": "Search query 'q' is required"}), 400
        
        matches = profile_manager.search_profiles(query)
        results = [profile.to_dict() for profile in matches]
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/export/profiles', methods=['GET'])
def export_profiles():
    """Export all profiles to JSON file."""
    try:
        export_path = "/tmp/voice_profiles_export.json"
        profile_manager.save_profiles(export_path)
        
        return send_file(
            export_path,
            as_attachment=True,
            download_name="voice_profiles.json",
            mimetype="application/json"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/import/profiles', methods=['POST'])
def import_profiles():
    """Import profiles from JSON file."""
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save uploaded file temporarily
        temp_path = "/tmp/imported_profiles.json"
        file.save(temp_path)
        
        # Load profiles
        profile_manager.load_profiles(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return jsonify({"message": "Profiles imported successfully"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    print("Starting Voice Masking API Server...")
    print("Available endpoints:")
    print("  GET  /api/health - Health check")
    print("  GET  /api/devices - Get audio devices")
    print("  POST /api/devices/input - Set input device")
    print("  POST /api/devices/output - Set output device")
    print("  GET  /api/profiles - Get voice profiles")
    print("  POST /api/profiles - Create voice profile")
    print("  GET  /api/profiles/<name> - Get specific profile")
    print("  DELETE /api/profiles/<name> - Delete profile")
    print("  POST /api/processing/start - Start processing")
    print("  POST /api/processing/stop - Stop processing")
    print("  GET  /api/processing/status - Get status")
    print("  POST /api/processing/profile - Change profile")
    print("  GET  /api/settings - Get settings")
    print("  POST /api/settings - Update settings")
    print("  GET  /api/profiles/search - Search profiles")
    print("  GET  /api/export/profiles - Export profiles")
    print("  POST /api/import/profiles - Import profiles")
    print()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

