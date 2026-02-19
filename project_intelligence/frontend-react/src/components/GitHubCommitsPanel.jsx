import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { syncCommits } from '../services/api';
import {
    GitCommitHorizontal, RefreshCw, ChevronDown, ChevronUp,
    ExternalLink, CheckCircle2, AlertCircle, GitBranch, Plus, Minus, FileCode
} from 'lucide-react';

function timeAgo(isoString) {
    if (!isoString) return '';
    const diff = Math.floor((Date.now() - new Date(isoString).getTime()) / 1000);
    if (diff < 60) return `${diff}s ago`;
    if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
    if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
    return `${Math.floor(diff / 86400)}d ago`;
}

function fullTimestamp(isoString) {
    if (!isoString) return '';
    return new Date(isoString).toLocaleString();
}

export default function GitHubCommitsPanel({ project, onSyncSuccess }) {
    const [expanded, setExpanded] = useState(false);
    const [syncing, setSyncing] = useState(false);
    const [syncResult, setSyncResult] = useState(null);
    const [error, setError] = useState('');
    const [commits, setCommits] = useState(project.recent_commits || []);

    const hasGitHub = !!(project.github_repo_url);

    const handleSync = async (e) => {
        e.stopPropagation();
        setSyncing(true);
        setError('');
        setSyncResult(null);
        try {
            const result = await syncCommits(project.id);
            setCommits(result.commits || []);
            setSyncResult({
                new: result.new_commits,
                completed: result.tasks_auto_completed,
            });
            if (onSyncSuccess) onSyncSuccess(result);
        } catch (err) {
            setError(err.response?.data?.error || 'Sync failed');
        } finally {
            setSyncing(false);
        }
    };

    if (!hasGitHub) {
        return (
            <div className="mt-3 p-3 bg-gray-50 rounded-xl border border-dashed border-gray-300 flex items-center gap-2 text-xs text-gray-400">
                <GitCommitHorizontal size={14} />
                No GitHub repository linked
            </div>
        );
    }

    return (
        <div className="mt-3 rounded-xl border border-gray-200 overflow-hidden">
            {/* Header */}
            <button
                onClick={() => setExpanded(v => !v)}
                className="w-full flex items-center justify-between px-4 py-2.5 bg-gray-50 hover:bg-gray-100 transition-colors"
            >
                <div className="flex items-center gap-2">
                    <GitCommitHorizontal size={15} className="text-purple-600" />
                    <span className="text-sm font-semibold text-gray-700">
                        GitHub Commits
                    </span>
                    <a
                        href={project.github_repo_url}
                        target="_blank"
                        rel="noreferrer"
                        onClick={e => e.stopPropagation()}
                        className="text-xs text-purple-500 hover:text-purple-700 flex items-center gap-0.5"
                    >
                        {project.github_repo_owner}/{project.github_repo_name}
                        <ExternalLink size={10} />
                    </a>
                    {commits.length > 0 && (
                        <span className="bg-purple-100 text-purple-700 text-xs font-bold px-1.5 py-0.5 rounded-full">
                            {commits.length}
                        </span>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleSync}
                        disabled={syncing}
                        className="flex items-center gap-1 text-xs bg-purple-600 text-white px-2.5 py-1 rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
                    >
                        <RefreshCw size={12} className={syncing ? 'animate-spin' : ''} />
                        {syncing ? 'Syncing…' : 'Sync'}
                    </button>
                    {expanded ? <ChevronUp size={14} className="text-gray-400" /> : <ChevronDown size={14} className="text-gray-400" />}
                </div>
            </button>

            {/* Sync result banner */}
            <AnimatePresence>
                {syncResult && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className={`px-4 py-2 text-xs flex items-center gap-2 ${syncResult.completed > 0
                                ? 'bg-green-50 text-green-700'
                                : 'bg-blue-50 text-blue-700'
                            }`}
                    >
                        <CheckCircle2 size={12} />
                        <span>
                            {syncResult.new === 0
                                ? 'Already up to date'
                                : `${syncResult.new} new commit${syncResult.new !== 1 ? 's' : ''} synced`}
                            {syncResult.completed > 0 && (
                                <strong className="ml-1">
                                    · {syncResult.completed} task{syncResult.completed !== 1 ? 's' : ''} auto-completed ✅
                                </strong>
                            )}
                        </span>
                    </motion.div>
                )}
                {error && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="px-4 py-2 text-xs flex items-center gap-2 bg-red-50 text-red-700"
                    >
                        <AlertCircle size={12} />
                        {error}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Commits list */}
            <AnimatePresence>
                {expanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="divide-y divide-gray-100 max-h-72 overflow-y-auto"
                    >
                        {commits.length === 0 ? (
                            <div className="px-4 py-6 text-center text-sm text-gray-400">
                                No commits yet. Click Sync to fetch from GitHub.
                            </div>
                        ) : (
                            commits.map((commit) => (
                                <div
                                    key={commit.id || commit.sha}
                                    className={`px-4 py-3 ${commit.is_meaningful ? '' : 'opacity-60'}`}
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        {/* Left: SHA + badge */}
                                        <div className="flex items-center gap-2 min-w-0">
                                            <span
                                                className={`shrink-0 text-xs font-mono font-bold px-1.5 py-0.5 rounded ${commit.is_meaningful
                                                        ? 'bg-green-100 text-green-700'
                                                        : 'bg-gray-100 text-gray-500'
                                                    }`}
                                            >
                                                {commit.short_sha || (commit.sha || '').slice(0, 7)}
                                            </span>
                                            {commit.is_meaningful ? (
                                                <span className="shrink-0 text-xs text-green-600 font-semibold flex items-center gap-0.5">
                                                    <CheckCircle2 size={10} /> Meaningful
                                                </span>
                                            ) : (
                                                <span className="shrink-0 text-xs text-gray-400 font-medium flex items-center gap-0.5">
                                                    <AlertCircle size={10} /> Trivial
                                                    {commit.trivial_reason && (
                                                        <span className="ml-1 text-gray-300">({commit.trivial_reason})</span>
                                                    )}
                                                </span>
                                            )}
                                        </div>

                                        {/* Right: timestamp */}
                                        <span
                                            className="shrink-0 text-xs text-gray-400"
                                            title={fullTimestamp(commit.commit_time)}
                                        >
                                            {timeAgo(commit.commit_time)}
                                        </span>
                                    </div>

                                    {/* Commit message (first line) */}
                                    <p className="mt-1 text-sm text-gray-800 font-medium truncate">
                                        {commit.message?.split('\n')[0] || '(no message)'}
                                    </p>

                                    {/* Meta row */}
                                    <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-gray-500">
                                        <span className="flex items-center gap-0.5">
                                            <GitBranch size={10} /> {commit.branch || 'main'}
                                        </span>
                                        <span className="font-medium">{commit.author}</span>
                                        <span className="flex items-center gap-1">
                                            <FileCode size={10} /> {commit.files_changed} file{commit.files_changed !== 1 ? 's' : ''}
                                        </span>
                                        <span className="flex items-center gap-0.5 text-green-600 font-medium">
                                            <Plus size={10} />{commit.lines_added}
                                        </span>
                                        <span className="flex items-center gap-0.5 text-red-500 font-medium">
                                            <Minus size={10} />{commit.lines_deleted}
                                        </span>
                                        {commit.task_title && (
                                            <span className="bg-purple-100 text-purple-700 px-1.5 py-0.5 rounded-full font-semibold">
                                                ✅ Closed: {commit.task_title}
                                            </span>
                                        )}
                                        {commit.github_url && (
                                            <a
                                                href={commit.github_url}
                                                target="_blank"
                                                rel="noreferrer"
                                                className="flex items-center gap-0.5 text-purple-500 hover:text-purple-700"
                                            >
                                                View <ExternalLink size={10} />
                                            </a>
                                        )}
                                    </div>
                                </div>
                            ))
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Last sync info */}
            {project.last_commit_sync && (
                <div className="px-4 py-1.5 bg-gray-50 border-t border-gray-100 text-xs text-gray-400">
                    Last synced: {fullTimestamp(project.last_commit_sync)}
                </div>
            )}
        </div>
    );
}
