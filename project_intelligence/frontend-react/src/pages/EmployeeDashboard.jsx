import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { getEmployeeDashboard } from '../services/api';
import { TrendingUp, CheckCircle, Clock, Loader } from 'lucide-react';
import MeetingsList from '../components/MeetingsList';

export default function EmployeeDashboard() {
    const [dashboard, setDashboard] = useState(null);
    const [loading, setLoading] = useState(true);
    const [meetingsRefresh, setMeetingsRefresh] = useState(0);

    useEffect(() => {
        loadDashboard();
        const interval = setInterval(loadDashboard, 30000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboard = async () => {
        try {
            const data = await getEmployeeDashboard();
            setDashboard(data);
        } catch (error) {
            console.error('Failed to load dashboard:', error);
        } finally {
            setLoading(false);
        }
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

    const getWorkloadColor = (status) => {
        const colors = {
            NORMAL: 'bg-green-100 text-green-800',
            ELEVATED: 'bg-blue-100 text-blue-800',
            HIGH: 'bg-yellow-100 text-yellow-800',
            CRITICAL: 'bg-red-100 text-red-800',
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    const getStatusColor = (status) => {
        const colors = {
            TODO: 'bg-gray-100 text-gray-800',
            IN_PROGRESS: 'bg-blue-100 text-blue-800',
            BLOCKED: 'bg-red-100 text-red-800',
            DONE: 'bg-green-100 text-green-800',
        };
        return colors[status] || 'bg-gray-100 text-gray-800';
    };

    return (
        <div className="p-6 space-y-6">
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
            >
                <h1 className="text-3xl font-bold text-gray-900 mb-2">My Dashboard</h1>
                <p className="text-gray-600">Track your performance and manage your tasks</p>
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
                            <p className="text-sm font-semibold text-gray-600 mb-1">Performance Score</p>
                            <p className={`text-4xl font-bold ${getScoreColor(dashboard.performance_score)}`}>
                                {dashboard.performance_score.toFixed(1)}
                            </p>
                        </div>
                        <TrendingUp className="text-purple-500" size={48} />
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.2 }}
                    className="card"
                >
                    <div>
                        <p className="text-sm font-semibold text-gray-600 mb-3">Workload Status</p>
                        <span className={`px-4 py-2 rounded-full text-sm font-bold ${getWorkloadColor(dashboard.workload_status)}`}>
                            {dashboard.workload_status}
                        </span>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.3 }}
                    className="card"
                >
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Active Tasks</span>
                            <span className="font-bold text-blue-600">{dashboard.active_tasks_count}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-sm text-gray-600">Completed</span>
                            <span className="font-bold text-green-600">{dashboard.completed_tasks_count}</span>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Task Breakdown */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="card"
            >
                <h2 className="text-xl font-bold text-gray-900 mb-4">Task Breakdown</h2>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <p className="text-2xl font-bold text-gray-700">{dashboard.task_breakdown.TODO}</p>
                        <p className="text-sm text-gray-600">To Do</p>
                    </div>
                    <div className="text-center p-4 bg-blue-50 rounded-lg">
                        <p className="text-2xl font-bold text-blue-700">{dashboard.task_breakdown.IN_PROGRESS}</p>
                        <p className="text-sm text-blue-600">In Progress</p>
                    </div>
                    <div className="text-center p-4 bg-red-50 rounded-lg">
                        <p className="text-2xl font-bold text-red-700">{dashboard.task_breakdown.BLOCKED}</p>
                        <p className="text-sm text-red-600">Blocked</p>
                    </div>
                    <div className="text-center p-4 bg-green-50 rounded-lg">
                        <p className="text-2xl font-bold text-green-700">{dashboard.task_breakdown.DONE}</p>
                        <p className="text-sm text-green-600">Done</p>
                    </div>
                </div>
            </motion.div>

            {/* Meetings Section */}
            <MeetingsList userRole="EMPLOYEE" onRefresh={meetingsRefresh} />

            {/* Assigned Tasks */}
            <div className="space-y-4">
                <h2 className="text-2xl font-bold text-gray-900">My Tasks</h2>
                <div className="grid grid-cols-1 gap-4">
                    {dashboard.assigned_tasks.map((task, index) => (
                        <motion.div
                            key={task.id}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: index * 0.05 }}
                            className="card hover:scale-102 transition-transform cursor-pointer"
                        >
                            <div className="flex items-start justify-between mb-3">
                                <h3 className="text-lg font-bold text-gray-900">{task.title}</h3>
                                <span className={`px-3 py-1 rounded-full text-xs font-bold ${getStatusColor(task.status)}`}>
                                    {task.status.replace('_', ' ')}
                                </span>
                            </div>

                            <p className="text-sm text-gray-600 mb-3">{task.description}</p>

                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-gray-600">Priority:</span>
                                    <span className="ml-2 font-semibold text-purple-600">{task.priority}</span>
                                </div>
                                <div>
                                    <span className="text-gray-600">Estimated:</span>
                                    <span className="ml-2 font-semibold">{task.estimated_hours}h</span>
                                </div>
                                <div>
                                    <span className="text-gray-600">Actual:</span>
                                    <span className="ml-2 font-semibold">{task.actual_hours}h</span>
                                </div>
                                <div>
                                    <span className="text-gray-600">Project:</span>
                                    <span className="ml-2 font-semibold">{task.project_name}</span>
                                </div>
                            </div>
                        </motion.div>
                    ))}
                </div>
            </div>
        </div>
    );
}

