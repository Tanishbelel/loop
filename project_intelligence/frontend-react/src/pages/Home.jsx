import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Rocket, Users, Calendar, TrendingUp, Sparkles, ArrowRight } from 'lucide-react';

export default function Home() {
    const navigate = useNavigate();
    const { user } = useAuth();

    if (user) {
        navigate('/');
        return null;
    }

    const features = [
        {
            icon: <TrendingUp className="text-purple-600" size={32} />,
            title: 'Real-Time Analytics',
            description: 'Track project health, team performance, and sprint progress with AI-powered insights'
        },
        {
            icon: <Users className="text-indigo-600" size={32} />,
            title: 'Team Collaboration',
            description: 'Assign tasks, conduct scrum meetings, and manage workloads efficiently'
        },
        {
            icon: <Calendar className="text-blue-600" size={32} />,
            title: 'Sprint Management',
            description: 'Plan sprints, track completion probability, and identify risks early'
        },
        {
            icon: <Sparkles className="text-pink-600" size={32} />,
            title: 'AI-Powered Summaries',
            description: 'Get intelligent meeting summaries with action items and insights'
        }
    ];

    const demoCredentials = [
        { role: 'Project Manager', username: 'tanish', password: 'tanish123' },
        { role: 'Employee', username: 'drash', password: 'drash123' },
        { role: 'Employee', username: 'manas', password: 'manas123' },
        { role: 'Employee', username: 'sidi', password: 'sidi123' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-purple-50 via-indigo-50 to-blue-50">
            {/* Hero Section */}
            <div className="container mx-auto px-4 py-16">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-16"
                >
                    <div className="flex items-center justify-center mb-6">
                        <Rocket className="text-purple-600" size={64} />
                    </div>
                    <h1 className="text-6xl font-bold text-gray-900 mb-4">
                        Project Intelligence
                    </h1>
                    <p className="text-2xl text-gray-600 mb-8">
                        AI-Powered Project Management & Team Analytics
                    </p>
                    <button
                        onClick={() => navigate('/login')}
                        className="btn-primary text-lg px-8 py-4 inline-flex items-center gap-3"
                    >
                        Get Started
                        <ArrowRight size={24} />
                    </button>
                </motion.div>

                {/* Features Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
                    {features.map((feature, index) => (
                        <motion.div
                            key={index}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: index * 0.1 }}
                            className="card text-center"
                        >
                            <div className="flex justify-center mb-4">
                                {feature.icon}
                            </div>
                            <h3 className="text-xl font-bold text-gray-900 mb-2">
                                {feature.title}
                            </h3>
                            <p className="text-gray-600 text-sm">
                                {feature.description}
                            </p>
                        </motion.div>
                    ))}
                </div>

                {/* Demo Credentials */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.5 }}
                    className="max-w-4xl mx-auto"
                >
                    <div className="card">
                        <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
                            Demo Credentials
                        </h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {demoCredentials.map((cred, index) => (
                                <div
                                    key={index}
                                    className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 rounded-lg border-2 border-purple-200"
                                >
                                    <p className="text-sm font-semibold text-purple-900 mb-2">
                                        {cred.role}
                                    </p>
                                    <div className="space-y-1 text-sm">
                                        <p className="text-gray-700">
                                            <span className="font-semibold">Username:</span> {cred.username}
                                        </p>
                                        <p className="text-gray-700">
                                            <span className="font-semibold">Password:</span> {cred.password}
                                        </p>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="mt-6 text-center">
                            <button
                                onClick={() => navigate('/login')}
                                className="btn-primary inline-flex items-center gap-2"
                            >
                                Try Demo
                                <ArrowRight size={20} />
                            </button>
                        </div>
                    </div>
                </motion.div>

                {/* Key Features */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.6 }}
                    className="mt-16 text-center"
                >
                    <h2 className="text-3xl font-bold text-gray-900 mb-8">
                        Everything You Need for Agile Project Management
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                        <div className="text-left">
                            <h3 className="text-xl font-bold text-purple-600 mb-3">
                                For Managers
                            </h3>
                            <ul className="space-y-2 text-gray-700">
                                <li>✓ Real-time project health monitoring</li>
                                <li>✓ Task assignment with workload visibility</li>
                                <li>✓ Schedule & conduct scrum meetings</li>
                                <li>✓ AI-generated meeting summaries</li>
                                <li>✓ Risk detection & alerts</li>
                            </ul>
                        </div>
                        <div className="text-left">
                            <h3 className="text-xl font-bold text-indigo-600 mb-3">
                                For Employees
                            </h3>
                            <ul className="space-y-2 text-gray-700">
                                <li>✓ Personal performance dashboard</li>
                                <li>✓ Task management & tracking</li>
                                <li>✓ Join scrum meetings</li>
                                <li>✓ Workload status monitoring</li>
                                <li>✓ Sprint progress visibility</li>
                            </ul>
                        </div>
                        <div className="text-left">
                            <h3 className="text-xl font-bold text-blue-600 mb-3">
                                AI Features
                            </h3>
                            <ul className="space-y-2 text-gray-700">
                                <li>✓ Intelligent meeting summaries</li>
                                <li>✓ Automatic action item extraction</li>
                                <li>✓ Risk prediction & analysis</li>
                                <li>✓ Performance scoring</li>
                                <li>✓ Sprint completion probability</li>
                            </ul>
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Footer */}
            <div className="bg-white border-t border-gray-200 py-8 mt-16">
                <div className="container mx-auto px-4 text-center text-gray-600">
                    <p>© 2026 Project Intelligence. Built with React, Django & AI.</p>
                </div>
            </div>
        </div>
    );
}
