<#
.SYNOPSIS
    Speech-to-Text using OpenAI Whisper (runs locally, completely free).

.DESCRIPTION
    Records audio from your microphone and transcribes it using OpenAI's
    Whisper model running locally. No API calls, no cloud, no cost.

.PARAMETER Duration
    Recording duration in seconds. Default: 5

.PARAMETER Model
    Whisper model to use. Options: tiny, base, small, medium, large, turbo
    Default: base (good balance of speed and accuracy)

.PARAMETER File
    Transcribe an existing audio file instead of recording.

.PARAMETER ListDevices
    List available audio input devices.

.PARAMETER Device
    Audio input device index to use.

.PARAMETER Output
    Write transcription to a file.

.EXAMPLE
    Invoke-SpeechToText
    # Records 5 seconds and transcribes

.EXAMPLE
    Invoke-SpeechToText -Duration 10 -Model medium
    # Records 10 seconds with higher accuracy model

.EXAMPLE
    Invoke-SpeechToText -File "recording.wav"
    # Transcribes an existing audio file

.EXAMPLE
    Invoke-SpeechToText -ListDevices
    # Shows available microphones
#>

param(
    [int]$Duration = 5,
    [ValidateSet("tiny", "base", "small", "medium", "large", "turbo")]
    [string]$Model = "base",
    [string]$File,
    [switch]$ListDevices,
    [int]$Device,
    [string]$Output
)

$scriptPath = Join-Path $PSScriptRoot "speech_to_text.py"

$args = @()

if ($ListDevices) {
    $args += "--list-devices"
} else {
    if ($File) {
        $args += "--file", $File
    } else {
        $args += "--duration", $Duration
    }

    $args += "--model", $Model

    if ($PSBoundParameters.ContainsKey('Device')) {
        $args += "--device", $Device
    }

    if ($Output) {
        $args += "--output", $Output
    }
}

python $scriptPath @args
