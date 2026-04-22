import React, { useState, useEffect } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer,
  CartesianGrid
} from 'recharts';
import { Download, Search, Filter, Info, FileSpreadsheet } from 'lucide-react';
import axios from 'axios';

export default function Results() {
  const [exams, setExams] = useState([]);
  const [selectedExamId, setSelectedExamId] = useState('');
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get('/api/exams/').then(res => setExams(res.data));
  }, []);

  const handleExamChange = async (id) => {
    setSelectedExamId(id);
    if (!id) return;
    
    setLoading(true);
    try {
      const [resData, statData] = await Promise.all([
        axios.get(`/api/results/${id}`),
        axios.get(`/api/results/${id}/stats`)
      ]);
      setResults(resData.data);
      setStats(statData.data);
    } catch (e) {
      alert("Error al cargar resultados.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-8">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Resultados y Análisis</h1>
          <p className="text-gray-500">Consulta los puntajes detallados y métricas de cada examen.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-medium hover:bg-gray-50">
            <Download size={16} /> PDF Boletas
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700">
            <FileSpreadsheet size={16} /> Exportar Excel
          </button>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-200 flex flex-wrap gap-4 items-end">
        <div className="flex-1 min-w-[300px]">
          <label className="block text-sm font-medium text-gray-700 mb-2">Seleccionar Examen</label>
          <select 
            className="w-full px-4 py-2 border border-gray-300 rounded-lg"
            value={selectedExamId}
            onChange={e => handleExamChange(e.target.value)}
          >
            <option value="">-- Elige un examen para ver resultados --</option>
            {exams.map(e => <option key={e.id} value={e.id}>{e.name} - {e.subject}</option>)}
          </select>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          <input 
            type="text" 
            placeholder="Buscar alumno o DNI..."
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-64"
          />
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-gray-500">Cargando datos...</div>
      ) : stats ? (
        <div className="space-y-8">
          {/* Dashboard de resumen rápido */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { label: 'Promedio', value: stats.summary.mean.toFixed(1) },
              { label: 'Nota Máxima', value: stats.summary.max },
              { label: 'Nota Mínima', value: stats.summary.min },
              { label: 'Participantes', value: stats.summary.count }
            ].map((s, i) => (
              <div key={i} className="bg-white p-4 rounded-xl border border-gray-200 text-center">
                <p className="text-xs font-bold text-gray-500 uppercase">{s.label}</p>
                <p className="text-2xl font-bold text-primary mt-1">{s.value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
             {/* Tabla */}
             <div className="lg:col-span-2 bg-white rounded-xl border border-gray-200 overflow-hidden">
                <table className="w-full text-left">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Estudiante</th>
                      <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">DNI</th>
                      <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase">Correctas</th>
                      <th className="px-6 py-3 text-xs font-bold text-gray-500 uppercase text-right">Nota Final</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {results.map((r, i) => (
                      <tr key={i} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-medium text-gray-900">Estudiante #{r.student_id}</td>
                        <td className="px-6 py-4 text-sm text-gray-600 font-mono">12345678</td>
                        <td className="px-6 py-4">
                           <span className="text-green-600 font-bold">{r.correct}</span>
                           <span className="text-gray-300 mx-1">/</span>
                           <span className="text-gray-500">{r.correct + r.wrong + r.blank}</span>
                        </td>
                        <td className="px-6 py-4 text-right">
                           <span className={`px-3 py-1 rounded-full font-bold ${r.score >= 70 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                             {r.score.toFixed(1)}
                           </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
             </div>

             {/* Sidebar stats */}
             <div className="space-y-6">
                <div className="bg-white p-6 rounded-xl border border-gray-200">
                   <h3 className="font-bold text-gray-900 mb-4">Análisis de Ítems</h3>
                   <div className="space-y-4">
                      {Object.entries(stats.item_analysis).slice(0, 5).map(([q, data]) => (
                        <div key={q} className="flex items-center justify-between">
                           <span className="text-sm text-gray-600">Pregunta {q}</span>
                           <div className="flex items-center gap-2">
                              <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                                 <div className="h-full bg-blue-500" style={{width: `${data.difficulty_index * 100}%`}}></div>
                              </div>
                              <span className="text-xs font-bold">{(data.difficulty_index * 100).toFixed(0)}%</span>
                           </div>
                        </div>
                      ))}
                   </div>
                   <p className="text-[10px] text-gray-400 mt-4 flex items-center gap-1">
                      <Info size={10} /> El % indica la tasa de aciertos (Dificultad).
                   </p>
                </div>
             </div>
          </div>
        </div>
      ) : (
        <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-20 text-center">
          <p className="text-gray-400">Selecciona un examen para visualizar los resultados analíticos.</p>
        </div>
      )}
    </div>
  );
}
