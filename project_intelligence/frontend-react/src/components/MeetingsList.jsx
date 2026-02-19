import { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getMeetings, joinMeeting, startMeeting, completeMeeting, generateMeetingSummary } from '../services/api';
import { Calendar, Users, Clock, Video, Play, CheckCircle, Sparkles, Loader, Radio } from 'lucide-react';
import { format } from 'date-fns';

export default function MeetingsList({ userRole, onRefresh }) {
    const [meetings, setMeetings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState({});
    const navigate = useNavigate();

    const loadMeetings = useCallback(async () => {
        try {
            const data = await getMeetings();
            setMeetings(data);
        } catch (error) {
            console.error('Failed to load meetings:', error);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadMeetings();
    }, [onRefresh, loadMeetings]);

    // Auto-start timer: check every 30s if a scheduled meeting's time has arrived
    useEffect(() => {
        const checkAndAutoStart = async () => {
            const now = new Date();
            for (const meeting of meetings) {
                if (meeting.status === 'SCHEDULED') {
                    const scheduledTime = new Date(meeting.scheduled_time);
                    if (now >= scheduledTime) {
                        if (userRole === 'PROJECT_MANAGER') {
                            // Auto-start for PM
                            try {
                                await startMeeting(meeting.id);
                                loadMeetings();
                            } catch (e) {
                                console.error('Auto-start failed:', e);
                            }
                        }
                    }
                }
            }
        };

        const interval = setInterval(checkAndAutoStart, 30000);
        // Also run immediately on mount
        if (meetings.length > 0) checkAndAutoStart();
        return () => clearInterval(interval);
    }, [meetings, userRole, loadMeetings]);

    const handleJoinMeeting = async (meetingId) => {
        setActionLoading({ ...actionLoading, [meetingId]: 'joining' });
        try {
            await joinMeeting(meetingId);
            loadMeetings();
        } catch (error) {
            console.error('Failed to join meeting:', error);
        } finally {
            setActionLoading({ ...actionLoading, [meetingId]: null });
        }
    };

    const handleStartMeeting = async (meetingId) => {
        setActionLoading({ ...actionLoading, [meetingId]: 'starting' });
        try {
            await startMeeting(meetingId);
            loadMeetings();
        } catch (error) {
            console.error('Failed to start meeting:', error);
        } finally {
            setActionLoading({ ...actionLoading, [meetingId]: null });
        }
    };

    const handleCompleteMeeting = async (meetingId) => {
        setActionLoading({ ...actionLoading, [meetingId]: 'completing' });
        try {
            await completeMeeting(meetingId, '');
            loadMeetings();
        } catch (error) {
            console.error('Failed to complete meeting:', error);
        } finally {
            setActionLoading({ ...actionLoading, [meetingId]: null });
        }
    };

    const handleGenerateSummary = async (meetingId) => {
        setActionLoading({ ...actionLoading, [meetingId]: 'generating' });
        try {
            await generateMeetingSummary(meetingId);
            loadMeetings();
        } catch (error) {
            console.error('Failed to generate summary:', error);
        } finally {
            setActionLoading({ ...actionLoading, [meetingId]: null });
        }
    };

    const handleEnterRoom = (meetingId) => {
        navigate(`/meeting-room/${meetingId}`);
    };

    const isTimeArrived = (scheduledTime) => {
        return new Date() >= new Date(scheduledTime);
    };

    const getStatusColor = (status) => {
        const colors = {
            SCHEDULED: 'bg-blue-100 text-blue-800',
            IN_PROGRESS: 'bg-green-100 text-green-800',
            COMPLETED: 'bg-gray-100 text-gray-800',
            CANCELLED: 'bg-red-100 text-red-800',
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    const getMeetingTypeLabel = (type) => {
        return type.replace(/_/g, ' ');
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <Loader className="animate-spin text-purple-600" size={32} />
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900">Scrum Meetings</h2>

            {meetings.length === 0 ? (
                <div className="card text-center py-12">
                    <Calendar className="mx-auto text-gray-400 mb-4" size={48} />
                    <p className="text-gray-600">No meetings scheduled yet</p>
                </div>
            ) : (
                meetings.map((meeting, index) => (
                    <motion.div
                        key={meeting.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: index * 0.05 }}
                        className="card"
                    >
                        <div className="flex items-start justify-between mb-3">
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">{meeting.title}</h3>
                                <p className="text-sm text-gray-600">{meeting.project_name}</p>
                            </div>
                            <div className="flex items-center gap-2">
                                {meeting.status === 'SCHEDULED' && isTimeArrived(meeting.scheduled_time) && (
                                    <span className="flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold bg-orange-100 text-orange-700 animate-pulse">
                                        <Radio size={12} /> Time to start!
                                    </span>
                                )}
                                <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(meeting.status)}`}>
                                    {meeting.status}
                                </span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                            <div className="flex items-center gap-2 text-gray-600">
                                <Calendar size={16} />
                                {format(new Date(meeting.scheduled_time), 'MMM dd, yyyy')}
                            </div>
                            <div className="flex items-center gap-2 text-gray-600">
                                <Clock size={16} />
                                {format(new Date(meeting.scheduled_time), 'hh:mm a')} ({meeting.duration_minutes}min)
                            </div>
                            <div className="flex items-center gap-2 text-gray-600">
                                <Users size={16} />
                                {meeting.participant_count} participants
                            </div>
                            <div className="text-gray-600">
                                Type: {getMeetingTypeLabel(meeting.meeting_type)}
                            </div>
                        </div>

                        {meeting.agenda && (
                            <div className="mb-4 p-3 bg-gray-50 rounded-lg">
                                <p className="text-sm font-semibold text-gray-700 mb-1">Agenda:</p>
                                <p className="text-sm text-gray-600">{meeting.agenda}</p>
                            </div>
                        )}

                        {/* Action Buttons */}
                        <div className="flex gap-2 flex-wrap">
                            {meeting.status === 'SCHEDULED' && userRole === 'EMPLOYEE' && (
                                <button
                                    onClick={() => handleJoinMeeting(meeting.id)}
                                    disabled={actionLoading[meeting.id]}
                                    className="btn-primary flex items-center gap-2 text-sm px-4 py-2"
                                >
                                    {actionLoading[meeting.id] === 'joining' ? (
                                        <Loader className="animate-spin" size={16} />
                                    ) : (
                                        <Video size={16} />
                                    )}
                                    Join Meeting
                                </button>
                            )}

                            {meeting.status === 'SCHEDULED' && userRole === 'PROJECT_MANAGER' && (
                                <button
                                    onClick={() => handleStartMeeting(meeting.id)}
                                    disabled={actionLoading[meeting.id]}
                                    className="btn-primary flex items-center gap-2 text-sm px-4 py-2"
                                >
                                    {actionLoading[meeting.id] === 'starting' ? (
                                        <Loader className="animate-spin" size={16} />
                                    ) : (
                                        <Play size={16} />
                                    )}
                                    Start Meeting
                                </button>
                            )}

                            {/* Enter Meeting Room button for IN_PROGRESS meetings */}
                            {meeting.status === 'IN_PROGRESS' && (
                                <button
                                    onClick={() => handleEnterRoom(meeting.id)}
                                    className="bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition-all flex items-center gap-2 text-sm animate-pulse"
                                >
                                    <Video size={16} />
                                    Enter Meeting Room
                                </button>
                            )}

                            {meeting.status === 'IN_PROGRESS' && userRole === 'PROJECT_MANAGER' && (
                                <button
                                    onClick={() => handleCompleteMeeting(meeting.id)}
                                    disabled={actionLoading[meeting.id]}
                                    className="bg-gray-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-gray-700 transition-all flex items-center gap-2 text-sm"
                                >
                                    {actionLoading[meeting.id] === 'completing' ? (
                                        <Loader className="animate-spin" size={16} />
                                    ) : (
                                        <CheckCircle size={16} />
                                    )}
                                    Complete (No Room)
                                </button>
                            )}

                            {meeting.status === 'COMPLETED' && userRole === 'PROJECT_MANAGER' && !meeting.ai_summary && (
                                <button
                                    onClick={() => handleGenerateSummary(meeting.id)}
                                    disabled={actionLoading[meeting.id]}
                                    className="bg-purple-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-purple-700 transition-all flex items-center gap-2 text-sm"
                                >
                                    {actionLoading[meeting.id] === 'generating' ? (
                                        <Loader className="animate-spin" size={16} />
                                    ) : (
                                        <Sparkles size={16} />
                                    )}
                                    Generate AI Summary
                                </button>
                            )}
                        </div>

                        {/* AI Summary */}
                        {meeting.ai_summary && (
                            <div className="mt-4 p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border-2 border-purple-200">
                                <div className="flex items-center gap-2 mb-2">
                                    <Sparkles className="text-purple-600" size={20} />
                                    <p className="text-sm font-bold text-purple-900">AI Meeting Summary</p>
                                </div>
                                <p className="text-sm text-gray-700 mb-3">{meeting.ai_summary}</p>

                                {meeting.action_items && meeting.action_items.length > 0 && (
                                    <div>
                                        <p className="text-sm font-semibold text-gray-800 mb-2">Action Items:</p>
                                        <div className="space-y-2">
                                            {meeting.action_items.map((item, idx) => (
                                                <div key={idx} className="flex items-start gap-2 text-sm">
                                                    <CheckCircle size={16} className="text-purple-600 mt-0.5" />
                                                    <div>
                                                        <p className="text-gray-800">{item.item}</p>
                                                        <p className="text-xs text-gray-600">
                                                            Owner: {item.owner} • Priority: <span className="font-semibold">{item.priority}</span>
                                                        </p>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}
                    </motion.div>
                ))
            )}
        </div>
    );
}
