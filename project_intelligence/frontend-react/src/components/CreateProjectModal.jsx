import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { createProject, linkGitHubRepo } from '../services/api';
import { FolderPlus, X, Loader, AlertCircle, Github, Link, Plus, Eye, EyeOff } from 'lucide-react';

export default function CreateProjectModal({ isOpen, onClose, onSuccess }) {
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        start_date: '',
        end_date: ''
    });
    const [githubMode, setGithubMode] = useState('skip'); // 'skip' | 'link' | 'create'
    const [githubToken, setGithubToken] = useState('');
    const [repoUrl, setRepoUrl] = useState('');
    const [newRepoName, setNewRepoName] = useState('');
    const [privateRepo, setPrivateRepo] = useState(false);
    const [showToken, setShowToken] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const reset = () => {
        setFormData({ name: '', description: '', start_date: '', end_date: '' });
        setGithubMode('skip');
        setGithubToken('');
        setRepoUrl('');
        setNewRepoName('');
        setPrivateRepo(false);
        setShowToken(false);
        setError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // 1. Create the project
            const project = await createProject(formData);

            // 2. Optionally link/create GitHub repo
            if (githubMode !== 'skip' && githubToken) {
                await linkGitHubRepo(project.id, {
                    action: githubMode,
                    token: githubToken,
                    repo_url: repoUrl,
                    new_repo_name: newRepoName || formData.name.toLowerCase().replace(/\s+/g, '-'),
                    private: privateRepo,
                });
            }

            onSuccess();
            onClose();
            reset();
        } catch (err) {
            const msg =
                err.response?.data?.error ||
                err.response?.data?.name?.[0] ||
                JSON.stringify(err.response?.data || 'Failed to create project');
            setError(msg);
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
                        <h2 className="text-2xl font-bold text-gray-900">Create New Project</h2>
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
                        {/* Project Name */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Project Name *
                            </label>
                            <input
                                type="text"
                                value={formData.name}
                                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                className="input-field"
                                placeholder="e.g., E-Commerce Platform"
                                required
                            />
                        </div>

                        {/* Description */}
                        <div>
                            <label className="block text-sm font-semibold text-gray-700 mb-2">
                                Description
                            </label>
                            <textarea
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                className="input-field"
                                rows="3"
                                placeholder="Brief description of the project..."
                            />
                        </div>

                        {/* Dates */}
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    Start Date *
                                </label>
                                <input
                                    type="date"
                                    value={formData.start_date}
                                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                                    className="input-field"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold text-gray-700 mb-2">
                                    End Date *
                                </label>
                                <input
                                    type="date"
                                    value={formData.end_date}
                                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                                    className="input-field"
                                    required
                                />
                            </div>
                        </div>

                        {/* ─── GitHub Section ─────────────────────────────── */}
                        <div className="border border-gray-200 rounded-xl p-4 space-y-3">
                            <div className="flex items-center gap-2 mb-1">
                                <Github size={18} className="text-gray-700" />
                                <span className="font-semibold text-gray-800">GitHub Repository</span>
                                <span className="text-xs text-gray-400">(optional)</span>
                            </div>

                            {/* Mode selector */}
                            <div className="flex gap-2">
                                {[
                                    { value: 'skip', label: 'Skip' },
                                    { value: 'link', label: 'Link Existing', icon: <Link size={12} /> },
                                    { value: 'create', label: 'Create New', icon: <Plus size={12} /> },
                                ].map(opt => (
                                    <button
                                        key={opt.value}
                                        type="button"
                                        onClick={() => setGithubMode(opt.value)}
                                        className={`flex items-center gap-1 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${githubMode === opt.value
                                                ? 'bg-purple-600 text-white'
                                                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                                            }`}
                                    >
                                        {opt.icon}
                                        {opt.label}
                                    </button>
                                ))}
                            </div>

                            <AnimatePresence>
                                {githubMode !== 'skip' && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: 'auto', opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="space-y-3 overflow-hidden"
                                    >
                                        {/* PAT input */}
                                        <div>
                                            <label className="block text-xs font-semibold text-gray-600 mb-1">
                                                GitHub Personal Access Token *
                                            </label>
                                            <div className="relative">
                                                <input
                                                    type={showToken ? 'text' : 'password'}
                                                    value={githubToken}
                                                    onChange={(e) => setGithubToken(e.target.value)}
                                                    className="input-field pr-10 text-sm"
                                                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() => setShowToken(v => !v)}
                                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                                >
                                                    {showToken ? <EyeOff size={14} /> : <Eye size={14} />}
                                                </button>
                                            </div>
                                            <p className="text-xs text-gray-400 mt-1">
                                                Needs <code>repo</code> scope.{' '}
                                                <a
                                                    href="https://github.com/settings/tokens/new"
                                                    target="_blank"
                                                    rel="noreferrer"
                                                    className="text-purple-500 hover:underline"
                                                >
                                                    Generate one here
                                                </a>
                                            </p>
                                        </div>

                                        {githubMode === 'link' && (
                                            <div>
                                                <label className="block text-xs font-semibold text-gray-600 mb-1">
                                                    Repository URL or owner/repo *
                                                </label>
                                                <input
                                                    type="text"
                                                    value={repoUrl}
                                                    onChange={(e) => setRepoUrl(e.target.value)}
                                                    className="input-field text-sm"
                                                    placeholder="e.g., Tanishbelel/loop  or  https://github.com/owner/repo"
                                                />
                                            </div>
                                        )}

                                        {githubMode === 'create' && (
                                            <>
                                                <div>
                                                    <label className="block text-xs font-semibold text-gray-600 mb-1">
                                                        New Repository Name *
                                                    </label>
                                                    <input
                                                        type="text"
                                                        value={newRepoName}
                                                        onChange={(e) => setNewRepoName(e.target.value)}
                                                        className="input-field text-sm"
                                                        placeholder="my-awesome-project"
                                                    />
                                                </div>
                                                <label className="flex items-center gap-2 cursor-pointer text-sm text-gray-700">
                                                    <input
                                                        type="checkbox"
                                                        checked={privateRepo}
                                                        onChange={(e) => setPrivateRepo(e.target.checked)}
                                                        className="w-4 h-4 accent-purple-600"
                                                    />
                                                    Private repository
                                                </label>
                                            </>
                                        )}
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                        {/* ─────────────────────────────────────────────────── */}

                        <div className="flex gap-3 pt-2">
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
                                        <FolderPlus size={20} />
                                        Create Project
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
