import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FilePlus, 
  ScanLine, 
  KeyRound, 
  BarChart3, 
  Settings,
  LogOut,
  ShieldCheck,
  Lock,
  Loader2
} from 'lucide-react';
import axios from 'axios';

import Dashboard from './pages/Dashboard';
import Generator from './pages/Generator';
import Scanner from './pages/Scanner';
import AnswerKeys from './pages/AnswerKeys';
import Results from './pages/Results';

const SidebarItem = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link 
      to={to} 
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        isActive 
          ? 'bg-primary text-white' 
          : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </Link>
  );
};

const LicenseGuard = ({ children }) => {
    const [status, setStatus] = useState({ loading: true, active: false, expires_at: null });
    const [masterPass, setMasterPass] = useState('');
    const [days, setDays] = useState(30);
    const [genKey, setGenKey] = useState('');

    useEffect(() => {
        checkLicense();
    }, []);

    const checkLicense = async () => {
        try {
            const res = await axios.get('/api/license/status');
            setStatus({ loading: false, active: res.data.active, expires_at: res.data.expires_at });
        } catch (e) {
            setStatus({ loading: false, active: false });
        }
    };

    const handleGenerate = async () => {
        try {
            const res = await axios.post('/api/license/generate', { admin_pass: masterPass, days: parseInt(days) });
            setGenKey(res.data.key);
            alert("¡Licencia activada con éxito! Recarga la página.");
            window.location.reload();
        } catch (e) {
            alert("Contraseña maestra incorrecta.");
        }
    };

    if (status.loading) return <div className="h-screen flex items-center justify-center"><Loader2 className="animate-spin text-primary" size={48} /></div>;

    if (!status.active) {
        return (
            <div className="min-h-screen bg-gray-900 flex items-center justify-center p-6">
                <div className="max-w-md w-full bg-white rounded-3xl p-10 shadow-2xl text-center">
                    <div className="w-20 h-20 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
                        <Lock size={40} />
                    </div>
                    <h1 className="text-2xl font-black text-gray-900 mb-2">Acceso Restringido</h1>
                    <p className="text-gray-500 mb-8">El sistema EinScan Pro requiere una licencia activa para el Colegio Albert Einstein.</p>
                    
                    <div className="space-y-4 text-left">
                        <div>
                            <label className="text-xs font-bold text-gray-400 uppercase">Panel de Administración</label>
                            <input 
                                type="password" 
                                placeholder="Contraseña Maestra"
                                value={masterPass}
                                onChange={e => setMasterPass(e.target.value)}
                                className="w-full mt-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none focus:ring-2 focus:ring-primary"
                            />
                        </div>
                        <div>
                            <label className="text-xs font-bold text-gray-400 uppercase">Días de Acceso</label>
                            <select 
                                value={days} 
                                onChange={e => setDays(e.target.value)}
                                className="w-full mt-1 px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl outline-none"
                            >
                                <option value={1}>1 Día (Prueba)</option>
                                <option value={30}>30 Días (1 Mes)</option>
                                <option value={365}>365 Días (1 Año)</option>
                            </select>
                        </div>
                        <button 
                            onClick={handleGenerate}
                            className="w-full bg-primary text-white py-4 rounded-xl font-bold hover:bg-primary-dark transition-all"
                        >
                            ACTIVAR SISTEMA
                        </button>
                    </div>
                    <p className="mt-8 text-[10px] text-gray-400 uppercase tracking-widest font-bold">Powered by sentinel-byte</p>
                </div>
            </div>
        );
    }

    return (
        <div className="flex min-h-screen bg-gray-50">
            <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold text-primary flex items-center gap-2">
                        EinScan <span className="text-gray-900">Pro</span>
                    </h1>
                    <p className="text-xs text-gray-500 mt-1 uppercase tracking-wider font-semibold">
                        Colegio Albert Einstein
                    </p>
                </div>
                <nav className="flex-1 px-4 space-y-2">
                    <SidebarItem to="/" icon={LayoutDashboard} label="Panel Principal" />
                    <SidebarItem to="/generator" icon={FilePlus} label="1. Crear Examen y Ficha" />
                    <SidebarItem to="/answers" icon={KeyRound} label="2. Configurar Claves" />
                    <SidebarItem to="/scanner" icon={ScanLine} label="3. Escanear Hojas" />
                    <SidebarItem to="/results" icon={BarChart3} label="4. Ver Resultados" />
                </nav>
                <div className="p-4 border-t border-gray-100">
                    <div className="bg-green-50 p-3 rounded-xl mb-4 border border-green-100">
                        <p className="text-[10px] font-black text-green-700 uppercase mb-1">Licencia Activa</p>
                        <p className="text-xs text-green-600 font-medium">Expira: {new Date(status.expires_at).toLocaleDateString()}</p>
                    </div>
                    <button className="flex items-center gap-3 px-4 py-3 w-full text-gray-600 hover:bg-red-50 hover:text-red-600 rounded-lg transition-colors">
                        <LogOut size={20} />
                        <span className="font-medium">Cerrar Sesión</span>
                    </button>
                </div>
            </aside>
            <main className="flex-1 overflow-auto">
                <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
                    <h2 className="text-lg font-semibold text-gray-800">Sistema de Calificación OMR</h2>
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <p className="text-sm font-medium text-gray-900">Admin Einstein</p>
                            <p className="text-xs text-gray-500">Docente Autorizado</p>
                        </div>
                        <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">AE</div>
                    </div>
                </header>
                <div className="p-0">{children}</div>
            </main>
        </div>
    );
};

export default function App() {
  return (
    <BrowserRouter>
      <LicenseGuard>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/generator" element={<Generator />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/answers" element={<AnswerKeys />} />
          <Route path="/results" element={<Results />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </LicenseGuard>
    </BrowserRouter>
  );
}
