import { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getMeetingDetail, completeMeeting, generateMeetingSummary, saveTranscript } from '../services/api';
import {
    Mic, MicOff, Video, VideoOff, PhoneOff, Sparkles,
    Loader, AlertCircle, FileText, Users, Globe
} from 'lucide-react';

const LANGUAGE_OPTIONS = [
    { label: 'English', value: 'en-US' },
    { label: 'Hindi', value: 'hi-IN' },
    { label: 'Hindi + English (Hinglish)', value: 'hi' },
    { label: 'Marathi', value: 'mr-IN' },
    { label: 'Tamil', value: 'ta-IN' },
    { label: 'Telugu', value: 'te-IN' },
    { label: 'Gujarati', value: 'gu-IN' },
];

export default function MeetingRoom() {
    const { meetingId } = useParams();
    const navigate = useNavigate();

    const [meeting, setMeeting] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    // Media state
    const [micOn, setMicOn] = useState(true);
    const [camOn, setCamOn] = useState(true);
    const [stream, setStream] = useState(null);
    const videoRef = useRef(null);

    // Language selection
    const [selectedLang, setSelectedLang] = useState('en-US');
    const [langLocked, setLangLocked] = useState(false); // lock once listening starts

    // Transcription state
    const [transcript, setTranscript] = useState('');
    const [interimText, setInterimText] = useState(''); // live interim display
    const [isListening, setIsListening] = useState(false);
    const [speechSupported, setSpeechSupported] = useState(true);
    const recognitionRef = useRef(null);
    const transcriptRef = useRef('');
    const shouldListenRef = useRef(true); // controls auto-restart

    // Ending state
    const [ending, setEnding] = useState(false);
    const [ended, setEnded] = useState(false);
    const [summary, setSummary] = useState(null);

    // Load meeting info
    useEffect(() => {
        const load = async () => {
            try {
                const data = await getMeetingDetail(meetingId);
                setMeeting(data);
            } catch {
                setError('Could not load meeting details.');
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [meetingId]);

    // Start camera + mic
    useEffect(() => {
        let localStream = null;
        const startMedia = async () => {
            try {
                localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
                setStream(localStream);
                if (videoRef.current) {
                    videoRef.current.srcObject = localStream;
                }
            } catch {
                setError('Could not access camera/microphone. Please allow permissions and try again.');
            }
        };
        startMedia();
        return () => {
            if (localStream) localStream.getTracks().forEach(t => t.stop());
        };
    }, []);

    // Attach stream to video element when both are ready
    useEffect(() => {
        if (stream && videoRef.current) {
            videoRef.current.srcObject = stream;
        }
    }, [stream]);

    // Toggle mic
    const toggleMic = () => {
        if (stream) {
            stream.getAudioTracks().forEach(t => { t.enabled = !t.enabled; });
            setMicOn(prev => !prev);
        }
    };

    // Toggle camera
    const toggleCam = () => {
        if (stream) {
            stream.getVideoTracks().forEach(t => { t.enabled = !t.enabled; });
            setCamOn(prev => !prev);
        }
    };

    // Build and start a recognition instance
    const createRecognition = useCallback((lang) => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            setSpeechSupported(false);
            return null;
        }

        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true; // capture interim so nothing is lost
        recognition.maxAlternatives = 1;
        recognition.lang = lang;

        recognition.onresult = (event) => {
            let interim = '';
            let newFinal = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const text = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    newFinal += text + ' ';
                } else {
                    interim += text;
                }
            }

            if (newFinal) {
                transcriptRef.current += newFinal;
                setTranscript(transcriptRef.current);
                setInterimText('');
            } else {
                // Show interim live so user sees it's working
                setInterimText(interim);
            }
        };

        recognition.onerror = (e) => {
            // 'no-speech' is normal when user is quiet — ignore it
            if (e.error === 'no-speech') return;
            // 'aborted' happens on manual stop — ignore it
            if (e.error === 'aborted') return;
            console.error('Speech recognition error:', e.error);
        };

        recognition.onend = () => {
            setInterimText('');
            // Auto-restart only if we're still supposed to be listening
            if (shouldListenRef.current) {
                try {
                    recognition.start();
                } catch {
                    // If start fails (e.g., already started), wait a moment then retry
                    setTimeout(() => {
                        if (shouldListenRef.current) {
                            try { recognition.start(); } catch { /* ignore */ }
                        }
                    }, 300);
                }
            }
        };

        return recognition;
    }, []);

    // Start listening
    const startListening = useCallback((lang) => {
        const recognition = createRecognition(lang);
        if (!recognition) return;
        recognitionRef.current = recognition;
        shouldListenRef.current = true;
        try {
            recognition.start();
            setIsListening(true);
            setLangLocked(true);
        } catch (e) {
            console.error('Could not start recognition:', e);
        }
    }, [createRecognition]);

    // Auto-start listening once media is ready
    useEffect(() => {
        if (stream && !isListening && !ended) {
            startListening(selectedLang);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [stream]);

    // Change language mid-meeting: restart recognition with new lang
    const handleLangChange = (newLang) => {
        setSelectedLang(newLang);
        if (isListening && recognitionRef.current) {
            // Stop current, will restart via onend with new lang
            shouldListenRef.current = false;
            recognitionRef.current.onend = null;
            recognitionRef.current.stop();
            recognitionRef.current = null;
            setIsListening(false);
            // Start fresh with new language
            setTimeout(() => {
                startListening(newLang);
            }, 400);
        }
    };

    // End meeting
    const handleEndMeeting = async () => {
        setEnding(true);
        try {
            // Stop speech recognition cleanly
            shouldListenRef.current = false;
            if (recognitionRef.current) {
                recognitionRef.current.onend = null;
                recognitionRef.current.stop();
                recognitionRef.current = null;
            }
            setIsListening(false);

            // Flush any remaining interim text into the final transcript
            const finalTranscript = transcriptRef.current + (interimText ? interimText + ' ' : '');
            transcriptRef.current = finalTranscript;
            setInterimText('');

            // Stop media tracks
            if (stream) stream.getTracks().forEach(t => t.stop());

            // Save transcript
            await saveTranscript(meetingId, finalTranscript);

            // Complete meeting
            await completeMeeting(meetingId, finalTranscript);

            // Generate AI summary
            const result = await generateMeetingSummary(meetingId);
            setSummary(result);
            setEnded(true);
        } catch (err) {
            console.error('Error ending meeting:', err);
            setError('Failed to end meeting. Please try again.');
        } finally {
            setEnding(false);
        }
    };

    const goBack = () => navigate('/dashboard');

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gray-950">
                <Loader className="animate-spin text-purple-400" size={48} />
            </div>
        );
    }

    if (error && !stream) {
        return (
            <div className="flex flex-col items-center justify-center min-h-screen bg-gray-950 text-white gap-4 p-8">
                <AlertCircle className="text-red-400" size={48} />
                <p className="text-lg text-red-300 text-center">{error}</p>
                <button onClick={goBack} className="px-6 py-2 bg-purple-600 rounded-lg hover:bg-purple-700 transition-all">
                    Back to Dashboard
                </button>
            </div>
        );
    }

    // Post-meeting summary screen
    if (ended && summary) {
        return (
            <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center p-6">
                <div className="max-w-2xl w-full bg-gray-900 rounded-2xl p-8 shadow-2xl border border-purple-800">
                    <div className="flex items-center gap-3 mb-6">
                        <Sparkles className="text-purple-400" size={32} />
                        <h2 className="text-2xl font-bold text-white">Meeting Ended — AI Summary</h2>
                    </div>

                    <div className="bg-gray-800 rounded-xl p-5 mb-6">
                        <p className="text-sm font-semibold text-purple-300 mb-2">Summary</p>
                        <p className="text-gray-200 leading-relaxed">{summary.summary}</p>
                    </div>

                    {summary.action_items && summary.action_items.length > 0 && (
                        <div className="bg-gray-800 rounded-xl p-5 mb-6">
                            <p className="text-sm font-semibold text-purple-300 mb-3">Action Items</p>
                            <div className="space-y-3">
                                {summary.action_items.map((item, i) => (
                                    <div key={i} className="flex items-start gap-3 bg-gray-700 rounded-lg p-3">
                                        <span className={`text-xs font-bold px-2 py-1 rounded-full mt-0.5 ${item.priority === 'HIGH' ? 'bg-red-900 text-red-300' :
                                                item.priority === 'MEDIUM' ? 'bg-yellow-900 text-yellow-300' :
                                                    'bg-green-900 text-green-300'
                                            }`}>{item.priority}</span>
                                        <div>
                                            <p className="text-white text-sm">{item.item}</p>
                                            <p className="text-gray-400 text-xs mt-0.5">Owner: {item.owner}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {transcriptRef.current && (
                        <div className="bg-gray-800 rounded-xl p-5 mb-6 max-h-40 overflow-y-auto">
                            <p className="text-sm font-semibold text-purple-300 mb-2">Full Transcript</p>
                            <p className="text-gray-400 text-sm leading-relaxed">{transcriptRef.current}</p>
                        </div>
                    )}

                    <button
                        onClick={goBack}
                        className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-bold text-white transition-all"
                    >
                        Back to Dashboard
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-950 text-white flex flex-col">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 bg-gray-900 border-b border-gray-800">
                <div>
                    <h1 className="text-lg font-bold text-white">{meeting?.title || 'Meeting Room'}</h1>
                    <p className="text-sm text-gray-400">{meeting?.project_name} • {meeting?.meeting_type?.replace(/_/g, ' ')}</p>
                </div>
                <div className="flex items-center gap-4">
                    {/* Language selector */}
                    <div className="flex items-center gap-2">
                        <Globe size={16} className="text-purple-400" />
                        <select
                            value={selectedLang}
                            onChange={(e) => handleLangChange(e.target.value)}
                            className="bg-gray-800 text-white text-sm rounded-lg px-3 py-1.5 border border-gray-700 focus:outline-none focus:border-purple-500"
                            title="Select transcription language"
                        >
                            {LANGUAGE_OPTIONS.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                        <Users size={16} />
                        <span>{meeting?.participant_count || 1} participant(s)</span>
                    </div>
                </div>
            </div>

            {/* Main content */}
            <div className="flex flex-1 gap-4 p-4 overflow-hidden">
                {/* Video area */}
                <div className="flex-1 flex flex-col gap-4">
                    <div className="relative flex-1 bg-gray-900 rounded-2xl overflow-hidden flex items-center justify-center border border-gray-800 min-h-64">
                        <video
                            ref={videoRef}
                            autoPlay
                            muted
                            playsInline
                            className={`w-full h-full object-cover rounded-2xl ${!camOn ? 'opacity-0' : ''}`}
                        />
                        {!camOn && (
                            <div className="absolute inset-0 flex items-center justify-center">
                                <div className="w-24 h-24 rounded-full bg-gray-700 flex items-center justify-center">
                                    <VideoOff size={40} className="text-gray-400" />
                                </div>
                            </div>
                        )}
                        <div className="absolute bottom-3 left-3 bg-black/60 rounded-lg px-3 py-1 text-sm font-semibold">
                            You
                        </div>
                        {!micOn && (
                            <div className="absolute top-3 right-3 bg-red-600 rounded-full p-1.5">
                                <MicOff size={14} />
                            </div>
                        )}
                    </div>

                    {/* Controls */}
                    <div className="flex items-center justify-center gap-4">
                        <button
                            onClick={toggleMic}
                            className={`p-4 rounded-full transition-all ${micOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600 hover:bg-red-700'}`}
                            title={micOn ? 'Mute' : 'Unmute'}
                        >
                            {micOn ? <Mic size={22} /> : <MicOff size={22} />}
                        </button>
                        <button
                            onClick={toggleCam}
                            className={`p-4 rounded-full transition-all ${camOn ? 'bg-gray-700 hover:bg-gray-600' : 'bg-red-600 hover:bg-red-700'}`}
                            title={camOn ? 'Turn off camera' : 'Turn on camera'}
                        >
                            {camOn ? <Video size={22} /> : <VideoOff size={22} />}
                        </button>
                        <button
                            onClick={handleEndMeeting}
                            disabled={ending}
                            className="px-6 py-4 rounded-full bg-red-600 hover:bg-red-700 transition-all flex items-center gap-2 font-bold disabled:opacity-60"
                            title="End Meeting"
                        >
                            {ending ? <Loader className="animate-spin" size={22} /> : <PhoneOff size={22} />}
                            {ending ? 'Ending...' : 'End Meeting'}
                        </button>
                    </div>
                </div>

                {/* Transcript panel */}
                <div className="w-80 flex flex-col bg-gray-900 rounded-2xl border border-gray-800 overflow-hidden">
                    <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-800">
                        <FileText size={16} className="text-purple-400" />
                        <span className="text-sm font-semibold text-gray-200">Live AI Transcript</span>
                        {isListening && (
                            <span className="ml-auto flex items-center gap-1 text-xs text-green-400">
                                <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                                Listening
                            </span>
                        )}
                    </div>

                    {!speechSupported && (
                        <div className="p-4 text-sm text-yellow-300 bg-yellow-900/30 border-b border-yellow-800">
                            ⚠️ Speech recognition is not supported in this browser. Use Chrome or Edge.
                        </div>
                    )}

                    <div className="flex-1 overflow-y-auto p-4">
                        {(transcript || interimText) ? (
                            <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                                {transcript}
                                {interimText && (
                                    <span className="text-gray-500 italic">{interimText}</span>
                                )}
                            </p>
                        ) : (
                            <div className="flex flex-col items-center justify-center h-full text-center gap-3 text-gray-500">
                                <Mic size={32} className="text-gray-600" />
                                <p className="text-sm">Start speaking — the AI will transcribe everything said in this meeting.</p>
                                <p className="text-xs text-gray-600">
                                    Selected: {LANGUAGE_OPTIONS.find(l => l.value === selectedLang)?.label}
                                </p>
                            </div>
                        )}
                    </div>

                    <div className="px-4 py-3 border-t border-gray-800 text-xs text-gray-500 text-center">
                        Transcript is saved when you end the meeting
                    </div>
                </div>
            </div>

            {error && (
                <div className="mx-4 mb-4 p-3 bg-red-900/50 border border-red-700 rounded-xl text-red-300 text-sm flex items-center gap-2">
                    <AlertCircle size={16} />
                    {error}
                </div>
            )}
        </div>
    );
}
