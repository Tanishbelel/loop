import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createTask, getProjects, getSprints } from '../services/api';
import { ListTodo, X, Loader, AlertCircle } from 'lucide-react';

export default function CreateTaskModal({ isOpen, onClose, onSuccess }) {
    const [projects, setProjects] = useState([]);
    const [sprints, setSprints] = useState([]);
    const [formData, setFormData] = useState({
        project: '',
        sprint: '',
        title: '',
        description: '',
        priority: 'MEDIUM',
        estimated_hours: 8
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen) {
            loadProjects();
        }
    }, [isOpen]);

    useEffect(() => {
        if (formData.project) {
            loadSprints(formData.project);
        }
    }, [formData.project]);

    const loadProjects = async () => {
        try {
            const data = await getProjects();
            setProjects(data);
        } catch (err) {
            console.error('Failed to load projects:', err);
        }
    };

    const loadSprints = async (projectId) => {
        try {
            const data = await getSprints();
            const projectSprints = data.filter(s => s.project === parseInt(projectId));
            setSprints(projectSprints);
        } catch (err) {
            console.error('Failed to load sprints:', err);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await createTask(formData);
            onSuccess();
            onClose();
            // Reset form
            setFormData({
                project: '',
                sprint: '',
                title: '',
                description: '',
                priority: 'MEDIUM',
                estimated_hours: 8
            });
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to create task');
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
                        <h2 className="text-2xl font-bold text-gray-900">Create New Task</h2>
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
                                Project *
                            </label>
                            <select
                                value={formData.project}
                                onChange={(e) => setFormData({ ...formData, project: e.target.value, sprint: '' })}
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
                                Sprint (Optional)
                            </label>
                            <select
                                value={formData.sprint}
                                onChange={(e) => setFormData({ ...formData, sprint: e.target.value })}
                                className="input-field"
                                disabled={!formData.project}
                            >
                                <option value="">No sprint</option>
                                {sprints.map(sprint => (
                                    <option key={sprint.id} value={sprint.id}>
                                        Sprint {sprint.sprint_number}
                                    </option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Task Title *
                            </label>
                            <input
                                type="text"
                                value={formData.title}
                                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                className="input-field"
                                placeholder="e.g., Implement user authentication"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Description
                            </label>
                            <textarea
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                className="input-field"
                                rows="4"
                                placeholder="Task details and requirements..."
                            />
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Priority *
                                </label>
                                <select
                                    value={formData.priority}
                                    onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
                                    className="input-field"
                                    required
                                >
                                    <option value="LOW">Low</option>
                                    <option value="MEDIUM">Medium</option>
                                    <option value="HIGH">High</option>
                                    <option value="CRITICAL">Critical</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Estimated Hours *
                                </label>
                                <input
                                    type="number"
                                    value={formData.estimated_hours}
                                    onChange={(e) => setFormData({ ...formData, estimated_hours: parseFloat(e.target.value) })}
                                    className="input-field"
                                    min="0.5"
                                    step="0.5"
                                    required
                                />
                            </div>
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
                                        <ListTodo size={20} />
                                        Create Task
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
