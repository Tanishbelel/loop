import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getManagerDashboard, linkGitHubRepo } from '../services/api';
import { Heart, AlertTriangle, Users, Loader, Calendar, UserPlus, FolderPlus, ListTodo, Github, Link, X, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import AssignTaskModal from '../components/AssignTaskModal';
import CreateMeetingModal from '../components/CreateMeetingModal';
import CreateProjectModal from '../components/CreateProjectModal';
import CreateTaskModal from '../components/CreateTaskModal';
import MeetingsList from '../components/MeetingsList';
import GitHubCommitsPanel from '../components/GitHubCommitsPanel';

// Modal for linking GitHub to an existing project
function LinkGitHubModal({ project, isOpen, onClose, onSuccess }) {
    const [repoUrl, setRepoUrl] = useState('');
    const [token, setToken] = useState('');
    const [showToken, setShowToken] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await linkGitHubRepo(project.id, { action: 'link', token, repo_url: repoUrl });
            onSuccess();
            onClose();
            setRepoUrl(''); setToken('');
        } catch (err) {
            setError(err.response?.data?.error || 'Failed to link repository');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }}
                    className="bg-white rounded-2xl p-6 max-w-md w-full"
                    onClick={e => e.stopPropagation()}
                >
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                            <Github size={20} /> Link GitHub Repo
                        </h3>
                        <button onClick={onClose}><X size={20} className="text-gray-400 hover:text-gray-600" /></button>
                    </div>
                    <p className="text-sm text-gray-500 mb-4">Linking to: <strong>{project.name}</strong></p>
                    {error && (
                        <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
                    )}
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">Repository (owner/repo or URL)</label>
                            <input
                                type="text" value={repoUrl} onChange={e => setRepoUrl(e.target.value)}
                                className="input-field" placeholder="Tanishbelel/loop" required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-1">GitHub Personal Access Token</label>
                            <div className="relative">
                                <input
                                    type={showToken ? 'text' : 'password'} value={token} onChange={e => setToken(e.target.value)}
                                    className="input-field pr-10" placeholder="ghp_xxxx" required
                                />
                                <button type="button" onClick={() => setShowToken(v => !v)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                                    {showToken ? <EyeOff size={14} /> : <Eye size={14} />}
                                </button>
                            </div>
                        </div>
                        <div className="flex gap-3">
                            <button type="submit" disabled={loading}
                                className="btn-primary flex-1 flex items-center justify-center gap-2">
                                {loading ? <><Loader className="animate-spin" size={16} />Linking...</> : <><Link size={16} />Link Repository</>}
                            </button>
                            <button type="button" onClick={onClose} className="btn-secondary flex-1">Cancel</button>
                        </div>
                    </form>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}

