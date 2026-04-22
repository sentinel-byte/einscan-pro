import React from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, 
  FilePlus, 
  ScanLine, 
  KeyRound, 
  BarChart3, 
  Settings,
  LogOut
} from 'lucide-react';

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

const Layout = ({ children }) => {
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
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
          <button className="flex items-center gap-3 px-4 py-3 w-full text-gray-600 hover:bg-red-50 hover:text-red-600 rounded-lg transition-colors">
            <LogOut size={20} />
            <span className="font-medium">Cerrar Sesión</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
          <h2 className="text-lg font-semibold text-gray-800">Sistema de Calificación OMR</h2>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">Admin Einstein</p>
              <p className="text-xs text-gray-500">Docente Autorizado</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-bold">
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
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/generator" element={<Generator />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/answers" element={<AnswerKeys />} />
          <Route path="/results" element={<Results />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
