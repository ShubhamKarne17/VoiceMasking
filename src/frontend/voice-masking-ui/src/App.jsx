import { useState, useEffect } from 'react'
import './App.css'

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api'

function App() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentProfile, setCurrentProfile] = useState('original')
  const [profiles, setProfiles] = useState({})
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchProfiles = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/profiles`)
      if (response.ok) {
        const data = await response.json()
        setProfiles(data.profiles)
        setCurrentProfile(data.current_profile)
        setError(null)
      } else {
        throw new Error('Failed to fetch profiles')
      }
    } catch (err) {
      setError('Failed to connect to the voice masking server. Please ensure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const toggleProcessing = async () => {
    try {
      const endpoint = isProcessing ? 'stop' : 'start'
      const response = await fetch(`${API_BASE_URL}/processing/${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: currentProfile })
      })
      
      if (response.ok) {
        setIsProcessing(!isProcessing)
      }
    } catch (err) {
      setError('Failed to toggle processing')
    }
  }

  const changeProfile = async (profileName) => {
    try {
      const response = await fetch(`${API_BASE_URL}/processing/profile`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ profile: profileName })
      })
      
      if (response.ok) {
        setCurrentProfile(profileName)
      }
    } catch (err) {
      setError('Failed to change voice profile')
    }
  }

  useEffect(() => {
    fetchProfiles()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-lg font-medium">Loading Voice Masking System...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-4">
            🛡️ Voice Privacy Masking System
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Transform your voice in real-time to protect your identity during live communication. 
            Choose from various voice profiles and maintain your privacy with AI-powered voice conversion.
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-center">
              <span className="text-red-600 mr-2">⚠️</span>
              <span className="text-red-800">{error}</span>
            </div>
          </div>
        )}

        {/* Main Control Panel */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-semibold mb-2">
              {isProcessing ? (
                <span className="text-green-600">🎤 Voice Masking Active</span>
              ) : (
                <span className="text-gray-400">🎤 Voice Masking Inactive</span>
              )}
            </h2>
            <p className="text-gray-600">
              Current Profile: <span className="font-medium bg-gray-100 px-2 py-1 rounded">
                {profiles[currentProfile]?.display_name || currentProfile}
              </span>
            </p>
          </div>

          {/* Main Control Button */}
          <div className="flex justify-center mb-6">
            <button
              onClick={toggleProcessing}
              className={`px-8 py-4 text-lg font-semibold rounded-lg transition-all duration-300 ${
                isProcessing 
                  ? 'bg-red-600 hover:bg-red-700 text-white' 
                  : 'bg-green-600 hover:bg-green-700 text-white'
              }`}
            >
              {isProcessing ? '⏸️ Stop Voice Masking' : '▶️ Start Voice Masking'}
            </button>
          </div>
        </div>

        {/* Voice Profiles */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h3 className="text-xl font-semibold mb-4">Voice Profiles</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(profiles).map(([name, profile]) => (
              <div 
                key={name}
                className={`p-4 border rounded-lg cursor-pointer transition-all duration-200 hover:shadow-md ${
                  currentProfile === name ? 'border-purple-500 bg-purple-50' : 'border-gray-200'
                }`}
                onClick={() => changeProfile(name)}
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold">{profile.display_name}</h4>
                  {currentProfile === name && <span className="text-green-600">✓</span>}
                </div>
                <p className="text-sm text-gray-600 mb-3">{profile.description}</p>
                <div className="flex gap-2 text-xs">
                  <span className="bg-gray-100 px-2 py-1 rounded">
                    Pitch: {profile.pitch_shift}x
                  </span>
                  <span className="bg-gray-100 px-2 py-1 rounded">
                    Formant: {profile.formant_shift}x
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Privacy Notice */}
        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <span className="text-blue-600 mr-2">🛡️</span>
            <div>
              <h4 className="font-semibold text-blue-800 mb-1">Privacy First</h4>
              <p className="text-blue-700 text-sm">
                All voice processing happens locally on your device. Your original voice data never leaves your computer.
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t">
          <p className="text-sm text-gray-500">
            Voice Privacy Masking System v1.0.0 | Built with AI-powered voice transformation
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
