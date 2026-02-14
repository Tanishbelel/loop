import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getManagerDashboard } from '../services/api';
import { Heart, AlertTriangle, Users, TrendingUp, Loader, Calendar, UserPlus, FolderPlus, ListTodo } from 'lucide-react';
import AssignTaskModal from '../components/AssignTaskModal';
import CreateMeetingModal from '../components/CreateMeetingModal';
import CreateProjectModal from '../components/CreateProjectModal';
import CreateTaskModal from '../components/CreateTaskModal';
import MeetingsList from '../components/MeetingsList';

export default function ManagerDashboard() {
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedTask, setSelectedTask] = useState(null);
    const [showAssignModal, setShowAssignModal] = useState(false);
    const [showMeetingModal, setShowMeetingModal] = useState(false);
    const [showProjectModal, setShowProjectModal] = useState(false);
    const [showTaskModal, setShowTaskModal] = useState(false);
    const [meetingsRefresh, setMeetingsRefresh] = useState(0);

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

    const handleAssignTask = (task) => {
        setSelectedTask(task);
        setShowAssignModal(true);
    };

    const handleAssignSuccess = () => {
        loadDashboard();
        setMeetingsRefresh(prev => prev + 1);
    };

    const handleMeetingSuccess = () => {
        setMeetingsRefresh(prev => prev + 1);
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

    // Get all tasks from all projects
    const allTasks = dashboard.projects.flatMap(project =>
        project.tasks || []
    );

    return (
        <div className="p-6 space-y-6">
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
                    <button
                        onClick={() => setShowProjectModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <FolderPlus size={20} />
                        New Project
                    </button>
                    <button
                        onClick={() => setShowTaskModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <ListTodo size={20} />
                        New Task
                    </button>
                    <button
                        onClick={() => setShowMeetingModal(true)}
                        className="btn-primary flex items-center gap-2"
                    >
                        <Calendar size={20} />
                        Schedule Meeting
                    </button>
                </div>
            </motion.div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.1 }}
                    className="card"
                >
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

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="card"
                >
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-gray-600 mb-1">Active Alerts</p>
                            <p className="text-4xl font-bold text-red-600">
                                {dashboard.total_risk_alerts}
                            </p>
                        </div>
                        <AlertTriangle className="text-red-500" size={48} />
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="card"
                >
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-semibold text-gray-600 mb-1">Overloaded Team</p>
                            <p className="text-4xl font-bold text-yellow-600">
                                {dashboard.overloaded_employees.length}
                            </p>
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
                            className="card hover:scale-105 transition-transform"
                        >
                            <div className="flex items-start justify-between mb-4">
                                <h3 className="text-xl font-bold text-gray-900">{project.name}</h3>
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
                                        <div key={sprint.id} className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-600">Sprint {sprint.sprint_number}</span>
                                            <span className="font-semibold text-purple-600">
                                                {sprint.completion_probability.toFixed(1)}% complete
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}

                            {project.tasks && project.tasks.length > 0 && (
                                <div className="border-t pt-4 mt-4">
                                    <p className="text-sm font-semibold text-gray-700 mb-2">Unassigned Tasks:</p>
                                    {project.tasks.filter(t => !t.assigned_to).slice(0, 3).map((task) => (
                                        <div key={task.id} className="flex justify-between items-center text-sm mb-2 p-2 bg-gray-50 rounded">
                                            <span className="text-gray-700">{task.title}</span>
                                            <button
                                                onClick={() => handleAssignTask(task)}
                                                className="text-purple-600 hover:text-purple-800 font-semibold text-xs flex items-center gap-1"
                                            >
                                                <UserPlus size={14} />
                                                Assign
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
                                                : 'bg-yellow-50 text-yellow-700'
                                                }`}
                                        >
                                            <span className="font-semibold">{alert.severity}:</span> {alert.message}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </motion.div>
                    ))}
                </div>
            </div>

            {/* Meetings Section */}
            <MeetingsList userRole="PROJECT_MANAGER" onRefresh={meetingsRefresh} />

            {/* Overloaded Employees */}
            {dashboard.overloaded_employees.length > 0 && (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card"
                >
                    <h2 className="text-2xl font-bold text-gray-900 mb-4">Overloaded Employees</h2>
                    <div className="space-y-3">
                        {dashboard.overloaded_employees.map((emp) => (
                            <div key={emp.user_id} className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg">
                                <span className="font-semibold text-gray-900">{emp.username}</span>
                                <div className="flex items-center gap-3">
                                    <span className="text-sm text-gray-600">{emp.active_tasks} tasks</span>
                                    <span className={`px-3 py-1 rounded-full text-xs font-bold ${emp.overload_level === 'CRITICAL'
                                        ? 'bg-red-200 text-red-800'
                                        : 'bg-yellow-200 text-yellow-800'
                                        }`}>
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
                    onClose={() => {
                        setShowAssignModal(false);
                        setSelectedTask(null);
                    }}
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
        </div>
    );
}

