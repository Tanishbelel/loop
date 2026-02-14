import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createMeeting } from '../services/api';
import { Calendar, Clock, X, Loader, AlertCircle } from 'lucide-react';

export default function CreateMeetingModal({ projects, isOpen, onClose, onSuccess }) {
    const [formData, setFormData] = useState({
        project: '',
        meeting_type: 'DAILY_STANDUP',
        title: '',
        description: '',
        scheduled_time: '',
        duration_minutes: 15,
        agenda: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await createMeeting(formData);
            onSuccess();
            onClose();
            // Reset form
            setFormData({
                project: '',
                meeting_type: 'DAILY_STANDUP',
                title: '',
                description: '',
                scheduled_time: '',
                duration_minutes: 15,
                agenda: ''
            });
        } catch (err) {
            setError('Failed to create meeting');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="bg-white rounded-2xl p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-gray-900">Schedule Scrum Meeting</h2>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                            <X size={24} />
                        </button>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                            <AlertCircle size={16} />
                            <span className="text-sm">{error}</span>
                        </div>
                    )}

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Project
                            </label>
                            <select
                                value={formData.project}
                                onChange={(e) => setFormData({ ...formData, project: e.target.value })}
                                className="input-field"
                                required
                            >
                                <option value="">Select a project...</option>
                                {projects.map(project => (
                                    <option key={project.id} value={project.id}>
                                        {project.name}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Meeting Type
                            </label>
                            <select
                                value={formData.meeting_type}
                                onChange={(e) => setFormData({ ...formData, meeting_type: e.target.value })}
                                className="input-field"
                                required
                            >
                                <option value="DAILY_STANDUP">Daily Standup</option>
                                <option value="SPRINT_PLANNING">Sprint Planning</option>
                                <option value="SPRINT_REVIEW">Sprint Review</option>
                                <option value="SPRINT_RETRO">Sprint Retrospective</option>
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Title
                            </label>
                            <input
                                type="text"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                className="input-field"
                                placeholder="e.g., Daily Standup - Sprint 5"
                                required
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Scheduled Time
                                </label>
                                <input
                                    type="datetime-local"
                                    value={formData.scheduled_time}
                                    onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                                    className="input-field"
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Duration (minutes)
                                </label>
                                <input
                                    type="number"
                                    value={formData.duration_minutes}
                                    onChange={(e) => setFormData({ ...formData, duration_minutes: parseInt(e.target.value) })}
                                    className="input-field"
                                    min="5"
                                    max="120"
                                    required
                                />
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Agenda
                            </label>
                            <textarea
                                value={formData.agenda}
                                onChange={(e) => setFormData({ ...formData, agenda: e.target.value })}
                                className="input-field"
                                rows="4"
                                placeholder="Meeting agenda and topics to discuss..."
                            />
                        </div>

                        <div className="flex gap-3 pt-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="btn-primary flex-1 flex items-center justify-center gap-2"
                            >
                                {loading ? (
                                    <>
                                        <Loader className="animate-spin" size={20} />
                                        Creating...
                                    </>
                                ) : (
                                    <>
                                        <Calendar size={20} />
                                        Schedule Meeting
                                    </>
                                )}
                            </button>
                            <button type="button" onClick={onClose} className="btn-secondary flex-1">
                                Cancel
                            </button>
                        </div>
                    </form>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
