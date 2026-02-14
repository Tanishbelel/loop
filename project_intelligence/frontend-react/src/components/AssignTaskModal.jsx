import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getEmployees, assignTask } from '../services/api';
import { Users, Loader, X, AlertCircle } from 'lucide-react';

export default function AssignTaskModal({ task, isOpen, onClose, onSuccess }) {
    const [employees, setEmployees] = useState([]);
    const [selectedEmployee, setSelectedEmployee] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen) {
            loadEmployees();
        }
    }, [isOpen]);

    const loadEmployees = async () => {
        try {
            const data = await getEmployees();
            setEmployees(data);
        } catch (err) {
            setError('Failed to load employees');
        }
    };

    const handleAssign = async () => {
        if (!selectedEmployee) return;

        setLoading(true);
        setError('');
        try {
            await assignTask(task.id, selectedEmployee);
            onSuccess();
            onClose();
        } catch (err) {
            setError('Failed to assign task');
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
                    className="bg-white rounded-2xl p-6 max-w-md w-full"
                    onClick={(e) => e.stopPropagation()}
                >
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-2xl font-bold text-gray-900">Assign Task</h2>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                            <X size={24} />
                        </button>
                    </div>

                    <div className="mb-4 p-4 bg-purple-50 rounded-lg">
                        <h3 className="font-semibold text-gray-900">{task.title}</h3>
                        <p className="text-sm text-gray-600 mt-1">{task.description}</p>
                        <div className="flex gap-3 mt-2 text-xs">
                            <span className="text-gray-600">Priority: <strong>{task.priority}</strong></span>
                            <span className="text-gray-600">Est: <strong>{task.estimated_hours}h</strong></span>
                        </div>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center gap-2 text-red-700">
                            <AlertCircle size={16} />
                            <span className="text-sm">{error}</span>
                        </div>
                    )}

                    <div className="mb-6">
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                            Select Employee
                        </label>
                        <select
                            value={selectedEmployee}
                            onChange={(e) => setSelectedEmployee(e.target.value)}
                            className="input-field"
                        >
                            <option value="">Choose an employee...</option>
                            {employees.map(emp => (
                                <option key={emp.id} value={emp.id}>
                                    {emp.username} - {emp.first_name} {emp.last_name}
                                    {emp.active_tasks !== undefined && ` (${emp.active_tasks} active tasks)`}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={handleAssign}
                            disabled={!selectedEmployee || loading}
                            className="btn-primary flex-1 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <>
                                    <Loader className="animate-spin" size={20} />
                                    Assigning...
                                </>
                            ) : (
                                <>
                                    <Users size={20} />
                                    Assign Task
                                </>
                            )}
                        </button>
                        <button onClick={onClose} className="btn-secondary flex-1">
                            Cancel
                        </button>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    );
}
