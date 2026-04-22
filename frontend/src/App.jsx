import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation, Navigate, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FilePlus, 
  ScanLine, 
  KeyRound, 
  BarChart3, 
  LogOut,
  Lock,
  Loader2,
  ShieldCheck,
  Plus,
  Trash2,
  Settings
} from 'lucide-react';
import axios from 'axios';

import Dashboard from './pages/Dashboard';
import Generator from './pages/Generator';
import Scanner from './pages/Scanner';
import AnswerKeys from './pages/AnswerKeys';
import Results from './pages/Results';

// Interceptor para añadir la licencia a todas las peticiones
axios.interceptors.request.use(config => {
  const key = localStorage.getItem('einscan_key');
  if (key) {
    config.headers['X-License-Key'] = key;
  }
  return config;
});

const SidebarItem = ({ to, icon: Icon, label }) => {
  const location = useLocation();
  const isActive = location.pathname === to;
  
  return (
    <Link 
      to={to} 
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        isActive 
          ? 'bg-primary text-white shadow-lg shadow-red-200' 
          : 'text-gray-600 hover:bg-gray-100'
      }`}
    >
      <Icon size={20} />
      <span className="font-medium">{label}</span>
    </Link>
  );
};

const KeyEntry = () => {
    const [key, setKey] = useState('');
    const [loading, setLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await axios.post('/api/license/validate', { key });
            localStorage.setItem('einscan_key', key);
            window.location.reload();
        } catch (err) {
            alert("Clave inválida o expirada.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 flex items-center justify-center p-6 font-sans">
            <div className="max-w-md w-full bg-white rounded-[2.5rem] p-12 shadow-2xl text-center">
                <div className="w-24 h-24 bg-red-50 text-primary rounded-3xl flex items-center justify-center mx-auto mb-8 rotate-3">
                    <ShieldCheck size={48} />
                </div>
                <h1 className="text-3xl font-black text-gray-900 mb-2">EinScan <span className="text-primary">Pro</span></h1>
                <p className="text-gray-400 font-medium mb-10">Ingresa tu clave de acceso para continuar.</p>
                
                <form onSubmit={handleLogin} className="space-y-6">
                    <input 
                        type="text" 
                        placeholder="EINSTEIN-XXXX-XXXX"
                        value={key}
                        onChange={e => setKey(e.target.value.toUpperCase())}
                        required
                        className="w-full px-6 py-4 bg-gray-50 border-2 border-gray-100 rounded-2xl outline-none focus:border-primary transition-all text-center font-mono text-lg"
                    />
                    <button 
                        type="submit"
                        disabled={loading}
                        className="w-full bg-primary text-white py-4 rounded-2xl font-black text-lg hover:bg-primary-dark transition-all shadow-xl shadow-red-200 disabled:opacity-50"
                    >
                        {loading ? <Loader2 className="animate-spin mx-auto" /> : 'DESBLOQUEAR SISTEMA'}
                    </button>
                </form>
                
                <Link to="/admin-login" className="mt-8 block text-xs font-bold text-gray-300 hover:text-gray-500 uppercase tracking-widest">
                    Acceso Administrador
                </Link>
            </div>
        </div>
    );
};

const AdminPanel = () => {
    const [pass, setPass] = useState('');
    const [isAuth, setIsAuth] = useState(false);
    const [licenses, setLicenses] = useState([]);
    const [days, setDays] = useState(30);

    const handleAuth = (e) => {
        e.preventDefault();
        loadLicenses();
    };

    const loadLicenses = async () => {
        try {
            const res = await axios.get(`/api/license/list?admin_pass=${pass}`);
            setLicenses(res.data);
            setIsAuth(true);
        } catch (e) {
            alert("Contraseña Maestra incorrecta.");
        }
    };

    const handleGenerate = async () => {
        try {
            const res = await axios.post('/api/license/generate', { admin_pass: pass, days: parseInt(days) });
            alert(`¡Clave Generada!: ${res.data.key}`);
            loadLicenses();
        } catch (e) {
            alert("Error al generar.");
        }
    };

    if (!isAuth) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center p-6">
                <div className="max-w-md w-full bg-white rounded-3xl p-10 shadow-xl border border-gray-100">
                    <h2 className="text-xl font-black text-gray-900 mb-6 uppercase">Panel de Control Admin</h2>
                    <form onSubmit={handleAuth} className="space-y-4">
                        <input 
                            type="password" 
                            placeholder="Contraseña Maestra"
                            value={pass}
                            onChange={e => setPass(e.target.value)}
                            className="w-full px-4 py-3 bg-gray-50 rounded-xl outline-none border border-gray-200"
                        />
                        <button className="w-full bg-gray-900 text-white py-3 rounded-xl font-bold">ENTRAR AL PANEL</button>
                        <Link to="/" className="block text-center text-sm text-gray-400">Volver al inicio</Link>
                    </form>
                </div>
            </div>
        );
    }

    return (
        <div className="p-10 max-w-5xl mx-auto">
            <div className="flex justify-between items-center mb-10">
                <h1 className="text-3xl font-black text-gray-900">GESTIÓN DE LICENCIAS</h1>
                <Link to="/" className="text-primary font-bold">Cerrar Panel</Link>
            </div>

            <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm mb-10">
                <h3 className="font-bold text-gray-800 mb-4">Generar Nueva Clave</h3>
                <div className="flex gap-4">
                    <select value={days} onChange={e => setDays(e.target.value)} className="px-4 py-2 bg-gray-50 rounded-xl border">
                        <option value={1}>1 Día</option>
                        <option value={30}>30 Días</option>
                        <option value={365}>1 Año</option>
                    </select>
                    <button onClick={handleGenerate} className="bg-primary text-white px-8 py-2 rounded-xl font-bold flex items-center gap-2">
                        <Plus size={20} /> CREAR CLAVE
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-3xl border border-gray-100 overflow-hidden shadow-sm">
                <table className="w-full text-left">
                    <thead className="bg-gray-50 font-bold text-xs text-gray-400 uppercase tracking-widest">
                        <tr>
                            <th className="p-6">Clave</th>
                            <th className="p-6">Expira</th>
                            <th className="p-6">Estado</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50 font-medium">
                        {licenses.map((lic, i) => (
                            <tr key={i}>
                                <td className="p-6 font-mono font-bold text-primary">{lic.key}</td>
                                <td className="p-6">{new Date(lic.expires_at).toLocaleDateString()}</td>
                                <td className="p-6">
                                    <span className={`px-3 py-1 rounded-full text-[10px] font-black ${new Date(lic.expires_at) > new Date() ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                                        {new Date(lic.expires_at) > new Date() ? 'ACTIVA' : 'EXPIRADA'}
                                    </span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

const MainLayout = ({ children }) => {
    const navigate = useNavigate();
    const [exp, setExp] = useState(null);

    useEffect(() => {
        axios.post('/api/license/validate', { key: localStorage.getItem('einscan_key') })
            .then(res => setExp(res.data.expires_at))
            .catch(() => {
                localStorage.removeItem('einscan_key');
                window.location.reload();
            });
    }, []);

    const handleLogout = () => {
        localStorage.removeItem('einscan_key');
        window.location.href = '/';
    };

    return (
        <div className="flex min-h-screen bg-gray-50 font-sans">
            <aside className="w-72 bg-white border-r border-gray-200 flex flex-col sticky top-0 h-screen">
                <div className="p-8">
                    <h1 className="text-2xl font-black text-gray-900 tracking-tight flex items-center gap-2">
                        EinScan <span className="text-primary">Pro</span>
                    </h1>
                    <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-widest font-black">
                        Colegio Albert Einstein
                    </p>
                </div>
                
                <nav className="flex-1 px-6 space-y-2">
                    <SidebarItem to="/" icon={LayoutDashboard} label="Panel Principal" />
                    <SidebarItem to="/generator" icon={FilePlus} label="1. Crear Examen" />
                    <SidebarItem to="/answers" icon={KeyRound} label="2. Poner Claves" />
                    <SidebarItem to="/scanner" icon={ScanLine} label="3. Escanear Hojas" />
                    <SidebarItem to="/results" icon={BarChart3} label="4. Ver Resultados" />
                </nav>
                
                <div className="p-6 border-t border-gray-50">
                    <div className="bg-gray-950 p-5 rounded-[1.5rem] mb-4 text-white">
                        <p className="text-[9px] font-black text-gray-500 uppercase tracking-widest mb-1">Licencia Activa</p>
                        <p className="text-xs font-bold">Expira: {exp ? new Date(exp).toLocaleDateString() : '...'}</p>
                    </div>
                    <button 
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-6 py-4 w-full text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-2xl transition-all font-bold"
                    >
                        <LogOut size={20} />
                        <span>Cerrar Sesión</span>
                    </button>
                </div>
            </aside>

            <main className="flex-1 overflow-auto">
                <header className="h-20 bg-white/80 backdrop-blur-md border-b border-gray-100 flex items-center justify-between px-10 sticky top-0 z-50">
                    <h2 className="text-sm font-black text-gray-400 uppercase tracking-widest">Sistema de Calificación OMR</h2>
                    <div className="flex items-center gap-4">
                        <div className="text-right">
                            <p className="text-sm font-bold text-gray-900">Admin Einstein</p>
                            <p className="text-[10px] text-gray-400 font-bold uppercase">Docente</p>
                        </div>
                        <div className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center text-white font-black text-lg shadow-lg shadow-red-200">
                            AE
                        </div>
                    </div>
                </header>
                
                <div className="p-0">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default function App() {
  const hasKey = !!localStorage.getItem('einscan_key');

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/admin-login" element={<AdminPanel />} />
        {!hasKey ? (
            <Route path="*" element={<KeyEntry />} />
        ) : (
            <Route path="*" element={
                <MainLayout>
                    <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/generator" element={<Generator />} />
                        <Route path="/scanner" element={<Scanner />} />
                        <Route path="/answers" element={<AnswerKeys />} />
                        <Route path="/results" element={<Results />} />
                        <Route path="*" element={<Navigate to="/" />} />
                    </Routes>
                </MainLayout>
            } />
        )}
      </Routes>
    </BrowserRouter>
  );
}
