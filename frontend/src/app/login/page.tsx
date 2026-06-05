'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Shield, Eye, EyeOff, CalendarDays } from 'lucide-react';
import API_URL from '@/lib/api';

export default function LoginPage() {
    const router = useRouter();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`${API_URL}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ username, password }),
            });
            const data = await res.json();
            if (!res.ok) {
                setError(data.detail || 'เข้าสู่ระบบไม่สำเร็จ');
            } else {
                localStorage.setItem('user', JSON.stringify(data.user)); // Keep user info, NO token
                router.push('/');
            }
        } catch {
            setError('ไม่สามารถเชื่อมต่อกับ Server ได้');
        }
        setLoading(false);
    };

    return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4 relative overflow-hidden">
            {/* Background glow */}
            <div className="absolute inset-0 pointer-events-none">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-3xl" />
                <div className="absolute bottom-0 right-0 w-[400px] h-[400px] bg-purple-600/10 rounded-full blur-3xl" />
            </div>

            <motion.div
                initial={{ opacity: 0, y: 30 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="relative w-full max-w-md"
            >
                {/* Logo */}
                <div className="text-center mb-8">
                    <div className="inline-flex w-20 h-20 rounded-3xl bg-gradient-to-tr from-blue-600 to-purple-600 items-center justify-center mb-4 shadow-2xl shadow-blue-500/30">
                        <CalendarDays className="h-10 w-10 text-white" />
                    </div>
                    <h1 className="text-3xl font-bold text-white">JadVen.ai</h1>
                    <p className="text-slate-400 mt-1">ระบบจัดตารางเวรพยาบาลอัจฉริยะ</p>
                </div>

                {/* Card */}
                <div className="bg-slate-800/80 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-8 shadow-2xl">
                    <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Shield className="h-5 w-5 text-blue-400" />
                        เข้าสู่ระบบ
                    </h2>

                    <form onSubmit={handleLogin} className="space-y-5">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">ชื่อผู้ใช้</label>
                            <input
                                type="text"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                required
                                autoFocus
                                placeholder="เช่น admin, headnurse"
                                className="w-full bg-slate-900/70 border border-slate-600 rounded-xl px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">รหัสผ่าน</label>
                            <div className="relative">
                                <input
                                    type={showPassword ? 'text' : 'password'}
                                    value={password}
                                    onChange={e => setPassword(e.target.value)}
                                    required
                                    placeholder="••••••••"
                                    className="w-full bg-slate-900/70 border border-slate-600 rounded-xl px-4 py-3 pr-12 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                                />
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white transition-colors"
                                >
                                    {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <motion.div initial={{ opacity: 0, y: -5 }} animate={{ opacity: 1, y: 0 }} className="bg-red-500/10 border border-red-500/30 text-red-400 text-sm px-4 py-3 rounded-xl">
                                ❌ {error}
                            </motion.div>
                        )}

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white font-bold rounded-xl transition-all shadow-lg shadow-blue-500/20 hover:shadow-blue-500/40 disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {loading ? (
                                <><div className="h-5 w-5 rounded-full border-2 border-white/30 border-t-white animate-spin" /> กำลังเข้าสู่ระบบ...</>
                            ) : (
                                'เข้าสู่ระบบ →'
                            )}
                        </button>
                    </form>

                    {/* Default accounts hint */}
                    <div className="mt-6 p-4 bg-slate-900/50 rounded-xl border border-slate-700/50">
                        <p className="text-xs text-slate-500 font-medium mb-2">🔑 บัญชีทดสอบ</p>
                        <div className="space-y-1 text-xs text-slate-400">
                            <p><span className="text-slate-300 font-mono">admin</span> / <span className="font-mono">admin1234</span> <span className="text-blue-400">(Admin)</span></p>
                            <p><span className="text-slate-300 font-mono">headnurse</span> / <span className="font-mono">nurse1234</span> <span className="text-emerald-400">(Head Nurse)</span></p>
                            <p><span className="text-slate-300 font-mono">nurse01</span> / <span className="font-mono">nurse1234</span> <span className="text-slate-400">(Nurse)</span></p>
                        </div>
                    </div>
                </div>
            </motion.div>
        </div>
    );
}
