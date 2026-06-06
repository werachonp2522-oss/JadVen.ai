'use client';

import { useState, useEffect, useCallback } from 'react';
import {
  CalendarDays,
  Users,
  Settings,
  Menu,
  Activity,
  MessageSquare,
  AlertTriangle,
  Plus,
  Search,
  Shield,
  Clock,
  UserPlus,
  Trash2,
  Edit,
  Building2,
  Download,
  BarChart3,
  Calendar,
  X,
  Send,
  CheckCircle,
  XCircle,
  LogOut,
  UserCog,
  FileText,
  Bell,
  User,
  Key,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useRouter } from 'next/navigation';
import API_URL from '@/lib/api';

export default function Home() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('schedule');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [pendingLeaves, setPendingLeaves] = useState(0);
  // Toast
  const [toasts, setToasts] = useState<{ id: number, msg: string, type: 'success' | 'error' | 'info' }[]>([]);
  const showToast = useCallback((msg: string, type: 'success' | 'error' | 'info' = 'success') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, msg, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3500);
  }, []);
  // Profile modal
  const [profileOpen, setProfileOpen] = useState(false);
  const [profileName, setProfileName] = useState('');
  const [pwForm, setPwForm] = useState({ current: '', newPw: '', confirm: '' });
  const [profileSaving, setProfileSaving] = useState(false);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [aiInput, setAiInput] = useState('');
  const [aiMessages, setAiMessages] = useState<{ role: string, text: string }[]>([]);
  const [aiLoading, setAiLoading] = useState(false);

  // Auth check on load
  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (!userStr) {
      router.push('/login');
      return;
    }
    try { setCurrentUser(JSON.parse(userStr)); setProfileName(JSON.parse(userStr)?.full_name || ''); } catch { router.push('/login'); }
    // Fetch pending leave count for badge
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/leave/')
      .then(r => r.json())
      .then(d => setPendingLeaves(d.filter((l: any) => l.status === 'pending').length))
      .catch(() => { });
  }, [router]);

  const handleLogout = async () => {
    try {
      await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/auth/logout', { method: 'POST', credentials: 'include' });
    } catch { }
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    router.push('/login');
  };

  const getAuthHeaders = () => ({
    'Content-Type': 'application/json'
  }); // Credentials managed by cookies

  const handleSaveProfile = async () => {
    setProfileSaving(true);
    try {
      const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/auth/profile', { method: 'PUT', headers: getAuthHeaders(), credentials: 'include', body: JSON.stringify({ full_name: profileName }) });
      const data = await res.json();
      if (res.ok) {
        const updated = { ...currentUser, full_name: profileName };
        setCurrentUser(updated); localStorage.setItem('user', JSON.stringify(updated));
        showToast('อัปเดตโปรไฟล์สำเร็จ ✅', 'success');
      } else { showToast(data.detail || 'เกิดข้อผิดพลาด', 'error'); }
    } catch { showToast('ไม่สามารถเชื่อมต่อ Server', 'error'); }
    setProfileSaving(false);
  };

  const handleChangePassword = async () => {
    if (pwForm.newPw !== pwForm.confirm) { showToast('รหัสผ่านใหม่ไม่ตรงกัน', 'error'); return; }
    setProfileSaving(true);
    try {
      const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/auth/change-password', { method: 'PUT', headers: getAuthHeaders(), credentials: 'include', body: JSON.stringify({ current_password: pwForm.current, new_password: pwForm.newPw }) });
      const data = await res.json();
      if (res.ok) { showToast('เปลี่ยนรหัสผ่านสำเร็จ ✅', 'success'); setPwForm({ current: '', newPw: '', confirm: '' }); }
      else { showToast(data.detail || 'เกิดข้อผิดพลาด', 'error'); }
    } catch { showToast('ไม่สามารถเชื่อมต่อ Server', 'error'); }
    setProfileSaving(false);
  };

  const sendAiMessage = async () => {
    if (!aiInput.trim()) return;
    const userMsg = aiInput;
    setAiMessages(prev => [...prev, { role: 'user', text: userMsg }]);
    setAiInput('');
    setAiLoading(true);
    try {
      const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/prompt/analyze', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: userMsg })
      });
      const data = await res.json();
      setAiMessages(prev => [...prev, { role: 'ai', text: data.status === 'success' ? data.extracted_data : data.message }]);
    } catch { setAiMessages(prev => [...prev, { role: 'ai', text: 'ไม่สามารถเชื่อมต่อ AI ได้' }]); }
    setAiLoading(false);
  };

  return (
    <div className="flex h-screen bg-slate-900 overflow-hidden text-slate-100">

      {/* Sidebar Overlay (Mobile) */}
      <AnimatePresence>
        {!sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-20 md:hidden"
            onClick={() => setSidebarOpen(true)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          width: sidebarOpen ? 256 : 80,
          transition: { duration: 0.3, ease: 'easeInOut' }
        }}
        className="relative z-30 flex flex-col bg-slate-800/80 backdrop-blur-xl border-r border-slate-700/50"
      >
        <div className="flex items-center justify-between p-4 h-16 border-b border-slate-700/50">
          <AnimatePresence mode="wait">
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="flex items-center gap-2 font-bold text-xl text-brand-500"
              >
                <Activity className="h-6 w-6" />
                <span>JadVen.ai</span>
              </motion.div>
            )}
          </AnimatePresence>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <Menu className="h-5 w-5 text-slate-400" />
          </button>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <NavItem
            icon={<CalendarDays />}
            label="ตารางเวร (Schedule)"
            isActive={activeTab === 'schedule'}
            onClick={() => setActiveTab('schedule')}
            isOpen={sidebarOpen}
          />
          <NavItem
            icon={<AlertTriangle />}
            label="แก้ปัญหากะทันหัน"
            isActive={activeTab === 'conflict'}
            onClick={() => setActiveTab('conflict')}
            isOpen={sidebarOpen}
          />
          <NavItem
            icon={<Users />}
            label="บุคลากร (Staff)"
            isActive={activeTab === 'staff'}
            onClick={() => setActiveTab('staff')}
            isOpen={sidebarOpen}
          />
          <NavItem
            icon={<Settings />}
            label="ตั้งค่ากฎ (Rule Builder)"
            isActive={activeTab === 'rules'}
            onClick={() => setActiveTab('rules')}
            isOpen={sidebarOpen}
          />
          <NavItem
            icon={<Building2 />}
            label="ตั้งค่าวอร์ด (Ward Config)"
            isActive={activeTab === 'wardconfig'}
            onClick={() => setActiveTab('wardconfig')}
            isOpen={sidebarOpen}
          />
          <NavItem
            icon={<Calendar />}
            label="วันลา (Leave)"
            isActive={activeTab === 'leave'}
            onClick={() => setActiveTab('leave')}
            isOpen={sidebarOpen}
            badge={pendingLeaves > 0 ? pendingLeaves : undefined}
          />
          <NavItem
            icon={<Activity />}
            label="แลกเวร (Shift Swap)"
            isActive={activeTab === 'swap'}
            onClick={() => setActiveTab('swap')}
            isOpen={sidebarOpen}
          />
          <NavItem
            icon={<BarChart3 />}
            label="แดชบอร์ด (Dashboard)"
            isActive={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
            isOpen={sidebarOpen}
          />
          {currentUser?.role === 'admin' && (
            <NavItem
              icon={<UserCog />}
              label="จัดการผู้ใช้ (Admin)"
              isActive={activeTab === 'users'}
              onClick={() => setActiveTab('users')}
              isOpen={sidebarOpen}
            />
          )}
          <NavItem
            icon={<CalendarDays />}
            label="ปฏิทินเวร (Calendar)"
            isActive={activeTab === 'calendar'}
            onClick={() => setActiveTab('calendar')}
            isOpen={sidebarOpen}
          />
        </nav>

        {/* User Profile */}
        <div className="p-4 border-t border-slate-700/50">
          <div className={`flex items-center gap-3 ${sidebarOpen ? '' : 'justify-center'}`}>
            <div onClick={() => setProfileOpen(true)} className="h-10 w-10 rounded-full bg-gradient-to-tr from-brand-600 to-purple-600 flex items-center justify-center font-bold text-white shadow-lg flex-shrink-0 cursor-pointer hover:ring-2 hover:ring-brand-400 transition-all">
              {currentUser?.full_name?.charAt(0) || currentUser?.username?.charAt(0)?.toUpperCase() || '?'}
            </div>
            {sidebarOpen && (
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white truncate">{currentUser?.full_name || currentUser?.username}</p>
                <p className="text-xs text-slate-400 truncate">
                  {currentUser?.role === 'admin' ? '🔴 Admin' : currentUser?.role === 'head_nurse' ? '🟢 Head Nurse' : '🔵 Nurse'}
                  {' · '}{currentUser?.ward?.replace('แผนก ', '') || 'ER'}
                </p>
              </div>
            )}
            {sidebarOpen && (
              <button onClick={handleLogout} title="ออกจากระบบ" className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-500/10 transition-colors flex-shrink-0">
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-800 via-slate-900 to-slate-900">

        {/* Top Header */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-white/5 glass z-10">
          <h1 className="text-xl font-semibold text-white/90">
            {activeTab === 'schedule' && "จัดการตารางเวรอัจฉริยะ (Smart Roster)"}
            {activeTab === 'conflict' && "ระบบจัดการความขัดแย้ง (AI-Conflict Solver)"}
            {activeTab === 'staff' && "รายชื่อบุคลากรพยาบาล"}
            {activeTab === 'rules' && "ตัวสร้างกฎครอบจักรวาล (Universal Rule Builder)"}
            {activeTab === 'wardconfig' && "ตั้งค่าความต้องการบุคลากรประจำวอร์ด"}
            {activeTab === 'leave' && "จัดการวันลาบุคลากร"}
            {activeTab === 'swap' && "ระบบแลกเวร (Shift Swap)"}
            {activeTab === 'dashboard' && "แดชบอร์ดสถิติ"}
            {activeTab === 'users' && "จัดการผู้ใช้งานระบบ (Admin)"}
            {activeTab === 'calendar' && "ปฏิทินตารางเวร (Calendar)"}
          </h1>
          <div className="flex items-center gap-4">
            <button onClick={() => setAiChatOpen(true)} className="flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-full text-sm font-medium transition-colors border border-slate-700">
              <MessageSquare className="h-4 w-4 text-brand-500" />
              <span className="hidden sm:inline">Ask AI Assistant</span>
            </button>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-auto p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
              className="h-full"
            >
              {activeTab === 'schedule' && <ScheduleView />}
              {activeTab === 'conflict' && <ConflictSolverView />}
              {activeTab === 'staff' && <StaffView />}
              {activeTab === 'rules' && <RuleBuilderView />}
              {activeTab === 'wardconfig' && <WardConfigView />}
              {activeTab === 'leave' && <LeaveView />}
              {activeTab === 'swap' && <ShiftSwapView />}
              {activeTab === 'dashboard' && <DashboardView />}
              {activeTab === 'users' && <UserManagementView />}
              {activeTab === 'calendar' && <CalendarView />}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      {/* Toast Overlay */}
      <div className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 pointer-events-none">
        <AnimatePresence>
          {toasts.map(t => (
            <motion.div key={t.id} initial={{ opacity: 0, x: 40, scale: 0.9 }} animate={{ opacity: 1, x: 0, scale: 1 }} exit={{ opacity: 0, x: 40, scale: 0.9 }}
              className={`pointer-events-auto px-5 py-3 rounded-xl shadow-2xl text-sm font-medium flex items-center gap-3 border backdrop-blur-lg ${t.type === 'success' ? 'bg-emerald-900/90 border-emerald-500/40 text-emerald-200' :
                t.type === 'error' ? 'bg-red-900/90 border-red-500/40 text-red-200' :
                  'bg-slate-800/90 border-slate-600/40 text-slate-200'
                }`}>
              {t.type === 'success' ? <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0" /> : t.type === 'error' ? <XCircle className="h-4 w-4 text-red-400 flex-shrink-0" /> : <Bell className="h-4 w-4 text-blue-400 flex-shrink-0" />}
              {t.msg}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Profile Modal */}
      <AnimatePresence>
        {profileOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setProfileOpen(false)} />
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="relative w-full max-w-md bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl overflow-hidden">
              <div className="px-6 py-4 border-b border-slate-700/50 flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><User className="h-5 w-5 text-brand-400" /> โปรไฟล์ของฉัน</h3>
                <button onClick={() => setProfileOpen(false)} className="p-1.5 rounded-lg text-slate-400 hover:text-white transition-colors"><X className="h-4 w-4" /></button>
              </div>
              <div className="p-6 space-y-6">
                {/* Avatar */}
                <div className="flex items-center gap-4">
                  <div className="h-16 w-16 rounded-2xl bg-gradient-to-tr from-brand-600 to-purple-600 flex items-center justify-center font-bold text-white text-2xl shadow-xl">
                    {profileName?.charAt(0) || currentUser?.username?.charAt(0)?.toUpperCase()}
                  </div>
                  <div>
                    <p className="text-white font-semibold">{currentUser?.username}</p>
                    <p className="text-xs text-slate-400">{currentUser?.role === 'admin' ? '🔴 Admin' : currentUser?.role === 'head_nurse' ? '🟢 Head Nurse' : '🔵 Nurse'}</p>
                    <p className="text-xs text-slate-500">{currentUser?.ward}</p>
                  </div>
                </div>
                {/* Update Name */}
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-slate-300">ชื่อ-นามสกุล</label>
                  <div className="flex gap-2">
                    <input value={profileName} onChange={e => setProfileName(e.target.value)} className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                    <button onClick={handleSaveProfile} disabled={profileSaving} className="px-4 py-2 bg-brand-600 hover:bg-brand-500 rounded-lg text-sm text-white font-medium disabled:opacity-50">
                      {profileSaving ? '...' : 'บันทึก'}
                    </button>
                  </div>
                </div>
                {/* Change Password */}
                <div className="border-t border-slate-700/50 pt-4 space-y-3">
                  <p className="text-sm font-medium text-slate-300 flex items-center gap-2"><Key className="h-4 w-4" /> เปลี่ยนรหัสผ่าน</p>
                  <input type="password" placeholder="รหัสผ่านปัจจุบัน" value={pwForm.current} onChange={e => setPwForm({ ...pwForm, current: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  <input type="password" placeholder="รหัสผ่านใหม่ (อย่างน้อย 6 ตัว)" value={pwForm.newPw} onChange={e => setPwForm({ ...pwForm, newPw: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  <input type="password" placeholder="ยืนยันรหัสผ่านใหม่" value={pwForm.confirm} onChange={e => setPwForm({ ...pwForm, confirm: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  <button onClick={handleChangePassword} disabled={profileSaving || !pwForm.current || !pwForm.newPw} className="w-full py-2.5 bg-amber-600 hover:bg-amber-500 rounded-lg text-sm text-white font-medium disabled:opacity-40 transition-colors">
                    {profileSaving ? 'กำลังบันทึก...' : 'เปลี่ยนรหัสผ่าน'}
                  </button>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* AI Chat Modal */}
      <AnimatePresence>
        {aiChatOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setAiChatOpen(false)} />
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="relative w-full max-w-lg bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl flex flex-col max-h-[80vh]">
              <div className="px-6 py-4 border-b border-slate-700/50 flex justify-between items-center">
                <h3 className="text-lg font-bold text-white flex items-center gap-2"><MessageSquare className="h-5 w-5 text-brand-400" />AI Assistant (Gemini)</h3>
                <button onClick={() => setAiChatOpen(false)} className="text-slate-400 hover:text-white"><X className="h-5 w-5" /></button>
              </div>
              <div className="flex-1 overflow-auto p-4 space-y-3 min-h-[300px]">
                {aiMessages.length === 0 && <p className="text-slate-500 text-center py-10">ถามอะไรก็ได้เกี่ยวกับตารางเวร เช่น &quot;ใครลงเวรดึกเยอะสุด?&quot;</p>}
                {aiMessages.map((msg, i) => (
                  <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] px-4 py-2 rounded-2xl text-sm whitespace-pre-wrap ${msg.role === 'user' ? 'bg-brand-600 text-white' : 'bg-slate-700 text-slate-200'}`}>{msg.text}</div>
                  </div>
                ))}
                {aiLoading && <div className="flex justify-start"><div className="bg-slate-700 px-4 py-2 rounded-2xl text-sm text-slate-400">กำลังคิด...</div></div>}
              </div>
              <div className="p-4 border-t border-slate-700/50 flex gap-2">
                <input value={aiInput} onChange={e => setAiInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendAiMessage()} placeholder="พิมพ์คำถาม..." className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                <button onClick={sendAiMessage} disabled={aiLoading} className="px-4 py-2 bg-brand-600 hover:bg-brand-500 rounded-xl text-white transition-colors disabled:opacity-50"><Send className="h-4 w-4" /></button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

// Subcomponents

function NavItem({ icon, label, isActive, onClick, isOpen, badge }: any) {
  return (
    <button
      onClick={onClick}
      className={`
        w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200
        ${isActive
          ? 'bg-brand-500/10 text-brand-400 border border-brand-500/20 shadow-inner'
          : 'text-slate-400 hover:bg-white/5 hover:text-slate-200'}
        ${!isOpen && 'justify-center'}
      `}
      title={!isOpen ? label : undefined}
    >
      <div className={`relative flex-shrink-0 ${isActive ? 'text-brand-400' : ''}`}>
        {icon}
        {badge !== undefined && (
          <span className="absolute -top-1.5 -right-1.5 h-4 w-4 bg-red-500 text-white text-[9px] font-bold rounded-full flex items-center justify-center">
            {badge > 9 ? '9+' : badge}
          </span>
        )}
      </div>
      <AnimatePresence mode="wait">
        {isOpen && (
          <motion.span
            initial={{ opacity: 0, width: 0 }}
            animate={{ opacity: 1, width: 'auto' }}
            exit={{ opacity: 0, width: 0 }}
            className="font-medium whitespace-nowrap overflow-hidden text-left flex-1 flex items-center justify-between"
          >
            {label}
            {badge !== undefined && (
              <span className="ml-2 px-1.5 py-0.5 bg-red-500 text-white text-[9px] font-bold rounded-full">
                {badge > 9 ? '9+' : badge}
              </span>
            )}
          </motion.span>
        )}
      </AnimatePresence>
    </button>
  );
}


function ScheduleView() {
  const [loading, setLoading] = useState(false);
  const [schedule, setSchedule] = useState<any>(null);
  const [scheduleDays, setScheduleDays] = useState<number>(7);
  const [errorChart, setErrorChart] = useState<any>(null);
  const [fairnessScore, setFairnessScore] = useState<number | null>(90);
  const [activeRules, setActiveRules] = useState<any[]>([]);
  const [selectedWard, setSelectedWard] = useState<string>('');
  const [wards, setWards] = useState<any[]>([]);
  const [selectedMonth, setSelectedMonth] = useState<string>('2026-03');
  const [wardStaff, setWardStaff] = useState<any[]>([]);
  const [startOnCallStaffId, setStartOnCallStaffId] = useState<string>('auto');

  const isIT = !!(selectedWard && (
    selectedWard.toLowerCase().includes('it') ||
    selectedWard.includes('ไอที') ||
    selectedWard.toLowerCase().includes('information technology')
  ));

  useEffect(() => {
    if (!selectedWard) return;
    setStartOnCallStaffId('auto');
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          const filtered = data.filter((s: any) => s.is_active && (s.ward === selectedWard || (!s.ward && selectedWard === 'แผนก ER (ฉุกเฉิน)')));
          setWardStaff(filtered);
        }
      })
      .catch(err => console.error(err));
  }, [selectedWard]);

  useEffect(() => {
    // Fetch rules to show in the summary
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/rules/')
      .then(res => res.json())
      .then(data => setActiveRules(data.filter((r: any) => r.is_active)))
      .catch(err => console.error(err));

    // Fetch wards
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/ward-config/', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
    })
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data)) {
          setWards(data);
          if (data.length > 0) setSelectedWard(data[0].ward_name);
        } else {
          setWards([]);
        }
      })
      .catch(err => console.error(err));
  }, []);

  const generateSchedule = async () => {
    setLoading(true);
    try {
      // 1. Fetch active staff from DB
      const staffRes = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      const staffList = await staffRes.json();

      const activeNurses = staffList
        .filter((s: any) => s.is_active && (s.ward === selectedWard || (!s.ward && selectedWard === 'แผนก ER (ฉุกเฉิน)')))
        .map((s: any) => ({
          id: s.id.toString(),
          name: `${s.employee_id} (${s.name}${s.seniority !== 'N/A' ? ` - ${s.seniority}` : ''})`,
          type: s.role_type,
          seniority: s.seniority
        }));

      if (activeNurses.length === 0) {
        setErrorChart(`ไม่พบบุคลากรที่ Active ใน ${selectedWard} (กรุณาเพิ่มบุคลากรหรือตรวจสอบแผนกก่อนคำนวณ)`);
        setSchedule(null);
        setFairnessScore(null);
        setLoading(false);
        return;
      }

      // 2. Send dynamic data to OR-Tools Backend
      const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/schedule/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` },
        body: JSON.stringify({
          num_days: scheduleDays,
          nurses: activeNurses,
          period: selectedMonth,
          department: selectedWard,
          start_on_call_staff_id: startOnCallStaffId !== 'auto' ? startOnCallStaffId : undefined
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setSchedule(data.schedule);
        setFairnessScore(data.fairness_score);
        setErrorChart(null);
      } else {
        setErrorChart(data.message);
      }
    } catch (err) {
      console.error(err);
      setErrorChart("ไม่สามารถเชื่อมต่อกับ AI Backend ได้");
    }
    setLoading(false);
  };

  return (
    <div className="flex flex-col gap-6 h-full">
      {/* Top Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <select value={selectedWard} onChange={(e) => setSelectedWard(e.target.value)} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500">
            {Array.isArray(wards) ? wards.map((w) => (
              <option key={w.id} value={w.ward_name}>{w.ward_name}</option>
            )) : <option value="">กำลังโหลดแผนก...</option>}
          </select>
          <select value={scheduleDays} onChange={(e) => setScheduleDays(Number(e.target.value))} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500">
            <option value={7}>7 วัน (รายสัปดาห์)</option>
            <option value={14}>14 วัน (ครึ่งเดือน)</option>
            <option value={28}>28 วัน (4 สัปดาห์)</option>
            <option value={30}>30 วัน (รายเดือน)</option>
          </select>
          <input type="month" value={selectedMonth} onChange={(e) => setSelectedMonth(e.target.value)} className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
          {selectedWard && (selectedWard.toLowerCase().includes('it') || selectedWard.includes('ไอที') || selectedWard.toLowerCase().includes('information technology')) && (
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400 whitespace-nowrap">เริ่มเวร On-Call:</span>
              <select 
                value={startOnCallStaffId} 
                onChange={(e) => setStartOnCallStaffId(e.target.value)} 
                className="bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="auto">🔄 อัตโนมัติ (ต่อจากเดือนก่อน)</option>
                {wardStaff.map((s) => (
                  <option key={s.id} value={s.id.toString()}>
                    👤 {s.employee_id} - {s.name}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>
        <div className="flex items-center gap-3">
          {schedule && (
            <button
              onClick={async () => {
                if (!schedule) return;
                try {
                  const ExcelJS = await import('exceljs');
                  const workbook = new ExcelJS.Workbook();
                  const worksheet = workbook.addWorksheet('ตารางเวร');

                  // Enable grid lines
                  worksheet.views = [{ showGridLines: true }];

                  // Set column widths
                  worksheet.getColumn(1).width = 32; // Staff name
                  for (let i = 0; i < scheduleDays; i++) {
                    worksheet.getColumn(i + 2).width = 8; // Days
                  }
                  worksheet.getColumn(scheduleDays + 2).width = 12; // Total shifts

                  const totalCols = scheduleDays + 2;

                  // 1. Title Banner
                  worksheet.mergeCells(1, 1, 1, totalCols);
                  const titleCell = worksheet.getCell(1, 1);
                  const monthLabel = selectedMonth
                    ? new Date(selectedMonth + '-01').toLocaleDateString('th-TH', { year: 'numeric', month: 'long' })
                    : '';
                  titleCell.value = `ตารางจัดเวร: ${selectedWard || 'แผนก ER (ฉุกเฉิน)'}${monthLabel ? '  |  ' + monthLabel : ''}`;
                  titleCell.font = { name: 'Tahoma', size: 16, bold: true, color: { argb: 'FFFFFFFF' } };
                  titleCell.alignment = { vertical: 'middle', horizontal: 'center' };
                  titleCell.fill = {
                    type: 'pattern',
                    pattern: 'solid',
                    fgColor: { argb: 'FF1E3A8A' } // Dark Blue (1E3A8A)
                  };
                  worksheet.getRow(1).height = 40;

                  // 2. Subtitle
                  worksheet.mergeCells(2, 1, 2, totalCols);
                  const subtitleCell = worksheet.getCell(2, 1);
                  const currentDate = new Date().toLocaleDateString('th-TH');
                  subtitleCell.value = `สร้างโดย JadVen.ai (AI-assisted scheduling) | ประจำเดือน: ${monthLabel || '-'} | ออกรายงานเมื่อ ${currentDate}`;
                  subtitleCell.font = { name: 'Tahoma', size: 10, italic: true, color: { argb: 'FF475569' } };
                  subtitleCell.alignment = { vertical: 'middle', horizontal: 'center' };
                  worksheet.getRow(2).height = 20;

                  // Row 3 is empty
                  worksheet.getRow(3).height = 15;

                  // 4. Table Headers Row
                  const headerRowNumber = 4;
                  const headers = ['บุคลากร', ...Array.from({ length: scheduleDays }, (_, i) => (i + 1).toString()), 'รวมกะ'];
                  worksheet.getRow(headerRowNumber).values = headers;
                  worksheet.getRow(headerRowNumber).height = 28;

                  // Style Header Row
                  worksheet.getRow(headerRowNumber).eachCell((cell, colNum) => {
                    cell.font = { name: 'Tahoma', size: 11, bold: true, color: { argb: 'FFFFFFFF' } };
                    cell.fill = {
                      type: 'pattern',
                      pattern: 'solid',
                      fgColor: { argb: 'FF1E293B' } // Slate-800
                    };
                    cell.alignment = { vertical: 'middle', horizontal: colNum === 1 ? 'left' : 'center' };
                    cell.border = {
                      top: { style: 'thin', color: { argb: 'FF475569' } },
                      left: { style: 'thin', color: { argb: 'FF475569' } },
                      bottom: { style: 'medium', color: { argb: 'FF0F172A' } },
                      right: { style: 'thin', color: { argb: 'FF475569' } }
                    } as any;
                  });

                  let currentRow = 5;
                  const rns = schedule.filter((r: any) => r.type === 'RN');
                  const nas = schedule.filter((r: any) => r.type !== 'RN');

                  const borderThin: any = {
                    top: { style: 'thin', color: { argb: 'FFCBD5E1' } },
                    left: { style: 'thin', color: { argb: 'FFCBD5E1' } },
                    bottom: { style: 'thin', color: { argb: 'FFCBD5E1' } },
                    right: { style: 'thin', color: { argb: 'FFCBD5E1' } }
                  };

                  const addSeparator = (title: string, bgColor: string, textColor: string) => {
                    worksheet.mergeCells(currentRow, 1, currentRow, totalCols);
                    const cell = worksheet.getCell(currentRow, 1);
                    cell.value = title;
                    cell.font = { name: 'Tahoma', size: 10, bold: true, color: { argb: textColor } };
                    cell.fill = {
                      type: 'pattern',
                      pattern: 'solid',
                      fgColor: { argb: bgColor }
                    };
                    cell.alignment = { vertical: 'middle', horizontal: 'center' };
                    worksheet.getRow(currentRow).height = 24;
                    currentRow++;
                  };

                  const addStaffRows = (staffList: any[]) => {
                    staffList.forEach((row: any) => {
                      const displayShifts = row.shifts.map((shiftVal: string, idx: number) => {
                        if (isIT) {
                          if (shiftVal === 'N') {
                            let isWeekend = false;
                            if (selectedMonth && selectedMonth.includes('-')) {
                              const [yrStr, moStr] = selectedMonth.split('-');
                              const dDate = new Date(parseInt(yrStr), parseInt(moStr) - 1, idx + 1);
                              const day = dDate.getDay();
                              isWeekend = (day === 0 || day === 6);
                            }
                            return isWeekend ? 'On-Call' : 'M / N';
                          }
                          if (shiftVal === 'M') return 'M';
                          if (shiftVal === 'OFF') return '—';
                          return shiftVal;
                        }
                        return shiftVal;
                      });

                      const workedShifts = row.shifts.filter((s: string) => s !== 'OFF').length;
                      const morningShifts = row.shifts.filter((s: string) => s === 'M').length;
                      const onCallShifts  = row.shifts.filter((s: string) => s === 'N').length;
                      const onCallWeeks   = Math.round(onCallShifts / 7);

                      const totalVal = isIT 
                        ? `${morningShifts}M / ${onCallWeeks}Wk`
                        : workedShifts;

                      const values = [row.nurse, ...displayShifts, totalVal];
                      
                      const newRow = worksheet.getRow(currentRow);
                      newRow.values = values;
                      newRow.height = 26;
 
                       // Style name cell
                       const nameCell = newRow.getCell(1);
                       nameCell.font = { name: 'Tahoma', size: 10, bold: true, color: { argb: 'FF1E293B' } };
                       nameCell.alignment = { vertical: 'middle', horizontal: 'left' };
                       nameCell.border = borderThin;
 
                       // Style shift cells
                       for (let i = 0; i < scheduleDays; i++) {
                         const shiftCell = newRow.getCell(i + 2);
                         const shiftVal = row.shifts[i];
                         shiftCell.alignment = { vertical: 'middle', horizontal: 'center' };
                         shiftCell.border = borderThin;
 
                         if (shiftVal === 'M') {
                           shiftCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFD1FAE5' } }; // Light Emerald
                           shiftCell.font = { name: 'Tahoma', size: 10, bold: true, color: { argb: 'FF065F46' } };
                         } else if (shiftVal === 'E') {
                           shiftCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFFEF3C7' } }; // Light Amber
                           shiftCell.font = { name: 'Tahoma', size: 10, bold: true, color: { argb: 'FF92400E' } };
                         } else if (shiftVal === 'N') {
                           shiftCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF3E8FF' } }; // Light Purple
                           shiftCell.font = { name: 'Tahoma', size: 10, bold: true, color: { argb: 'FF6B21A8' } };
                         } else {
                           // OFF
                           shiftCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF1F5F9' } }; // Light Slate/Gray
                           shiftCell.font = { name: 'Tahoma', size: 10, color: { argb: 'FF94A3B8' } };
                         }
                       }
 
                       // Style total cell
                       const totalCell = newRow.getCell(totalCols);
                       totalCell.font = { name: 'Tahoma', size: 10, bold: true, color: { argb: 'FF1D4ED8' } }; // Brand Blue
                       totalCell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFEFF6FF' } };
                       totalCell.alignment = { vertical: 'middle', horizontal: 'center' };
                       totalCell.border = borderThin;
 
                       currentRow++;
                     });
                   };
 
                   if (rns.length > 0) {
                     addSeparator('--- พยาบาลวิชาชีพ (RN) ---', 'FFDBEAFE', 'FF1E40AF');
                     addStaffRows(rns);
                   }
 
                   if (nas.length > 0) {
                     const sepTitle = isIT ? '--- เจ้าหน้าที่ไอที ---' : '--- ทีมสนับสนุน / ผู้ช่วย (PN/NA/PL/TN) ---';
                     addSeparator(sepTitle, 'FFF1F5F9', 'FF475569');
                     addStaffRows(nas);
                   }

                  // Write buffer and download
                  const buffer = await workbook.xlsx.writeBuffer();
                  const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = `schedule_${selectedWard.replace(/\s+/g, '_') || 'ward'}.xlsx`;
                  a.click();
                  URL.revokeObjectURL(url);
                } catch (err) {
                  console.error('Failed to export Excel:', err);
                  alert('เกิดข้อผิดพลาดในการส่งออก Excel');
                }
              }}
              className="flex items-center gap-2 px-4 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-all shadow-lg shadow-emerald-600/20"
            >
              <Download className="h-4 w-4" />
              <span>Export Excel</span>
            </button>
          )}
          {schedule && (
            <button
              onClick={async () => {
                if (!schedule) return;
                const { default: jsPDF } = await import('jspdf');
                const { default: autoTable } = await import('jspdf-autotable');
                const doc = new jsPDF({ orientation: 'landscape' });
                const days = Array.from({ length: scheduleDays }, (_, i) => `D${i + 1}`);

                // Load Thai Font from public directory
                try {
                  const fontRes = await fetch('/fonts/Sarabun-Regular.ttf');
                  if (fontRes.ok) {
                    const blob = await fontRes.blob();
                    const base64Font = await new Promise<string>((resolve) => {
                      const reader = new FileReader();
                      reader.onloadend = () => resolve((reader.result as string).split(',')[1]);
                      reader.readAsDataURL(blob);
                    });
                    doc.addFileToVFS('Sarabun-Regular.ttf', base64Font);
                    doc.addFont('Sarabun-Regular.ttf', 'Sarabun', 'normal');
                    doc.setFont('Sarabun');
                  } else {
                    doc.setFont('helvetica');
                  }
                } catch (e) {
                  console.error('Failed to load font:', e);
                  doc.setFont('helvetica');
                }

                doc.setFontSize(16);
                doc.text('JadVen.ai - Schedule Report', 14, 15);
                doc.setFontSize(10);
                doc.text(`Generated: ${new Date().toLocaleDateString('th-TH')} for Ward: ${selectedWard}`, 14, 22);

                const rns = schedule.filter((r: any) => r.type === 'RN');
                const nas = schedule.filter((r: any) => r.type !== 'RN');

                const tableBody: any[] = [];
                if (rns.length > 0) {
                  tableBody.push([{ content: '--- พยาบาลวิชาชีพ (RN) ---', colSpan: scheduleDays + 1, styles: { halign: 'center', fillColor: [59, 130, 246, 0.1], textColor: [59, 130, 246], fontStyle: 'bold' } }]);
                  rns.forEach((r: any) => tableBody.push([r.nurse, ...r.shifts]));
                }
                if (nas.length > 0) {
                  tableBody.push([{ content: '--- ทีมสนับสนุน / ผู้ช่วย (PN/NA/PL/TN) ---', colSpan: scheduleDays + 1, styles: { halign: 'center', fillColor: [226, 232, 240], textColor: [71, 85, 105], fontStyle: 'bold' } }]);
                  nas.forEach((r: any) => tableBody.push([r.nurse, ...r.shifts]));
                }

                autoTable(doc, {
                  startY: 28,
                  head: [['Nurse', ...days]],
                  body: tableBody,
                  styles: { fontSize: 9, cellPadding: 3 },
                  headStyles: { fillColor: [59, 130, 246], textColor: 255, fontStyle: 'bold' },
                  alternateRowStyles: { fillColor: [240, 245, 255] },
                  columnStyles: { 0: { fontStyle: 'bold', cellWidth: 40 } },
                });
                doc.save('schedule_jadven.pdf');
              }}
              className="flex items-center gap-2 px-4 py-2.5 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-all shadow-lg shadow-purple-600/20"
            >
              <FileText className="h-4 w-4" />
              <span>Export PDF</span>
            </button>
          )}
          <button
            onClick={generateSchedule}
            disabled={loading}
            className="flex items-center gap-2 px-6 py-2.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg font-medium transition-all focus:ring-2 focus:ring-brand-500 focus:ring-offset-2 focus:ring-offset-slate-900 shadow-lg shadow-brand-600/20 disabled:opacity-50"
          >
            {loading ? (
              <div className="h-4 w-4 rounded-full border-2 border-white/20 border-t-white animate-spin" />
            ) : (
              <Activity className="h-4 w-4" />
            )}
            <span>{loading ? 'AI กำลังคำนวณ 1,000+ ความเป็นไปได้...' : 'สร้างตารางด้วย OR-Tools AI'}</span>
          </button>
        </div>
      </div>

      {/* Main Table Area */}
      <div className="flex-1 glass-card overflow-hidden flex flex-col">
        {errorChart && (
          <div className="m-4 p-4 border border-red-500/30 bg-red-500/10 text-red-400 rounded-xl flex items-center gap-3">
            <AlertTriangle className="h-5 w-5" />
            <p>{errorChart}</p>
          </div>
        )}

        {!schedule && !loading && !errorChart && (
          <div className="flex-1 flex flex-col items-center justify-center text-slate-400 space-y-4">
            <CalendarDays className="h-16 w-16 opacity-20" />
            <p>กดปุ่ม "สร้างตารางด้วย OR-Tools AI" เพื่อเริ่มคำนวณเวร</p>
          </div>
        )}

        {schedule && (
          <div className="flex-1 overflow-auto">
            {(() => {
              // --- Pre-compute on-call week ranges for IT ---
              // A "week" = 7 consecutive days (0-based). An on-call week for a nurse
              // is any 7-day window where that nurse has N shifts.
              // Build a map: dayIndex -> which nurse's on-call week it is.
              const onCallDayNurseMap: Record<number, number> = {};
              const onCallWeekRanges: Array<{start: number; end: number}> = [];
              if (isIT && schedule.length > 0) {
                const numWeeks = Math.floor(scheduleDays / 7);
                for (let w = 0; w < numWeeks; w++) {
                  const wStart = w * 7;
                  const wEnd = Math.min(wStart + 7, scheduleDays);
                  // Find which nurse is on-call (has N) in this week
                  for (let nIdx = 0; nIdx < schedule.length; nIdx++) {
                    const nurse = schedule[nIdx];
                    const hasN = nurse.shifts.slice(wStart, wEnd).some((s: string) => s === 'N');
                    if (hasN) {
                      for (let d = wStart; d < wEnd; d++) onCallDayNurseMap[d] = nIdx;
                      onCallWeekRanges.push({ start: wStart, end: wEnd - 1 });
                      break;
                    }
                  }
                }
              }

              // --- Color palette for on-call week banding (cycles per week) ---
              const weekBandColors = [
                'bg-purple-900/25 border-purple-700/30',
                'bg-violet-900/20 border-violet-700/30',
                'bg-indigo-900/20 border-indigo-700/30',
                'bg-fuchsia-900/20 border-fuchsia-700/30',
              ];
              const getOnCallWeekIdx = (dayIdx: number): number => {
                for (let i = 0; i < onCallWeekRanges.length; i++) {
                  if (dayIdx >= onCallWeekRanges[i].start && dayIdx <= onCallWeekRanges[i].end)
                    return i;
                }
                return -1;
              };

              return (
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="sticky top-0 bg-slate-800/90 backdrop-blur shadow-sm z-10">
                    {isIT && onCallWeekRanges.length > 0 && (
                      <tr className="border-b border-slate-700/50">
                        <th className="sticky left-0 bg-slate-800 z-20 px-6 py-2 text-xs text-slate-500 border-r border-slate-700/50"></th>
                        {[...Array(scheduleDays)].map((_, i) => {
                          const wIdx = getOnCallWeekIdx(i);
                          const isFirst = wIdx >= 0 && onCallWeekRanges[wIdx]?.start === i;
                          const isLast  = wIdx >= 0 && onCallWeekRanges[wIdx]?.end   === i;
                          const nurseName = wIdx >= 0 && onCallDayNurseMap[i] !== undefined
                            ? schedule[onCallDayNurseMap[i]]?.nurse?.split('(')[0]?.trim() || ''
                            : '';
                          if (wIdx >= 0 && isFirst) {
                            const span = onCallWeekRanges[wIdx].end - onCallWeekRanges[wIdx].start + 1;
                            return (
                              <th key={i} colSpan={span} className="py-1.5 text-center text-[10px] font-bold text-purple-300">
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-purple-500/20 border border-purple-500/30">
                                  <span>🔔</span> {nurseName} — On-Call Week {wIdx + 1}
                                </span>
                              </th>
                            );
                          } else if (wIdx >= 0 && !isFirst) {
                            return null;
                          }
                          return (
                            <th key={i} className="px-4 py-1.5 text-center">
                              <span className="text-[10px] text-slate-600">—</span>
                            </th>
                          );
                        })}
                        <th className="px-6 py-1.5 border-l border-slate-700/50"></th>
                      </tr>
                    )}
                    <tr>
                      <th className="sticky left-0 bg-slate-800 z-20 px-6 py-4 font-semibold text-slate-300 border-r border-slate-700/50">บุคลากร</th>
                      {[...Array(scheduleDays)].map((_, i) => {
                        const wIdx = getOnCallWeekIdx(i);
                        return (
                          <th key={i} className={`px-2 py-4 font-semibold text-center text-slate-300 ${
                            isIT && wIdx >= 0 ? 'border-l border-r border-purple-700/20' : ''
                          }`}>
                            <div className="text-xs text-slate-500">{i + 1}</div>
                          </th>
                        );
                      })}
                      <th className="px-6 py-4 font-semibold text-center text-slate-300 border-l border-slate-700/50">รวมกะ</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-700/50">
                    {[
                      ...schedule.filter((r: any) => r.type === 'RN'),
                      ...(schedule.some((r: any) => r.type === 'RN') && schedule.some((r: any) => r.type !== 'RN') ? [{ isSeparator: true, title: '--- ทีมสนับสนุน / ผู้ช่วย (PN/NA/PL/TN) ---' }] : []),
                      ...schedule.filter((r: any) => r.type !== 'RN')
                    ].map((row: any, i: number) => {
                      if (row.isSeparator) {
                        return (
                          <tr key={`sep-${i}`} className="bg-slate-800/80">
                            <td colSpan={scheduleDays + 2} className="px-6 py-2 text-center text-sm font-bold text-slate-400 border-y border-slate-700 uppercase tracking-widest">
                              {row.title}
                            </td>
                          </tr>
                        );
                      }

                      const workedShifts  = row.shifts.filter((s: string) => s !== 'OFF').length;
                      const morningShifts = row.shifts.filter((s: string) => s === 'M').length;
                      const onCallShifts  = row.shifts.filter((s: string) => s === 'N').length;
                      const onCallWeeks   = Math.round(onCallShifts / 7);

                      return (
                        <tr key={i} className="hover:bg-slate-700/20 transition-colors group">
                          <td className="sticky left-0 bg-slate-900 z-10 group-hover:bg-slate-800 transition-colors px-6 py-4 border-r border-slate-700/50">
                            <div className="font-medium text-slate-200">{row.nurse.split('(')[0].trim()}</div>
                            <div className="text-xs text-slate-500">{row.type} {row.nurse.includes('Senior') ? '- Senior' : row.nurse.includes('Junior') ? '- Junior' : ''}</div>
                            {isIT && (
                              <div className="flex gap-1 mt-1 flex-wrap">
                                {morningShifts > 0 && (
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/15 text-emerald-400 border border-emerald-500/20 font-medium">
                                    ☀️ {morningShifts}M
                                  </span>
                                )}
                                {onCallWeeks > 0 && (
                                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-purple-500/15 text-purple-400 border border-purple-500/20 font-medium">
                                    🔔 {onCallWeeks}สัปดาห์
                                  </span>
                                )}
                              </div>
                            )}
                          </td>
                          {row.shifts.map((shift: string, dIndex: number) => {
                            const onCallWkIdx = isIT ? getOnCallWeekIdx(dIndex) : -1;
                            const isThisNurseOnCall = isIT && shift === 'N';
                            const bandClass = (isIT && onCallWkIdx >= 0)
                              ? weekBandColors[onCallWkIdx % weekBandColors.length]
                              : '';
                            const isWeekStart = isIT && onCallWkIdx >= 0 && onCallWeekRanges[onCallWkIdx]?.start === dIndex;
                            const isWeekEnd   = isIT && onCallWkIdx >= 0 && onCallWeekRanges[onCallWkIdx]?.end   === dIndex;

                            let isWeekend = false;
                            if (selectedMonth && selectedMonth.includes('-')) {
                              const [yrStr, moStr] = selectedMonth.split('-');
                              const dDate = new Date(parseInt(yrStr), parseInt(moStr) - 1, dIndex + 1);
                              const day = dDate.getDay();
                              isWeekend = (day === 0 || day === 6);
                            }

                            return (
                              <td
                                key={dIndex}
                                className={`px-2 py-3 text-center ${
                                  isIT && onCallWkIdx >= 0
                                    ? `${bandClass} ${
                                        isWeekStart ? 'rounded-l-lg border-l-2' :
                                        isWeekEnd   ? 'rounded-r-lg border-r-2' : 'border-x'
                                      } border-purple-700/30`
                                    : 'px-4'
                                }`}
                              >
                                {isThisNurseOnCall ? (
                                  <div
                                    title={isWeekend ? "On-Call Standby Only" : "Morning Shift + On-Call Standby"}
                                    className={`inline-flex flex-col items-center justify-center w-14 h-10 rounded-lg font-bold border transition-all cursor-pointer hover:scale-105 shadow-sm gap-0.5
                                      ${isWeekend 
                                        ? 'bg-purple-600/35 text-purple-300 border-purple-500/40 text-[10px]' 
                                        : 'bg-gradient-to-br from-emerald-500/25 to-purple-500/35 text-slate-200 border-purple-500/40 text-[11px]'
                                      }
                                    `}
                                  >
                                    {isWeekend ? (
                                      <>
                                        <span className="text-xs leading-none">🔔</span>
                                        <span className="leading-none text-[9px]">On-Call</span>
                                      </>
                                    ) : (
                                      <>
                                        <span className="leading-none font-extrabold text-slate-100">M / N</span>
                                        <span className="text-[8px] leading-none opacity-85 text-emerald-300 font-medium">เช้า + ออนคอล</span>
                                      </>
                                    )}
                                  </div>
                                ) : (
                                  <div className={`
                                    inline-flex items-center justify-center w-12 h-10 rounded-lg text-sm font-bold border transition-all cursor-pointer hover:scale-105 shadow-sm
                                    ${shift === 'M'   ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/20' : ''}
                                    ${shift === 'E'   ? 'bg-amber-500/20   text-amber-400   border-amber-500/20'   : ''}
                                    ${shift === 'OFF' ? 'bg-slate-800      text-slate-500   border-slate-700'       : ''}
                                  `}>
                                    {shift === 'M' && isIT ? '☀️' : shift === 'OFF' ? '' : shift}
                                    {shift === 'OFF' ? <span className="text-slate-600 text-xs">—</span> : null}
                                  </div>
                                )}
                              </td>
                            );
                          })}
                          <td className="px-6 py-4 text-center border-l border-slate-700/50">
                            {isIT ? (
                              <div className="flex flex-col items-center gap-0.5">
                                <div className="text-xs text-emerald-400 font-medium">{morningShifts}M</div>
                                {onCallWeeks > 0 && <div className="text-xs text-purple-400 font-medium">🔔{onCallWeeks}wk</div>}
                              </div>
                            ) : (
                              <div className="inline-flex items-center justify-center bg-slate-800 rounded-lg px-3 py-1 text-sm font-medium border border-slate-700">
                                <span className="text-brand-400 font-bold">{workedShifts}</span><span className="text-slate-500 text-xs ml-1">กะ</span>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              );
            })()}
          </div>
        )}
      </div>

      {schedule && (
        <div className="grid grid-cols-3 gap-6">
          <div className="glass-card p-4 flex flex-col gap-2">
            <div className="text-sm text-slate-400 flex items-center justify-between">
              <span>กฏพื้นฐาน (Core Rules)</span>
              <span className="text-emerald-400 font-bold">Applied</span>
            </div>
            <div className="text-xs space-y-1 mt-2">
              {activeRules.filter(r => r.rule_type === 'global').map((r, idx) => (
                <div key={idx} className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-emerald-400"></div> {r.name.split('(')[0].trim()}</div>
              ))}
              {activeRules.filter(r => r.rule_type === 'global').length === 0 && <span className="text-slate-500 italic">ไม่มีกฎที่เปิดใช้งาน</span>}
            </div>
          </div>
          <div className="glass-card p-4 flex flex-col gap-2">
            <div className="text-sm text-slate-400 flex items-center justify-between">
              <span>พยาบาลเวร (Staffing Mix)</span>
              <span className="text-amber-400 font-bold">Standard</span>
            </div>
            <div className="text-xs space-y-1 mt-2">
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-amber-400"></div> เน้นกระจายเวรให้เท่าเทียม</div>
              <div className="flex items-center gap-2"><div className="w-1.5 h-1.5 rounded-full bg-amber-400"></div> มี RN คุมกะ M และ N เสมอ</div>
            </div>
          </div>
          <div className="glass-card p-4 flex flex-col gap-2">
            <div className="text-sm text-slate-400 flex items-center justify-between">
              <span>Fairness Score</span>
              <span className="text-brand-400 font-bold">{fairnessScore}/100</span>
            </div>
            <div className="w-full bg-slate-700 rounded-full h-1.5 mt-auto">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${fairnessScore}%` }}
                className="bg-gradient-to-r from-brand-600 to-emerald-400 h-1.5 rounded-full"
              />
            </div>
          </div>
        </div>
      )}

    </div>
  );
}

function ConflictSolverView() {
  const [request, setRequest] = useState("พยาบาลสมศรีขอลากะทันหันพรุ่งนี้ ช่วยปรับตารางให้หน่อย");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);

  const handlePrompt = async () => {
    setLoading(true);
    try {
      const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/prompt/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_message: request })
      });
      const data = await res.json();
      if (data.status === 'success') {
        setResponse(data.extracted_data);
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  }

  return (
    <div className="h-full flex flex-col gap-6 max-w-4xl mx-auto">
      <div className="text-center space-y-2 mb-4">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center mb-2 shadow-inner border border-white/5">
          <AlertTriangle className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">จัดการเหตุฉุกเฉินกะทันหัน (Gemini 1.5 Pro)</h2>
        <p className="text-slate-400">สื่อสารกับ AI ด้วยภาษาธรรมชาติ เพื่อปรับตารางเวรแบบ Real-time</p>
      </div>

      <div className="glass-card p-6 flex flex-col gap-4">
        <label className="text-sm font-medium text-slate-300">ระบุปัญหา (Natural Language Input)</label>
        <textarea
          className="w-full bg-slate-900/50 border border-slate-700/50 rounded-xl p-4 text-white focus:outline-none focus:ring-2 focus:ring-brand-500/50 min-h-[120px] resize-none"
          placeholder="เช่น: พรุ่งนี้ RN-A ป่วยกะทันหัน หาคนขึ้นเวรเช้าแทนให้หน่อย..."
          value={request}
          onChange={(e) => setRequest(e.target.value)}
        ></textarea>
        <div className="flex justify-end">
          <button
            onClick={handlePrompt}
            disabled={loading}
            className="px-6 py-2.5 bg-gradient-to-r from-purple-600 to-brand-600 text-white font-medium rounded-lg flex items-center gap-2 hover:shadow-lg hover:shadow-brand-500/20 transition-all disabled:opacity-50"
          >
            {loading ? <div className="h-4 w-4 rounded-full border-2 border-white/20 border-t-white animate-spin" /> : <MessageSquare className="h-4 w-4" />}
            <span>วิเคราะห์และแก้ไขปัญหา</span>
          </button>
        </div>
      </div>

      <AnimatePresence>
        {response && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass-card p-6 border border-emerald-500/30 ring-1 ring-emerald-500/10 shadow-[0_0_30px_rgba(16,185,129,0.1)] relative overflow-hidden"
          >
            <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2 text-emerald-400">
              <Activity className="h-5 w-5" />
              AI เสนอทางเลือก (Conflict Resolution Options)
            </h3>

            <div className="space-y-4">
              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700/50 relative group hover:border-brand-500/50 transition-colors cursor-pointer">
                <div className="absolute -left-3 top-1/2 -translate-y-1/2 bg-emerald-500 text-white w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ring-4 ring-slate-800">1</div>
                <h4 className="font-semibold text-white mb-1">Option A: เสนอ RN-B สลับเวร</h4>
                <p className="text-sm text-slate-400">ให้ RN-B ขึ้นเวรเช้าแทน (ปัจจุบันหยุด) และชดเชยวันหยุดให้ในสัปดาห์หน้า กฎเหล็ก 100% Pass</p>
                <button className="mt-3 px-4 py-1.5 bg-brand-500/10 text-brand-400 border border-brand-500/20 rounded-md text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">ยอมรับข้อเสนอนี้</button>
              </div>

              <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700/50 relative group hover:border-brand-500/50 transition-colors cursor-pointer">
                <div className="absolute -left-3 top-1/2 -translate-y-1/2 bg-slate-700 text-slate-300 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ring-4 ring-slate-800">2</div>
                <h4 className="font-semibold text-white mb-1">Option B: ดึงพยาบาลจาก Float Pool</h4>
                <p className="text-sm text-slate-400">แผนกมีคนไม่พอ ร้องขอพยาบาลจากแผนก IPD ที่มีเวรว่างมาช่วยชั่วคราว มีค่าใช้จ่ายเพิ่มเติม 1,500 บาท</p>
                <button className="mt-3 px-4 py-1.5 bg-brand-500/10 text-brand-400 border border-brand-500/20 rounded-md text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">ยอมรับข้อเสนอนี้</button>
              </div>
            </div>

            <div className="mt-6 p-4 bg-slate-950/50 rounded-lg font-mono text-xs text-brand-300 overflow-x-auto border border-white/5">
              <div className="text-slate-500 mb-2">// Raw JSON Data extracted by Gemini:</div>
              <pre>{response}</pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

const getRoleBadgeStyle = (role: string) => {
  switch (role) {
    case 'RN': return 'bg-blue-500/10 text-blue-400 border-blue-500/20';
    case 'TN': return 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20';
    case 'PN': return 'bg-purple-500/10 text-purple-400 border-purple-500/20';
    case 'PL': return 'bg-orange-500/10 text-orange-400 border-orange-500/20';
    case 'NA': return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    case 'IT': return 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20';
    case 'MA': return 'bg-pink-500/10 text-pink-400 border-pink-500/20';
    case 'SEC': return 'bg-red-500/10 text-red-400 border-red-500/20';
    case 'ADM': return 'bg-slate-500/10 text-slate-400 border-slate-500/20';
    default: return 'bg-teal-500/10 text-teal-400 border-teal-500/20';
  }
};

const getRoleLabel = (role: string) => {
  switch (role) {
    case 'RN': return 'พยาบาลวิชาชีพ (RN)';
    case 'TN': return 'พยาบาลเทคนิค (TN)';
    case 'PN': return 'ผู้ช่วยพยาบาล (PN)';
    case 'PL': return 'พนักงานเปล (PL)';
    case 'NA': return 'ผู้ช่วยเหลือ (NA)';
    case 'IT': return 'ไอที (IT)';
    case 'MA': return 'แม่บ้าน/ทำความสะอาด (MA)';
    case 'SEC': return 'รักษาความปลอดภัย (SEC)';
    case 'ADM': return 'ธุรการ/สำนักงาน (ADM)';
    default: return `${role} (อื่นๆ)`;
  }
};

function StaffView() {
  const [staff, setStaff] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<any>(null);
  const [formData, setFormData] = useState({
    employee_id: '',
    name: '',
    role_type: 'RN',
    seniority: 'Senior',
    ward: 'แผนก ER (ฉุกเฉิน)',
    is_active: true
  });

  const fetchStaff = () => {
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(res => res.json())
      .then(data => {
        setStaff(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });

    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/ward-config/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(res => res.json())
      .then(setWards)
      .catch(console.error);
  };

  useEffect(() => {
    fetchStaff();
  }, []);

  const handleAddClick = () => {
    setEditingStaff(null);
    setFormData({
      employee_id: `RN-${Math.floor(100 + Math.random() * 900)}`,
      name: '',
      role_type: 'RN',
      seniority: 'Senior',
      ward: wards.length > 0 ? wards[0].ward_name : 'แผนก ER (ฉุกเฉิน)',
      is_active: true
    });
    setModalOpen(true);
  };

  const handleEditClick = (person: any) => {
    const wardExists = wards.some((w: any) => w.ward_name === person.ward);
    const defaultWard = wards.length > 0 ? wards[0].ward_name : 'แผนก ER (ฉุกเฉิน)';

    setEditingStaff(person);
    setFormData({
      employee_id: person.employee_id,
      name: person.name,
      role_type: person.role_type,
      seniority: person.seniority,
      ward: wardExists ? (person.ward || defaultWard) : defaultWard,
      is_active: person.is_active
    });
    setModalOpen(true);
  };

  const handleDelete = async (id: number) => {
    if (confirm("คุณแน่ใจหรือไม่ที่จะลบพยาบาลท่านนี้?")) {
      try {
        const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/staff/${id}`, { method: 'DELETE' });
        if (!res.ok) {
          const errorData = await res.json();
          alert(errorData.detail || "เกิดข้อผิดพลาดในการลบข้อมูล");
          return;
        }
        fetchStaff();
      } catch (err) {
        console.error(err);
        alert("เกิดข้อผิดพลาดในการลบข้อมูล");
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const url = editingStaff
        ? (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/staff/${editingStaff.id}`
        : '' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/';
      const method = editingStaff ? 'PUT' : 'POST';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!res.ok) {
        const errorData = await res.json();
        alert(errorData.detail || "เกิดข้อผิดพลาดในการบันทึกข้อมูล");
        return;
      }
      setModalOpen(false);
      fetchStaff();
    } catch (err) {
      console.error(err);
      alert("เกิดข้อผิดพลาดในการบันทึกข้อมูล");
    }
  };

  return (
    <>
      <div className="h-full flex flex-col gap-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3 w-full md:w-auto">
            <div className="relative flex-1 md:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="text"
                placeholder="ค้นหาบุคลากร..."
                className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <button className="px-4 py-2 bg-slate-800 border border-slate-700 hover:bg-slate-700 rounded-lg text-sm text-white transition-colors">
              ตัวกรอง (Filter)
            </button>
          </div>
          <button
            onClick={handleAddClick}
            className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-brand-600/20"
          >
            <UserPlus className="h-4 w-4" />
            <span>เพิ่มบุคลากรใหม่</span>
          </button>
        </div>

        <div className="flex-1 glass-card overflow-hidden flex flex-col">
          <div className="overflow-auto">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-slate-800/80 border-b border-slate-700/50">
                <tr>
                  <th className="px-6 py-4 font-semibold text-slate-300">รหัส / ชื่อ-สกุล</th>
                  <th className="px-6 py-4 font-semibold text-slate-300">ตำแหน่ง (Type)</th>
                  <th className="px-6 py-4 font-semibold text-slate-300">ระดับ (Seniority)</th>
                  <th className="px-6 py-4 font-semibold text-slate-300">แผนก (Ward)</th>
                  <th className="px-6 py-4 font-semibold text-slate-300">สถานะ</th>
                  <th className="px-6 py-4 font-semibold text-right text-slate-300">จัดการ</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700/50">
                {loading ? (
                  <tr><td colSpan={5} className="text-center py-8 text-slate-400">กำลังโหลดข้อมูลจาก Database...</td></tr>
                ) : staff.map((person) => (
                  <tr key={person.id} className="hover:bg-slate-700/20 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-white">{person.name}</div>
                      <div className="text-xs text-slate-500">{person.employee_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium border ${getRoleBadgeStyle(person.role_type)}`}>
                        {getRoleLabel(person.role_type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-slate-300">{person.seniority}</td>
                    <td className="px-6 py-4 text-slate-400">{person.ward || '-'}</td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center gap-1.5 ${person.is_active ? 'text-emerald-400' : 'text-amber-400'}`}>
                        <span className={`w-1.5 h-1.5 rounded-full ${person.is_active ? 'bg-emerald-400' : 'bg-amber-400'}`}></span>
                        {person.is_active ? 'Active' : 'On Leave'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right space-x-2">
                      <button onClick={() => handleEditClick(person)} className="p-2 text-slate-400 hover:text-brand-400 hover:bg-brand-400/10 rounded-lg transition-colors">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button onClick={() => handleDelete(person.id)} className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Staff Modal */}
      <AnimatePresence>
        {modalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setModalOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="relative w-full max-w-md bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl flex flex-col overflow-hidden"
            >
              <div className="px-6 py-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/50">
                <h3 className="text-lg font-bold text-white">{editingStaff ? 'แก้ไขข้อมูลบุคลากร' : 'เพิ่มบุคลากรใหม่'}</h3>
              </div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">รหัสพนักงาน (ID)</label>
                  <input required type="text" value={formData.employee_id} onChange={e => setFormData({ ...formData, employee_id: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-not-allowed" placeholder="e.g. RN-A" readOnly />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">ชื่อ-สกุล</label>
                  <input required type="text" value={formData.name} onChange={e => setFormData({ ...formData, name: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="e.g. สมศรี ใจดี" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">ตำแหน่ง</label>
                    <select value={
                      ['RN', 'TN', 'PN', 'PL', 'NA', 'IT', 'MA', 'SEC', 'ADM'].includes(formData.role_type) 
                        ? formData.role_type 
                        : 'CUSTOM'
                    } onChange={e => {
                      const newRole = e.target.value;
                      if (newRole === 'CUSTOM') {
                        setFormData({
                          ...formData,
                          role_type: 'CUSTOM_TEMP'
                        });
                      } else {
                        setFormData({
                          ...formData,
                          role_type: newRole,
                          employee_id: editingStaff ? formData.employee_id : `${newRole}-${Math.floor(100 + Math.random() * 900)}`
                        });
                      }
                    }} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="RN">RN (พยาบาลวิชาชีพ)</option>
                      <option value="TN">TN (พยาบาลเทคนิค)</option>
                      <option value="PN">PN (ผู้ช่วยพยาบาล)</option>
                      <option value="PL">PL (พนักงานเปล)</option>
                      <option value="NA">NA (ผู้ช่วยเหลือ)</option>
                      <option value="IT">IT (เจ้าหน้าที่ไอที)</option>
                      <option value="MA">MA (แม่บ้าน / ทำความสะอาด)</option>
                      <option value="SEC">SEC (รปภ. / รักษาความปลอดภัย)</option>
                      <option value="ADM">ADM (ธุรการ / สำนักงาน)</option>
                      <option value="CUSTOM">อื่นๆ (ระบุรหัสตำแหน่งเอง...)</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">ระดับประสบการณ์</label>
                    <select value={formData.seniority} onChange={e => setFormData({ ...formData, seniority: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                      <option value="Senior">Senior</option>
                      <option value="Junior">Junior</option>
                      <option value="N/A">N/A</option>
                    </select>
                  </div>

                  {!['RN', 'TN', 'PN', 'PL', 'NA', 'IT', 'MA', 'SEC', 'ADM'].includes(formData.role_type) && (
                    <div className="col-span-2">
                      <label className="block text-xs font-medium text-slate-400 mb-1">ระบุรหัสตำแหน่งภาษาอังกฤษ (2-5 ตัว เช่น IT, SEC, MA, DR)</label>
                      <input 
                        required 
                        type="text" 
                        placeholder="e.g. IT"
                        value={formData.role_type === 'CUSTOM_TEMP' ? '' : formData.role_type}
                        onChange={e => {
                          const code = e.target.value.toUpperCase().replace(/[^A-Z]/g, '').slice(0, 5);
                          setFormData({
                            ...formData,
                            role_type: code,
                            employee_id: editingStaff ? formData.employee_id : `${code}-${Math.floor(100 + Math.random() * 900)}`
                          });
                        }}
                        className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500" 
                      />
                    </div>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">วอร์ดสังกัด</label>
                  <select value={formData.ward} onChange={e => setFormData({ ...formData, ward: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {wards.length > 0 ? wards.map(w => (
                      <option key={w.id} value={w.ward_name}>{w.ward_name}</option>
                    )) : (
                      <option value="แผนก ER (ฉุกเฉิน)">แผนก ER (ฉุกเฉิน)</option>
                    )}
                  </select>
                </div>
                <div className="flex items-center gap-2 pt-2">
                  <input type="checkbox" id="isActive" checked={formData.is_active} onChange={e => setFormData({ ...formData, is_active: e.target.checked })} className="rounded bg-slate-900 border-slate-700 text-blue-500 focus:ring-blue-500" />
                  <label htmlFor="isActive" className="text-sm font-medium text-slate-300">สถานะปฏิบัติงาน (Active)</label>
                </div>
                <div className="pt-6 flex justify-end gap-3">
                  <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-sm font-medium transition-colors border border-slate-700">ยกเลิก</button>
                  <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-blue-600/20">บันทึกข้อมูล</button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </>
  );
}

function RuleBuilderView() {
  const [rules, setRules] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchRules = () => {
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/rules/')
      .then(res => res.json())
      .then(data => {
        setRules(data);
        setLoading(false);
      })
      .catch(err => console.error(err));
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const handleToggle = async (id: number, currentStatus: boolean) => {
    setRules(prev => prev.map(r => r.id === id ? { ...r, is_active: !currentStatus } : r));
    try {
      await fetch(`' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/rules/${id}/toggle?is_active=${!currentStatus}`, {
        method: 'PUT'
      });
    } catch (error) {
      console.error(error);
      fetchRules(); // Revert on error
    }
  };

  return (
    <div className="h-full flex flex-col gap-6 max-w-5xl mx-auto w-full">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white mb-1">ตั้งค่ากฎครอบจักรวาล (Universal Rules)</h2>
          <p className="text-sm text-slate-400">กำหนดเงื่อนไขและข้อจำกัดต่างๆ เพื่อให้ AI (OR-Tools) คำนวณตารางเวรได้แม่นยำ</p>
        </div>
        <button className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition-colors shadow-lg shadow-brand-600/20">
          <Plus className="h-4 w-4" />
          <span>สร้างกฎใหม่</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 overflow-y-auto pb-4">
        {/* Render Rules */}
        {rules.map((rule) => (
          <div key={rule.id} className="glass-card p-5 border border-slate-700/50 hover:border-brand-500/30 transition-all group relative overflow-hidden flex flex-col h-full">
            {rule.is_active && <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>}
            {!rule.is_active && <div className="absolute top-0 left-0 w-1 h-full bg-slate-600"></div>}

            <div className="flex items-start justify-between mb-4">
              <div className={`p-2 rounded-lg ${rule.is_active ? 'bg-slate-800' : 'bg-slate-800/50'}`}>
                {rule.rule_type === 'global' ? <Shield className="h-5 w-5 text-emerald-400" /> : rule.rule_type === 'unit' ? <Users className="h-5 w-5 text-amber-400" /> : <Settings className="h-5 w-5 text-purple-400" />}
              </div>
              <div className="flex items-center gap-2">
                <span className={`text-xs font-semibold px-2 py-1 rounded-full border ${rule.rule_type === 'global' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                  rule.rule_type === 'unit' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
                    'bg-purple-500/10 text-purple-400 border-purple-500/20'
                  }`}>
                  {rule.rule_type.toUpperCase()}
                </span>
                <div onClick={() => handleToggle(rule.id, rule.is_active)} className={`w-10 h-6 rounded-full p-1 cursor-pointer transition-colors ${rule.is_active ? 'bg-emerald-500' : 'bg-slate-600'}`}>
                  <div className={`w-4 h-4 bg-white rounded-full shadow-sm transition-transform ${rule.is_active ? 'translate-x-4' : 'translate-x-0'}`}></div>
                </div>
              </div>
            </div>

            <h3 className={`font-semibold mb-2 ${rule.is_active ? 'text-white' : 'text-slate-400'}`}>{rule.name}</h3>
            <p className="text-sm text-slate-500 flex-1">{rule.description}</p>

            <div className="mt-4 pt-4 border-t border-slate-700/50 flex justify-end opacity-0 group-hover:opacity-100 transition-opacity">
              <button className="text-xs text-brand-400 hover:text-brand-300 font-medium flex items-center gap-1">
                <Settings className="h-3 w-3" /> แก้ไขเงื่อนไข
              </button>
            </div>
          </div>
        ))}

        {/* Add New Rule Card */}
        <div className="rounded-2xl border-2 border-dashed border-slate-700 hover:border-brand-500/50 hover:bg-brand-500/5 transition-all flex flex-col items-center justify-center text-center p-6 h-full min-h-[220px] cursor-pointer group">
          <div className="w-12 h-12 rounded-full bg-slate-800 group-hover:bg-brand-500/20 flex items-center justify-center mb-3 transition-colors">
            <Plus className="h-6 w-6 text-slate-400 group-hover:text-brand-400 transition-colors" />
          </div>
          <h3 className="font-medium text-slate-300 group-hover:text-white transition-colors">สร้างกฎเฉพาะถิ่น</h3>
          <p className="text-xs text-slate-500 mt-1">เพิ่มข้อจำกัดใหม่สำหรับแผนกของคุณ</p>
        </div>
      </div>
    </div>
  );
}

function WardConfigView() {
  const [configs, setConfigs] = useState<any[]>([]);
  const [selectedWard, setSelectedWard] = useState<string>('');
  const [config, setConfig] = useState<any>(null);
  const [configId, setConfigId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [activeStaffCount, setActiveStaffCount] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  const [isAdding, setIsAdding] = useState(false);
  const [newWardName, setNewWardName] = useState('');
  const [userRole, setUserRole] = useState<string>('');
  const [loading, setLoading] = useState(true);

  const fetchConfigs = () => {
    setLoading(true);
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/ward-config/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(res => res.json())
      .then(data => {
        setConfigs(data);
        if (data.length > 0) {
          if (!selectedWard || !data.find((c: any) => c.ward_name === selectedWard)) {
            setSelectedWard(data[0].ward_name);
            setConfig(data[0].config);
            setConfigId(data[0].id);
          } else {
            const active = data.find((c: any) => c.ward_name === selectedWard);
            setConfig(active.config);
            setConfigId(active.id);
          }
        } else {
          setConfig(null);
          setConfigId(null);
          setSelectedWard('');
        }
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchConfigs();
    const uStr = localStorage.getItem('user');
    if (uStr) {
      try { setUserRole(JSON.parse(uStr).role); } catch (e) { }
    }

    // Fetch active staff count
    // Fetch active staff count for the selected ward
    if (selectedWard) {
      fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
        .then(res => res.json())
        .then(data => setActiveStaffCount(data.filter((s: any) => s.is_active && (s.ward === selectedWard || (!s.ward && selectedWard === 'แผนก ER (ฉุกเฉิน)'))).length))
        .catch(err => console.error(err));
    } else {
      setActiveStaffCount(0);
    }
  }, [selectedWard]);

  const updateShiftValue = (shift: string, field: string, value: number) => {
    setConfig((prev: any) => ({
      ...prev,
      shifts: {
        ...prev.shifts,
        [shift]: { ...prev.shifts[shift], [field]: value }
      }
    }));
    setSaved(false);
  };

  const saveConfig = async () => {
    if (!configId) return;
    setSaving(true);
    try {
      await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/ward-config/${configId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      setSaved(true);
      fetchConfigs();
    } catch (err) {
      console.error(err);
    }
    setSaving(false);
  };

  const handleAddWard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newWardName.trim()) return;
    setIsAdding(true);
    try {
      const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/ward-config/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ward_name: newWardName.trim(), config: null })
      });
      if (res.ok) {
        setNewWardName('');
        const newWard = await res.json();
        setSelectedWard(newWard.ward_name);
        fetchConfigs();
      } else {
        const error = await res.json();
        alert(error.detail || 'เกิดข้อผิดพลาดในการเพิ่มแผนก');
      }
    } catch (err) {
      console.error(err);
    }
    setIsAdding(false);
  };

  const handleDeleteWard = async () => {
    if (!configId) return;
    if (!confirm(`คุณแน่ใจหรือไม่ว่าต้องการลบแผนก "${selectedWard}"? ข้อมูลการตั้งค่าจะถูกลบถาวร`)) return;

    setIsDeleting(true);
    try {
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/ward-config/${configId}`, { method: 'DELETE' });
      if (res.ok) {
        setSelectedWard('');
        fetchConfigs();
      } else {
        alert('เกิดข้อผิดพลาดในการลบแผนก');
      }
    } catch (err) {
      console.error(err);
    }
    setIsDeleting(false);
  };

  if (loading) return <div className="text-slate-400 text-center py-20">กำลังโหลดข้อมูล...</div>;

  // Smart Validator calculations
  const mTotal = config?.shifts?.M?.min_total || 0;
  const eTotal = config?.shifts?.E?.min_total || 0;
  const nTotal = config?.shifts?.N?.min_total || 0;
  const maxShifts = config?.max_shifts_per_week || 5;
  const demandPerDay = mTotal + eTotal + nTotal;
  const demandPerWeek = demandPerDay * 7;
  const capacityPerWeek = activeStaffCount * maxShifts;
  const usagePercent = capacityPerWeek > 0 ? Math.round((demandPerWeek / capacityPerWeek) * 100) : 0;
  const isFeasible = demandPerWeek <= capacityPerWeek;
  const surplus = capacityPerWeek - demandPerWeek;

  const shiftLabels: any = { M: { name: 'เช้า (Morning)', icon: '☀️' }, E: { name: 'บ่าย (Evening)', icon: '🌅' }, N: { name: 'ดึก (Night)', icon: '🌙' } };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-2 mb-8">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center mb-2 shadow-inner border border-white/5">
          <Building2 className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">ตั้งค่าความต้องการบุคลากรประจำวอร์ด</h2>
        <p className="text-slate-400">กำหนดจำนวนพยาบาลขั้นต่ำในแต่ละกะ เพื่อให้ AI จัดตารางตามที่วอร์ดของคุณต้องการ</p>
      </div>

      <div className="bg-slate-800/50 p-4 rounded-xl border border-slate-700 space-y-4">
        <h3 className="font-bold text-white mb-2">จัดการรายชื่อแผนก</h3>
        <div className="flex flex-wrap gap-2">
          {configs.map((c) => (
            <button
              key={c.id}
              onClick={() => setSelectedWard(c.ward_name)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${selectedWard === c.ward_name ? 'bg-brand-600 text-white shadow-lg' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'}`}
            >
              {c.ward_name}
            </button>
          ))}
        </div>

        {userRole === 'admin' && (
          <form onSubmit={handleAddWard} className="flex gap-2">
            <input
              type="text"
              placeholder="ชื่อแผนกใหม่..."
              value={newWardName}
              onChange={(e) => setNewWardName(e.target.value)}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500 max-w-sm"
            />
            <button type="submit" disabled={isAdding || !newWardName.trim()} className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 rounded-lg text-sm text-white font-medium flex items-center gap-2">
              <Plus className="h-4 w-4" /> เพิ่ม
            </button>
          </form>
        )}
      </div>

      {!config ? (
        <div className="text-slate-400 text-center py-20 bg-slate-800/20 rounded-xl border border-dashed border-slate-700">ไม่มีแผนกที่เลือก หรือยังไม่มีข้อมูล กรุณาเพิ่มแผนกใหม่</div>
      ) : (
        <>
          <div className="flex justify-between items-center bg-slate-800/50 p-4 rounded-xl border border-slate-700">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Building2 className="h-5 w-5 text-brand-400" />
              ตั้งค่าของแผนก: <span className="text-brand-400">{selectedWard}</span>
            </h3>
            {userRole === 'admin' && (
              <button onClick={handleDeleteWard} disabled={isDeleting} className="px-4 py-2 bg-red-500/10 text-red-400 hover:bg-red-500/20 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors">
                <Trash2 className="h-4 w-4" /> ลบแผนกนี้
              </button>
            )}
          </div>

          {/* Smart Validator Card */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className={`glass-card p-6 border ${isFeasible ? 'border-emerald-500/30' : 'border-red-500/30'}`}>
            <h3 className="font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-brand-400" />
              📊 สรุปกำลังคน (Smart Validator)
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="bg-slate-900/50 rounded-xl p-3 text-center">
                <div className="text-xs text-slate-400">คน Active</div>
                <div className="text-2xl font-bold text-white">{activeStaffCount}</div>
                <div className="text-xs text-slate-500">คน</div>
              </div>
              <div className="bg-slate-900/50 rounded-xl p-3 text-center">
                <div className="text-xs text-slate-400">กะสูงสุด/คน</div>
                <div className="text-2xl font-bold text-white">{maxShifts}</div>
                <div className="text-xs text-slate-500">กะ/สัปดาห์</div>
              </div>
              <div className="bg-slate-900/50 rounded-xl p-3 text-center">
                <div className="text-xs text-slate-400">กำลังคนรวม</div>
                <div className="text-2xl font-bold text-brand-400">{capacityPerWeek}</div>
                <div className="text-xs text-slate-500">คน-กะ/สัปดาห์</div>
              </div>
              <div className="bg-slate-900/50 rounded-xl p-3 text-center">
                <div className="text-xs text-slate-400">ความต้องการ</div>
                <div className={`text-2xl font-bold ${isFeasible ? 'text-emerald-400' : 'text-red-400'}`}>{demandPerWeek}</div>
                <div className="text-xs text-slate-500">{mTotal}+{eTotal}+{nTotal} × 7 วัน</div>
              </div>
            </div>

            {/* Capacity Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-400">อัตราใช้งานกำลังคน</span>
                <span className={`font-bold ${usagePercent <= 70 ? 'text-emerald-400' : usagePercent <= 90 ? 'text-amber-400' : 'text-red-400'}`}>{usagePercent}%</span>
              </div>
              <div className="h-4 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${Math.min(usagePercent, 100)}%` }}
                  transition={{ duration: 0.5 }}
                  className={`h-full rounded-full ${usagePercent <= 70 ? 'bg-gradient-to-r from-emerald-500 to-emerald-400' : usagePercent <= 90 ? 'bg-gradient-to-r from-amber-500 to-amber-400' : 'bg-gradient-to-r from-red-500 to-red-400'}`}
                />
              </div>
            </div>

            {/* Status Message */}
            <div className={`mt-4 p-3 rounded-lg text-sm flex items-start gap-2 ${isFeasible ? 'bg-emerald-500/10 text-emerald-300' : 'bg-red-500/10 text-red-300'}`}>
              {isFeasible ? (
                <>
                  <Shield className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div>
                    <span className="font-bold">✅ ค่ากำลังคนเพียงพอ!</span>
                    <span className="text-emerald-400/70 ml-1">เหลืออีก {surplus} คน-กะ สำหรับวันลา/ฉุกเฉิน</span>
                  </div>
                </>
              ) : (
                <>
                  <AlertTriangle className="h-5 w-5 mt-0.5 flex-shrink-0" />
                  <div>
                    <div className="font-bold">❌ กำลังคนไม่พอ! ขาดอีก {Math.abs(surplus)} คน-กะ</div>
                    <div className="text-red-400/70 mt-1">
                      💡 แนะนำ: ลดจำนวนคนต่อกะลง หรือเพิ่มกะสูงสุดจาก {maxShifts} → {maxShifts + 1} หรือเพิ่มบุคลากร
                    </div>
                  </div>
                </>
              )}
            </div>
          </motion.div>

          {/* Shift Configuration Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {['M', 'E', 'N'].map(shift => (
              <motion.div key={shift} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 space-y-4">
                <div className="flex items-center gap-3 mb-2">
                  <span className="text-2xl">{shiftLabels[shift].icon}</span>
                  <div>
                    <h3 className="font-bold text-white">{shiftLabels[shift].name}</h3>
                    <p className="text-xs text-slate-400">{config.shifts[shift].label}</p>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">จำนวนรวมขั้นต่ำ (คน)</label>
                    <input
                      type="number" min={0} max={10} disabled={userRole !== 'admin' && userRole !== 'head_nurse'}
                      value={config.shifts[shift].min_total}
                      onChange={(e) => updateShiftValue(shift, 'min_total', parseInt(e.target.value) || 0)}
                      className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-white text-center text-lg font-bold focus:ring-2 focus:ring-brand-500 focus:outline-none disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">RN ขั้นต่ำ (พยาบาลวิชาชีพ)</label>
                    <input
                      type="number" min={0} max={10} disabled={userRole !== 'admin' && userRole !== 'head_nurse'}
                      value={config.shifts[shift].min_rn}
                      onChange={(e) => updateShiftValue(shift, 'min_rn', parseInt(e.target.value) || 0)}
                      className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-white text-center text-lg font-bold focus:ring-2 focus:ring-brand-500 focus:outline-none disabled:opacity-50"
                    />
                  </div>
                  <div>
                    <label className="text-xs text-slate-400 block mb-1">NA ขั้นต่ำ (ผู้ช่วยเหลือ)</label>
                    <input
                      type="number" min={0} max={10} disabled={userRole !== 'admin' && userRole !== 'head_nurse'}
                      value={config.shifts[shift].min_na}
                      onChange={(e) => updateShiftValue(shift, 'min_na', parseInt(e.target.value) || 0)}
                      className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-2 text-white text-center text-lg font-bold focus:ring-2 focus:ring-brand-500 focus:outline-none disabled:opacity-50"
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* General Settings */}
          <div className="glass-card p-6">
            <h3 className="font-bold text-white mb-4 flex items-center gap-2">
              <Settings className="h-5 w-5 text-brand-400" />
              ตั้งค่าทั่วไป
            </h3>
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="text-sm text-slate-400 block mb-2">ทำงานสูงสุด (กะ/สัปดาห์)</label>
                <input
                  type="number" min={1} max={7} disabled={userRole !== 'admin' && userRole !== 'head_nurse'}
                  value={config.max_shifts_per_week}
                  onChange={(e) => { setConfig((p: any) => ({ ...p, max_shifts_per_week: parseInt(e.target.value) || 5 })); setSaved(false); }}
                  className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white text-center text-xl font-bold focus:ring-2 focus:ring-brand-500 focus:outline-none disabled:opacity-50"
                />
              </div>
              <div>
                <label className="text-sm text-slate-400 block mb-2">ทำงานขั้นต่ำ (กะ/สัปดาห์)</label>
                <input
                  type="number" min={0} max={7} disabled={userRole !== 'admin'}
                  value={config.min_shifts_per_week}
                  onChange={(e) => { setConfig((p: any) => ({ ...p, min_shifts_per_week: parseInt(e.target.value) || 1 })); setSaved(false); }}
                  className="w-full bg-slate-800 border border-slate-600 rounded-lg px-4 py-3 text-white text-center text-xl font-bold focus:ring-2 focus:ring-brand-500 focus:outline-none disabled:opacity-50"
                />
              </div>
            </div>
          </div>

          {/* Save Button */}
          {(userRole === 'admin' || userRole === 'head_nurse') && (
            <div className="flex justify-center">
              <button
                onClick={saveConfig}
                disabled={saving || saved}
                className={`px-8 py-3 rounded-xl font-bold text-lg transition-all flex items-center gap-3 shadow-lg ${
                  saved
                    ? 'bg-emerald-600 text-white shadow-emerald-500/20'
                    : 'bg-gradient-to-r from-brand-600 to-brand-500 hover:from-brand-500 hover:to-brand-400 text-white shadow-brand-500/20 hover:shadow-brand-500/40'
                  } disabled:opacity-50`}
              >
                {saving ? <div className="h-5 w-5 rounded-full border-2 border-white/20 border-t-white animate-spin" /> : saved ? <Shield className="h-5 w-5" /> : <Activity className="h-5 w-5" />}
                {saving ? 'กำลังบันทึก...' : saved ? 'บันทึกสำเร็จ ✓' : 'บันทึกค่าตั้งค่าวอร์ด'}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function LeaveView() {
  const [leaves, setLeaves] = useState<any[]>([]);
  const [staff, setStaff] = useState<any[]>([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [formData, setFormData] = useState({ staff_id: 0, staff_name: '', leave_date: '', leave_type: 'ลาป่วย', reason: '' });

  const fetchLeaves = () => fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/leave/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()).then(setLeaves).catch(console.error);

  useEffect(() => {
    fetchLeaves();
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setStaff(data.filter((s: any) => s.is_active));
        else setStaff([]);
      }).catch(console.error);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/leave/', { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` }, body: JSON.stringify(formData) });
    fetchLeaves(); setModalOpen(false);
  };

  const updateStatus = async (id: number, status: string) => {
    await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/leave/${id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${localStorage.getItem('token')}` }, body: JSON.stringify({ status }) });
    fetchLeaves();
  };

  const statusColors: any = { pending: 'bg-amber-500/10 text-amber-400 border-amber-500/30', approved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30', rejected: 'bg-red-500/10 text-red-400 border-red-500/30' };
  const statusLabels: any = { pending: 'รอพิจารณา', approved: 'อนุมัติ', rejected: 'ไม่อนุมัติ' };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2 mb-6">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center mb-2 shadow-inner border border-white/5">
          <Calendar className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">จัดการวันลาบุคลากร</h2>
        <p className="text-slate-400">บันทึกวันลาเพื่อให้ AI ไม่จัดเวรในวันที่ลา</p>
      </div>

      <div className="flex justify-end">
        <button onClick={() => { setFormData({ staff_id: staff[0]?.id || 0, staff_name: staff[0]?.name || '', leave_date: '', leave_type: 'ลาป่วย', reason: '' }); setModalOpen(true); }} className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="h-4 w-4" /> ขอวันลาใหม่
        </button>
      </div>

      {/* Leave List */}
      <div className="space-y-3">
        {leaves.length === 0 && <p className="text-slate-500 text-center py-10">ยังไม่มีรายการวันลา</p>}
        {leaves.map(leave => (
          <motion.div key={leave.id} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="h-10 w-10 rounded-full bg-gradient-to-tr from-brand-600 to-purple-600 flex items-center justify-center font-bold text-white text-xs">{leave.staff_name?.charAt(0) || '?'}</div>
              <div>
                <p className="font-medium text-white">{leave.staff_name}</p>
                <p className="text-sm text-slate-400">{leave.leave_date} • {leave.leave_type} {leave.reason && `• ${leave.reason}`}</p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className={`px-3 py-1 rounded-full text-xs font-medium border ${statusColors[leave.status]}`}>{statusLabels[leave.status]}</span>
              {leave.status === 'pending' && (
                <>
                  <button onClick={() => updateStatus(leave.id, 'approved')} className="p-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 transition-colors"><CheckCircle className="h-4 w-4" /></button>
                  <button onClick={() => updateStatus(leave.id, 'rejected')} className="p-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 transition-colors"><XCircle className="h-4 w-4" /></button>
                </>
              )}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Leave Modal */}
      <AnimatePresence>
        {modalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setModalOpen(false)} />
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="relative w-full max-w-md bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl">
              <div className="px-6 py-4 border-b border-slate-700/50"><h3 className="text-lg font-bold text-white">ขอวันลาใหม่</h3></div>
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">เลือกบุคลากร</label>
                  <select value={formData.staff_id} onChange={e => { const s = staff.find((x: any) => x.id === parseInt(e.target.value)); setFormData({ ...formData, staff_id: parseInt(e.target.value), staff_name: s?.name || '' }); }} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                    {staff.map((s: any) => <option key={s.id} value={s.id}>{s.employee_id} - {s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">วันที่ลา</label>
                  <input required type="date" value={formData.leave_date} onChange={e => setFormData({ ...formData, leave_date: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">ประเภทการลา</label>
                  <select value={formData.leave_type} onChange={e => setFormData({ ...formData, leave_type: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option>ลาป่วย</option><option>ลาพักร้อน</option><option>ลากิจ</option><option>ลาคลอด</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">เหตุผล (ไม่บังคับ)</label>
                  <input type="text" value={formData.reason} onChange={e => setFormData({ ...formData, reason: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-blue-500" placeholder="เช่น ไม่สบาย" />
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white">ยกเลิก</button>
                  <button type="submit" className="px-4 py-2 bg-brand-600 hover:bg-brand-500 rounded-lg text-sm text-white font-medium">ส่งคำขอลา</button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

function ShiftSwapView() {
  const [swaps, setSwaps] = useState<any[]>([]);
  const [currentUser, setCurrentUser] = useState<any>(null);
  const [staff, setStaff] = useState<any[]>([]);
  const [targetStaff, setTargetStaff] = useState<any[]>([]);
  const [targetStaffId, setTargetStaffId] = useState<string>('');
  const [requestDate, setRequestDate] = useState<string>('');
  const [targetDate, setTargetDate] = useState<string>('');
  const [submitting, setSubmitting] = useState(false);
  const [activeSubTab, setActiveSubTab] = useState<'create' | 'incoming' | 'outgoing' | 'head_approval'>('incoming');
  const [headPendingSwaps, setHeadPendingSwaps] = useState<any[]>([]);

  useEffect(() => {
    const uStr = localStorage.getItem('user');
    if (uStr) {
      try {
        const u = JSON.parse(uStr);
        setCurrentUser(u);
        if (u.role === 'head_nurse' || u.role === 'admin') {
          setActiveSubTab('head_approval');
        } else {
          setActiveSubTab('incoming');
        }
      } catch (e) {}
    }
  }, []);

  const fetchSwaps = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const rInc = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/swap/incoming', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dInc = await rInc.json();

      const rOut = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/swap/outgoing', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const dOut = await rOut.json();

      setSwaps([...(Array.isArray(dInc) ? dInc : []), ...(Array.isArray(dOut) ? dOut : [])]);

      const user = JSON.parse(localStorage.getItem('user') || '{}');
      if (user.role === 'head_nurse' || user.role === 'admin') {
        const rHead = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/swap/pending-approval', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const dHead = await rHead.json();
        setHeadPendingSwaps(Array.isArray(dHead) ? dHead : []);
      }
    } catch (err) {
      console.error(err);
    }
  }, []);

  const fetchStaff = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (Array.isArray(data) && currentUser) {
        setStaff(data);
        const filtered = data.filter((s: any) => s.is_active && s.ward === currentUser.ward && s.name !== currentUser.full_name);
        setTargetStaff(filtered);
        if (filtered.length > 0) setTargetStaffId(String(filtered[0].id));
      }
    } catch (err) {
      console.error(err);
    }
  }, [currentUser]);

  useEffect(() => {
    if (currentUser) {
      fetchSwaps();
      fetchStaff();
    }
  }, [currentUser, fetchSwaps, fetchStaff]);

  const handleCreateRequest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!targetStaffId || !requestDate || !targetDate) {
      alert("กรุณากรอกข้อมูลให้ครบถ้วน");
      return;
    }
    setSubmitting(true);
    try {
      const token = localStorage.getItem('token');
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/swap/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          target_user_id: parseInt(targetStaffId),
          request_date: requestDate,
          target_date: targetDate
        })
      });
      const data = await res.json();
      if (res.ok) {
        alert("ส่งคำขอแลกเวรเรียบร้อยแล้ว! รอเพื่อนร่วมงานตอบรับ");
        setRequestDate('');
        setTargetDate('');
        fetchSwaps();
        setActiveSubTab('outgoing');
      } else {
        alert(data.detail || "ไม่สามารถขอแลกเวรได้");
      }
    } catch (err) {
      console.error(err);
      alert("เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์");
    }
    setSubmitting(false);
  };

  const handleRespond = async (swapId: number, accept: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/swap/${swapId}/respond?accept=${accept}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        alert(accept ? "คุณได้ตอบรับคำขอแลกเวรนี้แล้ว รอหัวหน้าพยาบาลอนุมัติ" : "คุณได้ปฏิเสธคำขอแลกเวรแล้ว");
        fetchSwaps();
      } else {
        alert(data.detail || "เกิดข้อผิดพลาด");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleApprove = async (swapId: number, approve: boolean) => {
    try {
      const token = localStorage.getItem('token');
      const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/swap/${swapId}/approve?approve=${approve}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await res.json();
      if (res.ok) {
        alert(approve ? "อนุมัติการแลกเวรสำเร็จ! ระบบได้ทำการสลับเวรในตารางแล้ว" : "ปฏิเสธการอนุมัติสำเร็จ");
        fetchSwaps();
      } else {
        alert(data.detail || "เกิดข้อผิดพลาด");
      }
    } catch (err) {
      console.error(err);
    }
  };

  const incomingSwaps = swaps.filter((s: any) => currentUser && s.target_user.username === currentUser.username);
  const outgoingSwaps = swaps.filter((s: any) => currentUser && s.requester.username === currentUser.username);

  const statusBadge = (status: string) => {
    const badges: any = {
      pending_peer: 'bg-blue-500/10 text-blue-400 border-blue-500/30 (รอเพื่อนร่วมงานตอบรับ)',
      pending_head: 'bg-amber-500/10 text-amber-400 border-amber-500/30 (รอหัวหน้าอนุมัติ)',
      approved: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 (อนุมัติแล้ว)',
      rejected: 'bg-red-500/10 text-red-400 border-red-500/30 (หัวหน้าไม่อนุมัติ)',
      declined: 'bg-gray-500/10 text-gray-400 border-gray-500/30 (เพื่อนปฏิเสธ)'
    };
    return badges[status] || status;
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2 mb-6">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center mb-2 shadow-inner border border-white/5">
          <Activity className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">ระบบขอแลกเวร (Shift Swap Exchange)</h2>
        <p className="text-slate-400">ขอสลับเวรกับเพื่อนร่วมงานในแผนก และรอการอนุมัติจากหัวหน้าพยาบาลแบบเรียลไทม์</p>
      </div>

      <div className="flex border-b border-slate-700">
        {(currentUser?.role === 'head_nurse' || currentUser?.role === 'admin') && (
          <button
            onClick={() => setActiveSubTab('head_approval')}
            className={`px-4 py-2 font-medium text-sm transition-all border-b-2 ${activeSubTab === 'head_approval' ? 'border-brand-500 text-brand-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
          >
            อนุมัติการแลกเวร ({headPendingSwaps.length})
          </button>
        )}
        <button
          onClick={() => setActiveSubTab('incoming')}
          className={`px-4 py-2 font-medium text-sm transition-all border-b-2 ${activeSubTab === 'incoming' ? 'border-brand-500 text-brand-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
        >
          คำขอแลกเวรถึงฉัน ({incomingSwaps.length})
        </button>
        <button
          onClick={() => setActiveSubTab('outgoing')}
          className={`px-4 py-2 font-medium text-sm transition-all border-b-2 ${activeSubTab === 'outgoing' ? 'border-brand-500 text-brand-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
        >
          คำขอของฉัน ({outgoingSwaps.length})
        </button>
        <button
          onClick={() => setActiveSubTab('create')}
          className={`px-4 py-2 font-medium text-sm transition-all border-b-2 ${activeSubTab === 'create' ? 'border-brand-500 text-brand-400' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
        >
          สร้างคำขอใหม่
        </button>
      </div>

      <div className="space-y-4">
        {activeSubTab === 'create' && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6 max-w-md mx-auto">
            <h3 className="text-lg font-bold text-white mb-4">ส่งคำขอแลกเวรใหม่</h3>
            <form onSubmit={handleCreateRequest} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">เพื่อนร่วมงานในแผนก ({currentUser?.ward})</label>
                {targetStaff.length === 0 ? (
                  <p className="text-slate-500 text-sm">ไม่พบเพื่อนพนักงานท่านอื่นในแผนกของคุณ</p>
                ) : (
                  <select
                    value={targetStaffId}
                    onChange={e => setTargetStaffId(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
                  >
                    {targetStaff.map((s: any) => (
                      <option key={s.id} value={s.id}>{s.name} ({s.role_type})</option>
                    ))}
                  </select>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">วันที่ต้องการแลกเวรออก (วันของคุณ)</label>
                <input
                  required
                  type="date"
                  value={requestDate}
                  onChange={e => setRequestDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1">วันที่ต้องการแลกรับแทน (วันของเพื่อน)</label>
                <input
                  required
                  type="date"
                  value={targetDate}
                  onChange={e => setTargetDate(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
                />
              </div>
              <button
                type="submit"
                disabled={submitting || targetStaff.length === 0}
                className="w-full py-2 bg-brand-600 hover:bg-brand-500 rounded-lg text-white font-medium transition-colors disabled:opacity-50"
              >
                {submitting ? "กำลังส่ง..." : "ส่งคำขอ"}
              </button>
            </form>
          </motion.div>
        )}

        {activeSubTab === 'incoming' && (
          <div className="space-y-3">
            {incomingSwaps.length === 0 && <p className="text-slate-500 text-center py-10">ไม่มีคำขอแลกเวรส่งถึงคุณ</p>}
            {incomingSwaps.map((swap: any) => (
              <motion.div key={swap.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-4 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-white">ผู้ส่ง: {swap.requester.full_name}</p>
                  <p className="text-sm text-slate-400">
                    แลกเวรของเขาในวันที่ <span className="text-brand-400 font-medium">{swap.request_date}</span> กับเวรของคุณในวันที่ <span className="text-purple-400 font-medium">{swap.target_date}</span>
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    สถานะ: {statusBadge(swap.status)}
                  </p>
                </div>
                {swap.status === 'pending_peer' && (
                  <div className="flex gap-2">
                    <button onClick={() => handleRespond(swap.id, true)} className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1">
                      <CheckCircle className="h-3.5 w-3.5" /> ยอมรับ
                    </button>
                    <button onClick={() => handleRespond(swap.id, false)} className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs font-semibold flex items-center gap-1">
                      <XCircle className="h-3.5 w-3.5" /> ปฏิเสธ
                    </button>
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        )}

        {activeSubTab === 'outgoing' && (
          <div className="space-y-3">
            {outgoingSwaps.length === 0 && <p className="text-slate-500 text-center py-10">คุณยังไม่เคยส่งคำขอแลกเวร</p>}
            {outgoingSwaps.map((swap: any) => (
              <motion.div key={swap.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-4 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-white">ส่งถึง: {swap.target_user.full_name}</p>
                  <p className="text-sm text-slate-400">
                    แลกเวรของคุณในวันที่ <span className="text-brand-400 font-medium">{swap.request_date}</span> กับเวรของเขาในวันที่ <span className="text-purple-400 font-medium">{swap.target_date}</span>
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    สถานะ: {statusBadge(swap.status)}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}

        {activeSubTab === 'head_approval' && (
          <div className="space-y-3">
            {headPendingSwaps.length === 0 && <p className="text-slate-500 text-center py-10">ไม่มีคำขอสลับเวรที่รอการอนุมัติ</p>}
            {headPendingSwaps.map((swap: any) => (
              <motion.div key={swap.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card p-4 flex items-center justify-between">
                <div>
                  <p className="font-semibold text-white">ผู้ร้องขอสลับเวร: {swap.requester.full_name} 🔁 {swap.target_user.full_name}</p>
                  <p className="text-sm text-slate-400">
                    - เวรของ {swap.requester.full_name} วันที่ <span className="text-brand-400 font-medium">{swap.request_date}</span>
                    <br />
                    - เวรของ {swap.target_user.full_name} วันที่ <span className="text-purple-400 font-medium">{swap.target_date}</span>
                  </p>
                  <p className="text-xs text-slate-500 mt-1">
                    แผนก: {swap.requester.ward} (ทั้งสองยอมรับแล้ว รอการตัดสินใจของหัวหน้า)
                  </p>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleApprove(swap.id, true)} className="px-3 py-1.5 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-xs font-semibold flex items-center gap-1">
                    <CheckCircle className="h-3.5 w-3.5" /> อนุมัติการสลับ
                  </button>
                  <button onClick={() => handleApprove(swap.id, false)} className="px-3 py-1.5 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg text-xs font-semibold flex items-center gap-1">
                    <XCircle className="h-3.5 w-3.5" /> ปฏิเสธ
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function DashboardView() {
  const [staff, setStaff] = useState<any[]>([]);
  const [leaves, setLeaves] = useState<any[]>([]);
  const [history, setHistory] = useState<any[]>([]);
  const [wardConfig, setWardConfig] = useState<any>(null);

  useEffect(() => {
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/staff/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()).then(data => { if (Array.isArray(data)) setStaff(data); }).catch(console.error);
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/leave/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()).then(data => { if (Array.isArray(data)) setLeaves(data); }).catch(console.error);
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/schedule/history', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()).then(data => { if (Array.isArray(data)) setHistory(data); }).catch(console.error);
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/ward-config/', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } }).then(r => r.json()).then(d => { if (Array.isArray(d) && d.length > 0) setWardConfig(d[0].config); }).catch(console.error);
  }, []);

  const activeStaff = staff.filter(s => s.is_active).length;
  const totalStaff = staff.length;
  const pendingLeaves = leaves.filter(l => l.status === 'pending').length;
  const rnCount = staff.filter(s => s.is_active && s.role_type === 'RN').length;
  const naCount = staff.filter(s => s.is_active && (s.role_type === 'NA' || s.role_type === 'PN')).length;
  const latestFairness = history.length > 0 ? history[0]?.fairness_score : '-';

  const statCards = [
    { label: 'บุคลากร Active', value: activeStaff, sub: `จากทั้งหมด ${totalStaff} คน`, icon: '👩‍⚕️', color: 'from-brand-600 to-brand-400' },
    { label: 'พยาบาลวิชาชีพ (RN)', value: rnCount, sub: 'คน', icon: '🏥', color: 'from-emerald-600 to-emerald-400' },
    { label: 'ผู้ช่วย (NA/PN)', value: naCount, sub: 'คน', icon: '🤝', color: 'from-purple-600 to-purple-400' },
    { label: 'วันลารอพิจารณา', value: pendingLeaves, sub: 'รายการ', icon: '📋', color: 'from-amber-600 to-amber-400' },
    { label: 'Fairness Score ล่าสุด', value: latestFairness, sub: 'คะแนน', icon: '⚖️', color: 'from-cyan-600 to-cyan-400' },
    { label: 'ตารางที่เคยสร้าง', value: history.length, sub: 'ครั้ง', icon: '📊', color: 'from-pink-600 to-pink-400' },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      <div className="text-center space-y-2 mb-6">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center mb-2 shadow-inner border border-white/5">
          <BarChart3 className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">แดชบอร์ดสถิติ</h2>
        <p className="text-slate-400">ภาพรวมบุคลากร วันลา และประวัติตารางเวร</p>
      </div>

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {statCards.map((card, i) => (
          <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.05 }} className="glass-card p-5 relative overflow-hidden group">
            <div className={`absolute top-0 right-0 w-20 h-20 bg-gradient-to-br ${card.color} opacity-10 rounded-bl-full group-hover:opacity-20 transition-opacity`} />
            <span className="text-2xl">{card.icon}</span>
            <div className="mt-2">
              <div className="text-3xl font-bold text-white">{card.value}</div>
              <div className="text-xs text-slate-400">{card.sub}</div>
              <div className="text-sm text-slate-300 mt-1 font-medium">{card.label}</div>
            </div>
          </motion.div>
        ))}
      </div>

      {/* Role Distribution Bar */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-white mb-4 flex items-center gap-2"><Users className="h-5 w-5 text-brand-400" /> สัดส่วนบุคลากร (Active)</h3>
        <div className="flex h-8 rounded-full overflow-hidden bg-slate-800">
          {rnCount > 0 && <div style={{ width: `${(rnCount / activeStaff) * 100}%` }} className="bg-gradient-to-r from-brand-600 to-brand-400 flex items-center justify-center text-xs font-bold text-white">RN {rnCount}</div>}
          {naCount > 0 && <div style={{ width: `${(naCount / activeStaff) * 100}%` }} className="bg-gradient-to-r from-purple-600 to-purple-400 flex items-center justify-center text-xs font-bold text-white">NA/PN {naCount}</div>}
        </div>
      </div>

      {/* Schedule History */}
      <div className="glass-card p-6">
        <h3 className="font-bold text-white mb-4 flex items-center gap-2"><Clock className="h-5 w-5 text-brand-400" /> ประวัติตารางเวร</h3>
        {history.length === 0 ? (
          <p className="text-slate-500 text-center py-6">ยังไม่เคยสร้างตารางเวร</p>
        ) : (
          <div className="space-y-2">
            {history.slice(0, 5).map((h: any, i: number) => (
              <div key={i} className="flex items-center justify-between py-2 px-3 bg-slate-900/50 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded-lg bg-brand-600/20 flex items-center justify-center text-brand-400 text-sm font-bold">#{h.id}</div>
                  <div>
                    <span className="text-white text-sm font-medium">{h.period} • {h.department}</span>
                    <span className="text-slate-500 text-xs ml-2">{new Date(h.created_at).toLocaleDateString('th-TH')}</span>
                  </div>
                </div>
                <span className="text-brand-400 font-bold text-sm">Fairness: {h.fairness_score ?? '-'}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
function UserManagementView() {
  const [users, setUsers] = useState<any[]>([]);
  const [wards, setWards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editUser, setEditUser] = useState<any>(null);
  const [formData, setFormData] = useState({ username: '', password: '', full_name: '', role: 'nurse', ward: 'แผนก ER (ฉุกเฉิน)' });

  const getHeaders = () => {
    const token = localStorage.getItem('token');
    return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` };
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const uRes = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/users/?t=' + new Date().getTime(), { headers: getHeaders(), cache: 'no-store' });
      if (uRes.status === 401 || uRes.status === 403) {
        alert('เซสชันการยืนยันตัวตนหมดอายุ หรือไม่มีสิทธิ์เข้าถึงหน้านี้ กรุณาเข้าสู่ระบบใหม่');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
        return;
      }
      if (uRes.ok) {
        setUsers(await uRes.json());
      }

      const wRes = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/ward-config/?t=' + new Date().getTime(), { headers: getHeaders(), cache: 'no-store' });
      if (wRes.ok) {
        setWards(await wRes.json());
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  const openAdd = () => {
    setEditUser(null);
    setFormData({ username: '', password: '', full_name: '', role: 'nurse', ward: wards.length > 0 ? wards[0].ward_name : 'แผนก ER (ฉุกเฉิน)' });
    setModalOpen(true);
  };

  const openEdit = (u: any) => {
    setEditUser(u);
    setFormData({ username: u.username, password: '', full_name: u.full_name, role: u.role, ward: u.ward });
    setModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Validate password length for new user
    if (!editUser && formData.password.length < 8) {
      alert('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร');
      return;
    }
    setSaving(true);
    try {
      if (editUser) {
        const body: any = { full_name: formData.full_name, role: formData.role, ward: formData.ward };
        if (formData.password) body.password = formData.password;
        const res = await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/users/${editUser.id}`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify(body) });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          alert('ไม่สามารถแก้ไขข้อมูลผู้ใช้ได้: ' + (errData.detail || 'ข้อผิดพลาดบางอย่าง'));
        }
      } else {
        const res = await fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/users/', { method: 'POST', headers: getHeaders(), body: JSON.stringify(formData) });
        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          alert('ไม่สามารถเพิ่มผู้ใช้ใหม่ได้: ' + (errData.detail || 'ข้อผิดพลาดบางอย่าง'));
        }
      }
    } catch (e) {
      console.error(e);
      alert('เกิดข้อผิดพลาดในการเชื่อมต่อเซิร์ฟเวอร์');
    }
    await fetchData();
    setSaving(false);
    setModalOpen(false);
    // Reset form to blank state after saving
    setFormData({ username: '', password: '', full_name: '', role: 'nurse', ward: wards.length > 0 ? wards[0].ward_name : 'แผนก ER (ฉุกเฉิน)' });
    setEditUser(null);
  };

  const toggleActive = async (u: any) => {
    await fetch((process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + `/api/users/${u.id}`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify({ is_active: !u.is_active }) });
    fetchData();
  };

  const roleConfig: any = {
    admin: { label: 'Admin', color: 'bg-red-500/10 text-red-400 border-red-500/30' },
    head_nurse: { label: 'Head Nurse', color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30' },
    nurse: { label: 'Nurse', color: 'bg-blue-500/10 text-blue-400 border-blue-500/30' },
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2 mb-6">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center mb-2 shadow-inner border border-white/5">
          <UserCog className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">จัดการผู้ใช้งานระบบ</h2>
        <p className="text-slate-400">เพิ่ม/แก้ไขผู้ใช้และกำหนดสิทธิ์การเข้าถึง</p>
      </div>

      <div className="flex justify-end">
        <button onClick={openAdd} className="flex items-center gap-2 px-4 py-2 bg-brand-600 hover:bg-brand-500 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="h-4 w-4" /> เพิ่มผู้ใช้ใหม่
        </button>
      </div>

      <div className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50">
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">ชื่อ / Username</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">Role</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">วอร์ด</th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">สถานะ</th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">จัดการ</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/30">
            {users.map((u, i) => (
              <motion.tr key={u.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.04 }} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="h-9 w-9 rounded-full bg-gradient-to-tr from-brand-600 to-purple-600 flex items-center justify-center font-bold text-white text-sm">
                      {u.full_name?.charAt(0) || u.username?.charAt(0)?.toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-white">{u.full_name || '-'}</p>
                      <p className="text-xs text-slate-400 font-mono">@{u.username}</p>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${roleConfig[u.role]?.color || 'bg-slate-700 text-slate-300 border-slate-600'}`}>
                    {roleConfig[u.role]?.label || u.role}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-slate-300">{u.ward?.replace('แผนก ', '') || '-'}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${u.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-slate-700 text-slate-400'}`}>
                    {u.is_active ? '● Active' : '○ Inactive'}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <button onClick={() => openEdit(u)} className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"><Edit className="h-4 w-4" /></button>
                    {u.username !== 'admin' && (
                      <button onClick={() => toggleActive(u)} className={`p-1.5 rounded-lg transition-colors ${u.is_active ? 'text-red-400 hover:bg-red-500/10' : 'text-emerald-400 hover:bg-emerald-500/10'}`}>
                        {u.is_active ? <XCircle className="h-4 w-4" /> : <CheckCircle className="h-4 w-4" />}
                      </button>
                    )}
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
        {users.length === 0 && <p className="text-slate-500 text-center py-10">ไม่พบข้อมูล</p>}
      </div>

      <AnimatePresence>
        {modalOpen && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setModalOpen(false)} />
            <motion.div key={editUser?.id ?? 'new'} initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="relative w-full max-w-md bg-slate-800 rounded-2xl border border-slate-700 shadow-2xl">
              <div className="px-6 py-4 border-b border-slate-700/50">
                <h3 className="text-lg font-bold text-white">{editUser ? 'แก้ไขผู้ใช้' : 'เพิ่มผู้ใช้ใหม่'}</h3>
              </div>
              <form onSubmit={handleSubmit} autoComplete="off" className="p-6 space-y-4">
                {!editUser && (
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-1">Username</label>
                    <input required autoComplete="username" value={formData.username} onChange={e => setFormData({ ...formData, username: e.target.value })} placeholder="เช่น nurse02" className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                  </div>
                )}
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">ชื่อ-นามสกุล</label>
                  <input value={formData.full_name} onChange={e => setFormData({ ...formData, full_name: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">{editUser ? 'รหัสผ่านใหม่ (เว้นว่างถ้าไม่เปลี่ยน)' : 'รหัสผ่าน'}</label>
                  <input type="password" autoComplete="new-password" required={!editUser} value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })} placeholder={editUser ? '(เว้นว่างถ้าไม่ต้องการเปลี่ยน)' : 'กรอกรหัสผ่านอย่างน้อย 8 ตัว'} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white placeholder:text-slate-600 focus:outline-none focus:ring-2 focus:ring-brand-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">Role</label>
                  <select value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500">
                    <option value="admin">Admin (ผู้ดูแลระบบ)</option>
                    <option value="head_nurse">Head Nurse (หัวหน้าพยาบาล)</option>
                    <option value="nurse">Nurse (พยาบาล)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1">วอร์ด</label>
                  <select value={formData.ward || ''} onChange={e => setFormData({ ...formData, ward: e.target.value })} className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-brand-500">
                    <option value="" disabled>--- เลือกแผนก ---</option>
                    {wards.length > 0 ? wards.map((w: any) => (
                      <option key={w.id} value={w.ward_name}>{w.ward_name}</option>
                    )) : (
                      <option value="แผนก ER (ฉุกเฉิน)">แผนก ER (ฉุกเฉิน)</option>
                    )}
                  </select>
                </div>
                <div className="flex justify-end gap-3 pt-2">
                  <button type="button" onClick={() => setModalOpen(false)} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-white">ยกเลิก</button>
                  <button type="submit" disabled={saving} className="px-4 py-2 bg-brand-600 hover:bg-brand-500 rounded-lg text-sm text-white font-medium disabled:opacity-50">
                    {saving ? 'กำลังบันทึก...' : editUser ? 'บันทึก' : 'เพิ่มผู้ใช้'}
                  </button>
                </div>
              </form>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
// CalendarView component - appended to page.tsx via PowerShell

function CalendarView() {
  const [schedule, setSchedule] = useState<any>(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('' + (process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000') + '/api/schedule/history', { headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
      .then(r => r.ok ? r.json() : [])
      .then(data => {
        if (data.length > 0) setSchedule(data[data.length - 1]);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const shiftColors: any = {
    M: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    E: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    N: 'bg-purple-500/20 text-purple-300 border-purple-500/30',
    OFF: 'bg-slate-700/30 text-slate-500',
  };
  const shiftLabels: any = { M: 'เช้า', E: 'บ่าย', N: 'ดึก', OFF: 'หยุด' };

  const daysOfWeek = ['จ.', 'อ.', 'พ.', 'พฤ.', 'ศ.', 'ส.', 'อา.'];

  const firstDay = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1);
  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
  const startOffset = (firstDay.getDay() + 6) % 7; // Monday-based

  const prevMonth = () => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  const nextMonth = () => setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));

  // Map day number to schedule (week view from latest history)
  const dayShifts: any = {};
  if (schedule?.schedule_data) {
    const data = schedule.schedule_data;
    if (Array.isArray(data)) {
      data.forEach((row: any) => {
        if (row.shifts) {
          row.shifts.forEach((shift: string, idx: number) => {
            const day = idx + 1;
            if (!dayShifts[day]) dayShifts[day] = [];
            if (shift !== 'OFF') dayShifts[day].push({ nurse: row.nurse, shift });
          });
        }
      });
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="text-center space-y-2 mb-4">
        <div className="inline-flex w-16 h-16 rounded-2xl bg-gradient-to-tr from-brand-600/20 to-purple-600/20 items-center justify-center border border-white/5">
          <CalendarDays className="h-8 w-8 text-brand-400" />
        </div>
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">ปฏิทินตารางเวร</h2>
        <p className="text-slate-400 text-sm">แสดงตารางเวรจากข้อมูลล่าสุดในระบบ</p>
      </div>

      {/* Month nav */}
      <div className="glass-card p-4 flex items-center justify-between">
        <button onClick={prevMonth} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
          <ChevronLeft className="h-5 w-5" />
        </button>
        <h3 className="text-lg font-bold text-white">
          {currentMonth.toLocaleString('th-TH', { month: 'long', year: 'numeric' })}
        </h3>
        <button onClick={nextMonth} className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-700 transition-colors">
          <ChevronRight className="h-5 w-5" />
        </button>
      </div>

      {/* Calendar grid */}
      <div className="glass-card p-4">
        {/* Day headers */}
        <div className="grid grid-cols-7 gap-1 mb-2">
          {daysOfWeek.map(d => (
            <div key={d} className="text-center text-xs font-semibold text-slate-400 py-2">{d}</div>
          ))}
        </div>
        {/* Day cells */}
        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: startOffset }).map((_, i) => <div key={`empty-${i}`} />)}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const dayOfWeek = (startOffset + i) % 7; // 0=Mon..6=Sun
            const shifts = dayShifts[dayOfWeek + 1] || [];
            const isToday = new Date().getDate() === day &&
              new Date().getMonth() === currentMonth.getMonth() &&
              new Date().getFullYear() === currentMonth.getFullYear();
            return (
              <div key={day} className={`min-h-[80px] rounded-xl p-2 border ${isToday ? 'border-brand-500/60 bg-brand-500/10' : 'border-slate-700/30 bg-slate-800/30'} flex flex-col gap-1`}>
                <span className={`text-xs font-bold ${isToday ? 'text-brand-400' : 'text-slate-400'}`}>{day}</span>
                {shifts.slice(0, 3).map((s: any, si: number) => (
                  <div key={si} className={`px-1.5 py-0.5 rounded text-[9px] border truncate ${shiftColors[s.shift] || ''}`}>
                    {s.nurse?.split(' ').slice(-1)[0]} {shiftLabels[s.shift] || s.shift}
                  </div>
                ))}
                {shifts.length > 3 && <span className="text-[9px] text-slate-500">+{shifts.length - 3}</span>}
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-4 flex-wrap">
        {Object.entries(shiftLabels).filter(([k]) => k !== 'OFF').map(([k, v]) => (
          <div key={k} className="flex items-center gap-1.5">
            <div className={`h-3 w-3 rounded-full border ${shiftColors[k]?.split(' ').slice(0, 1).join('')}`} />
            <span className="text-xs text-slate-400">{v as string}</span>
          </div>
        ))}
        <div className="flex items-center gap-1.5">
          <div className="h-3 w-3 rounded-full border-2 border-brand-500 bg-brand-500/20" />
          <span className="text-xs text-slate-400">วันนี้</span>
        </div>
      </div>

      {loading && <p className="text-slate-500 text-center py-8">กำลังโหลดข้อมูล...</p>}
      {!loading && !schedule && (
        <div className="text-center py-12 space-y-3">
          <CalendarDays className="h-12 w-12 text-slate-600 mx-auto" />
          <p className="text-slate-500">ยังไม่มีตารางเวรในระบบ กรุณาสร้างตารางก่อน</p>
        </div>
      )}
    </div>
  );
}
