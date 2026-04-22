import React, { useState, useEffect } from 'react';
import { 
  FilePlus, 
  KeyRound, 
  ScanLine, 
  BarChart3, 
  ArrowRight,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const StepCard = ({ number, icon: Icon, title, desc, to, completed }) => (
  <Link to={to} className="group">
    <div className={`h-full p-8 rounded-3xl border-2 transition-all ${completed ? 'bg-green-50 border-green-200' : 'bg-white border-gray-100 hover:border-primary shadow-xl shadow-gray-200/50 hover:shadow-primary/10'}`}>
      <div className="flex justify-between items-start mb-6">
        <div className={`w-14 h-14 rounded-2xl flex items-center justify-center ${completed ? 'bg-green-500 text-white' : 'bg-gray-900 text-white group-hover:bg-primary'}`}>
          <Icon size={28} />
        </div>
        <span className="text-4xl font-black text-gray-100 group-hover:text-primary/10 transition-colors">{number}</span>
      </div>
      <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
      <p className="text-gray-500 text-sm leading-relaxed mb-6">{desc}</p>
      <div className={`flex items-center gap-2 font-bold text-sm ${completed ? 'text-green-600' : 'text-primary'}`}>
        {completed ? '¡Completado!' : 'Empezar ahora'} <ArrowRight size={16} className="group-hover:translate-x-1 transition-transform" />
      </div>
    </div>
  </Link>
);

export default function Dashboard() {
  const [examCount, setExCount] = useState(0);

  useEffect(() => {
    axios.get('/api/exams/').then(res => setExCount(res.data.length)).catch(() => {});
  }, []);

  return (
    <div className="p-10 max-w-7xl mx-auto">
      <div className="mb-12">
        <h1 className="text-4xl font-black text-gray-900 tracking-tight">Bienvenido a <span className="text-primary">EinScan Pro</span></h1>
        <p className="text-gray-500 text-lg mt-2">Sigue estos 4 pasos para calificar tus exámenes en tiempo récord.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <StepCard 
          number="01" 
          icon={FilePlus} 
          title="Crear Examen" 
          desc="Define el nombre, materia y descarga el PDF de la ficha oficial."
          to="/generator"
          completed={examCount > 0}
        />
        <StepCard 
          number="02" 
          icon={KeyRound} 
          title="Poner Claves" 
          desc="Marca las respuestas correctas para que el sistema pueda calificar."
          to="/answers"
        />
        <StepCard 
          number="03" 
          icon={ScanLine} 
          title="Escanear" 
          desc="Sube las fotos de las hojas llenas por tus alumnos."
          to="/scanner"
        />
        <StepCard 
          number="04" 
          icon={BarChart3} 
          title="Resultados" 
          desc="Mira las notas, promedios y exporta a Excel o PDF."
          to="/results"
        />
      </div>

      {examCount === 0 && (
        <div className="mt-16 bg-primary/5 border-2 border-primary/10 rounded-3xl p-10 flex flex-col md:flex-row items-center gap-8">
           <div className="w-20 h-20 bg-white rounded-2xl flex items-center justify-center shadow-lg text-primary">
              <AlertCircle size={40} />
           </div>
           <div className="flex-1 text-center md:text-left">
              <h2 className="text-2xl font-bold text-gray-900">Aún no tienes ningún examen creado</h2>
              <p className="text-gray-600 mt-1">El primer paso es crear un examen para poder generar la ficha y poner las claves.</p>
           </div>
           <Link to="/generator" className="bg-primary text-white px-10 py-4 rounded-2xl font-black shadow-lg shadow-red-200 hover:scale-105 transition-transform active:scale-95">
              CREAR MI PRIMER EXAMEN
           </Link>
        </div>
      )}

      {examCount > 0 && (
        <div className="mt-16 bg-white border border-gray-100 rounded-3xl p-10 shadow-sm">
           <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
              <CheckCircle2 className="text-green-500" /> Tienes {examCount} exámenes activos
           </h2>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link to="/scanner" className="p-6 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors flex justify-between items-center group">
                 <div>
                    <p className="font-bold text-gray-900">Continuar Escaneando</p>
                    <p className="text-sm text-gray-500">Sube más hojas al sistema</p>
                 </div>
                 <ArrowRight className="text-gray-400 group-hover:text-primary transition-colors" />
              </Link>
              <Link to="/results" className="p-6 bg-gray-50 rounded-2xl hover:bg-gray-100 transition-colors flex justify-between items-center group">
                 <div>
                    <p className="font-bold text-gray-900">Ver Últimos Resultados</p>
                    <p className="text-sm text-gray-500">Consulta las notas actuales</p>
                 </div>
                 <ArrowRight className="text-gray-400 group-hover:text-primary transition-colors" />
              </Link>
           </div>
        </div>
      )}
    </div>
  );
}