export default function ManagerDashboard() {
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState(null);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [showMeetingModal, setShowMeetingModal] = useState(false);
    const [showProjectModal, setShowProjectModal] = useState(false);
    const [showTaskModal, setShowTaskModal] = useState(false);
    const [meetingsRefresh, setMeetingsRefresh] = useState(0);
    const [linkGitHubProject, setLinkGitHubProject] = useState(null);
    const [syncToast, setSyncToast] = useState(null); // { message, type }

    useEffect(() => {
        loadDashboard();
        const interval = setInterval(loadDashboard, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboard = async () => {
        try {
            const data = await getManagerDashboard();
            setDashboard(data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAssignTask = (task) => { setSelectedTask(task); setShowAssignModal(true); };
    const handleAssignSuccess = () => { loadDashboard(); setMeetingsRefresh(prev => prev + 1); };
    const handleMeetingSuccess = () => setMeetingsRefresh(prev => prev + 1);

    const handleSyncSuccess = (result) => {
        loadDashboard();
        const msg = result.tasks_auto_completed > 0
            ? `✅ ${result.new_commits} new commits synced · ${result.tasks_auto_completed} task(s) auto-completed!`
            : result.new_commits > 0
                ? `${result.new_commits} new commit(s) synced`
                : 'Already up to date';
        setSyncToast({ message: msg, type: result.tasks_auto_completed > 0 ? 'success' : 'info' });
        setTimeout(() => setSyncToast(null), 5000);
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen">
                <Loader className="animate-spin text-purple-600" size={48} />
            </div>
        );
    }

    const getScoreColor = (score) => {
        if (score >= 70) return 'text-green-600';
        if (score >= 40) return 'text-yellow-600';
        return 'text-red-600';
    };

    const allTasks = dashboard.projects.flatMap(project => project.tasks || []);

    return (
        <div className="p-6 space-y-6">
            {/* Sync Toast */}
            <AnimatePresence>
                {syncToast && (
                    <motion.div
                        initial={{ opacity: 0, y: -20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className={`fixed top-4 right-4 z-50 px-5 py-3 rounded-xl shadow-lg flex items-center gap-2 text-sm font-medium ${syncToast.type === 'success'
                                ? 'bg-green-600 text-white'
                                : 'bg-blue-600 text-white'
                            }`}
                    >
                        <CheckCircle2 size={16} />
                        {syncToast.message}
                    </motion.div>
                )}
            </AnimatePresence>

            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center justify-between"
            >
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 mb-2">Manager Dashboard</h1>
                    <p className="text-gray-600">Real-time project intelligence and team analytics</p>
                </div>
                <div className="flex gap-3">
                    <button onClick={() => setShowProjectModal(true)} className="btn-primary flex items-center gap-2">
                        <FolderPlus size={20} /> New Project
                    </button>
                    <button onClick={() => setShowTaskModal(true)} className="btn-primary flex items-center gap-2">
                        <ListTodo size={20} /> New Task
                    </button>
                    <button onClick={() => setShowMeetingModal(true)} className="btn-primary flex items-center gap-2">
                        <Calendar size={20} /> Schedule Meeting
                    </button>
                </div>
            </motion.div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.1 }} className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-gray-600 mb-1">Overall Health</p>
                            <p className={`text-4xl font-bold ${getScoreColor(dashboard.overall_health)}`}>
                                {dashboard.overall_health.toFixed(1)}
                            </p>
                        </div>
                        <Heart className="text-green-500" size={48} />
                    </div>
                </motion.div>

                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-gray-600 mb-1">Active Alerts</p>
                            <p className="text-4xl font-bold text-red-600">{dashboard.total_risk_alerts}</p>
                        </div>
                        <AlertTriangle className="text-red-500" size={48} />
                    </div>
                </motion.div>

                <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }} className="card">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-gray-600 mb-1">Overloaded Team</p>
                            <p className="text-4xl font-bold text-yellow-600">{dashboard.overloaded_employees.length}</p>
                        </div>
                        <Users className="text-yellow-500" size={48} />
                    </div>
                </motion.div>
            </div>

            {/* Projects */}
            <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-900">Your Projects</h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {dashboard.projects.map((project, index) => (
                        <motion.div
                            key={project.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="card hover:scale-[1.01] transition-transform"
                        >
                            {/* Project header */}
                            <div className="flex items-start justify-between mb-4">
                                <div>
                                    <h3 className="text-xl font-bold text-gray-900">{project.name}</h3>
                                    {project.github_repo_url ? (
                                        <a
                                            href={project.github_repo_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="text-xs text-purple-500 hover:text-purple-700 flex items-center gap-1 mt-0.5"
                                        >
                                            <Github size={11} />
                                            {project.github_repo_owner}/{project.github_repo_name}
                                        </a>
                                    ) : (
                                        <button
                                            onClick={() => setLinkGitHubProject(project)}
                                            className="text-xs text-gray-400 hover:text-purple-600 flex items-center gap-1 mt-0.5 transition-colors"
                                        >
                                            <Github size={11} /> Link GitHub repo
                                        </button>
                                    )}
                                </div>
                                <span className={`text-3xl font-bold ${getScoreColor(project.health_score)}`}>
                                    {project.health_score.toFixed(1)}
                                </span>
                            </div>

                            <div className="space-y-2 mb-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-gray-600">Risk Score</span>
                                    <span className="font-semibold">{project.risk_score.toFixed(1)}/100</span>
                                </div>
                            </div>

                            {project.sprints.length > 0 && (
                                <div className="border-t pt-4">
                                    <p className="text-sm font-semibold text-gray-700 mb-2">Sprints:</p>
                                    {project.sprints.map((sprint) => (
                                        <div key={sprint.sprint_number} className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-600">Sprint {sprint.sprint_number}</span>
                                            <span className="font-semibold text-purple-600">
                                                {sprint.completion_probability.toFixed(1)}% complete
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {project.tasks && project.tasks.filter(t => !t.assigned_to).length > 0 && (
                                <div className="border-t pt-4 mt-4">
                                    <p className="text-sm font-semibold text-gray-700 mb-2">Unassigned Tasks:</p>
                                    {project.tasks.filter(t => !t.assigned_to).slice(0, 3).map((task) => (
                                        <div key={task.id} className="flex justify-between items-center text-sm mb-2 p-2 bg-gray-50 rounded">
                                            <span className="text-gray-700">{task.title}</span>
                                            <button
                                                onClick={() => handleAssignTask(task)}
                                                className="text-purple-600 hover:text-purple-800 font-semibold text-xs flex items-center gap-1"
                                            >
                                                <UserPlus size={14} /> Assign
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {project.active_alerts.length > 0 && (
                                <div className="border-t pt-4 mt-4">
                                    <p className="text-sm font-semibold text-gray-700 mb-2">Active Alerts:</p>
                                    {project.active_alerts.slice(0, 2).map((alert, i) => (
                                        <div
                                            key={i}
                                            className={`text-sm p-2 rounded-lg mb-2 ${alert.severity === 'CRITICAL'
                                                ? 'bg-red-50 text-red-700'
                                                : 'bg-yellow-50 text-yellow-700'}`}
                                        >
                                            <span className="font-semibold">{alert.severity}:</span> {alert.message}
                                        </div>
                                    ))}
                                </div>
                            )}

                            {/* ─── GitHub Commits Panel ─── */}
                            <GitHubCommitsPanel
                                project={project}
                                onSyncSuccess={handleSyncSuccess}
                            />
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Meetings Section */}
            <MeetingsList userRole="PROJECT_MANAGER" onRefresh={meetingsRefresh} />

            {/* Overloaded Employees */}
            {dashboard.overloaded_employees.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card">
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Overloaded Employees</h2>
                    <div className="space-y-3">
                        {dashboard.overloaded_employees.map((emp) => (
                            <div key={emp.user_id} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                                <span className="font-semibold text-gray-900">{emp.username}</span>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-gray-600">{emp.active_tasks} tasks</span>
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${emp.overload_level === 'CRITICAL'
                                        ? 'bg-red-200 text-red-800'
                                        : 'bg-yellow-200 text-yellow-800'}`}>
                                        {emp.overload_level}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </motion.div>
            )}

            {/* Modals */}
            {selectedTask && (
                <AssignTaskModal
                    task={selectedTask}
                    isOpen={showAssignModal}
                    onClose={() => { setShowAssignModal(false); setSelectedTask(null); }}
                    onSuccess={handleAssignSuccess}
                />
            )}
            <CreateMeetingModal
                projects={dashboard.projects}
                isOpen={showMeetingModal}
                onClose={() => setShowMeetingModal(false)}
                onSuccess={handleMeetingSuccess}
            />
            <CreateProjectModal
                isOpen={showProjectModal}
                onClose={() => setShowProjectModal(false)}
                onSuccess={handleAssignSuccess}
            />
            <CreateTaskModal
                isOpen={showTaskModal}
                onClose={() => setShowTaskModal(false)}
                onSuccess={handleAssignSuccess}
            />
            {linkGitHubProject && (
                <LinkGitHubModal
                    project={linkGitHubProject}
                    isOpen={!!linkGitHubProject}
                    onClose={() => setLinkGitHubProject(null)}
                    onSuccess={() => { loadDashboard(); setLinkGitHubProject(null); }}
                />
            )}
        </div>
    );
}
