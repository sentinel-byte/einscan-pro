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
import { Download, Search, Filter, Info, FileSpreadsheet, Trash2, AlertTriangle, Loader2 } from 'lucide-react';
import axios from 'axios';

export default function Results() {
  const [exams, setExams] = useState([]);
  const [selectedExamId, setSelectedExamId] = useState('');
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = () => {
    axios.get('/api/exams/').then(res => setExams(res.data));
  };

  const handleExamChange = async (id) => {
    setSelectedExamId(id);
    if (!id) {
        setResults([]);
        setStats(null);
        return;
    }
    
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

  const handleDeleteExam = async () => {
    if (!selectedExamId) return;
    const confirm = window.confirm("¿ESTÁS COMPLETAMENTE SEGURO? Esta acción borrará permanentemente este examen, todas las respuestas, las fotos escaneadas y las notas de los alumnos. No se puede deshacer.");
    
    if (confirm) {
      setDeleting(true);
      try {
        await axios.delete(`/api/exams/${selectedExamId}`);
        alert("Examen y todos sus datos eliminados con éxito.");
        setSelectedExamId('');
        setResults([]);
        setStats(null);
        loadExams();
      } catch (e) {
        alert("Error al eliminar el examen.");
      } finally {
        setDeleting(false);
      }
    }
  };

  const exportExcel = () => {
    if (!selectedExamId) return;
    window.open(`/api/export/excel/${selectedExamId}`, '_blank');
  };

  const exportPdfBoletas = () => {
    if (!selectedExamId) return;
    window.open(`/api/export/pdf-boletas/${selectedExamId}`, '_blank');
  };

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">4. Resultados y Análisis</h1>
          <p className="text-gray-500">Consulta los puntajes detallados y descarga los reportes finales.</p>
        </div>
        {selectedExamId && (
          <div className="flex gap-3">
            <button 
                onClick={exportPdfBoletas}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-50 transition-colors shadow-sm"
            >
              <Download size={16} /> PDF Boletas
            </button>
            <button 
                onClick={exportExcel}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-bold hover:bg-green-700 transition-colors shadow-lg shadow-green-100"
            >
              <FileSpreadsheet size={16} /> Exportar Excel
            </button>
          </div>
        )}
      </div>

      <div className="bg-white p-8 rounded-2xl border-2 border-gray-100 shadow-xl flex flex-col md:flex-row gap-6 items-end">
        <div className="flex-1 w-full">
          <label className="block text-xs font-black text-gray-400 uppercase tracking-widest mb-2">Selecciona un Examen para Auditar</label>
          <select 
            className="w-full px-4 py-3 border-2 border-gray-100 rounded-xl focus:ring-2 focus:ring-primary outline-none bg-gray-50 font-bold"
            value={selectedExamId}
            onChange={e => handleExamChange(e.target.value)}
          >
            <option value="">-- Ver lista de exámenes finalizados --</option>
            {exams.map(e => <option key={e.id} value={e.id}>{e.name} - {e.subject}</option>)}
          </select>
        </div>
        
        {selectedExamId && (
            <button 
                onClick={handleDeleteExam}
                disabled={deleting}
                className="flex items-center gap-2 px-6 py-3 bg-red-50 text-red-600 rounded-xl text-sm font-black hover:bg-red-600 hover:text-white transition-all border-2 border-red-100"
            >
              {deleting ? <Loader2 className="animate-spin" size={18} /> : <Trash2 size={18} />}
              ELIMINAR TODO EL EXAMEN
            </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-20 flex flex-col items-center gap-4">
            <Loader2 className="animate-spin text-primary" size={48} />
            <p className="text-gray-500 font-bold">Generando reportes estadísticos...</p>
        </div>
      ) : stats && results.length > 0 ? (
        <div className="space-y-8 animate-in fade-in duration-500">
          {/* Dashboard de resumen rápido */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            {[
              { label: 'Promedio Grupal', value: stats.summary.mean.toFixed(2) },
              { label: 'Nota Más Alta', value: stats.summary.max.toFixed(2) },
              { label: 'Nota Más Baja', value: stats.summary.min.toFixed(2) },
              { label: 'Total Alumnos', value: stats.summary.count }
            ].map((s, i) => (
              <div key={i} className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm text-center">
                <p className="text-[10px] font-black text-gray-400 uppercase tracking-widest">{s.label}</p>
                <p className="text-3xl font-black text-primary mt-1">{s.value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
             {/* Tabla */}
             <div className="lg:col-span-2 bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-gray-50 flex justify-between items-center">
                    <h3 className="font-black text-gray-800 uppercase tracking-tight">Ranking de Estudiantes</h3>
                    <span className="bg-primary/10 text-primary text-xs font-bold px-3 py-1 rounded-full">{results.length} registros</span>
                </div>
                <table className="w-full text-left">
                  <thead className="bg-gray-50/50">
                    <tr>
                      <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase">Estudiante</th>
                      <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase">DNI</th>
                      <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase">Aciertos</th>
                      <th className="px-6 py-4 text-[10px] font-black text-gray-400 uppercase text-right">Nota Final</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-50">
                    {results.sort((a,b) => b.score - a.score).map((r, i) => (
                      <tr key={i} className="hover:bg-gray-50/50 transition-colors">
                        <td className="px-6 py-4 font-bold text-gray-900">{r.student_name}</td>
                        <td className="px-6 py-4 text-sm text-gray-500 font-mono">{r.dni}</td>
                        <td className="px-6 py-4">
                           <div className="flex items-center gap-2">
                               <span className="text-green-600 font-black">{r.correct}</span>
                               <div className="w-16 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                                   <div className="h-full bg-green-500" style={{width: `${(r.correct/60)*100}%`}}></div>
                               </div>
                           </div>
                        </td>
                        <td className="px-6 py-4 text-right">
                           <span className={`px-4 py-1.5 rounded-xl font-black text-sm ${r.score >= 10 ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                             {r.score.toFixed(2)}
                           </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
             </div>

             {/* Sidebar stats */}
             <div className="space-y-6">
                <div className="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm">
                   <h3 className="font-black text-gray-800 mb-6 uppercase tracking-tight">Dificultad por Pregunta</h3>
                   <div className="space-y-4">
                      {Object.entries(stats.item_analysis).slice(0, 10).map(([q, data]) => (
                        <div key={q} className="flex items-center justify-between">
                           <span className="text-xs font-bold text-gray-500">Pregunta {q}</span>
                           <div className="flex items-center gap-3">
                              <div className="w-24 h-2 bg-gray-50 rounded-full overflow-hidden border border-gray-100">
                                 <div 
                                    className={`h-full transition-all ${data.difficulty_index > 0.7 ? 'bg-green-500' : data.difficulty_index > 0.4 ? 'bg-amber-500' : 'bg-red-500'}`} 
                                    style={{width: `${data.difficulty_index * 100}%`}}
                                 ></div>
                              </div>
                              <span className="text-[10px] font-black w-8">{(data.difficulty_index * 100).toFixed(0)}%</span>
                           </div>
                        </div>
                      ))}
                   </div>
                   <div className="mt-8 p-4 bg-blue-50 rounded-xl flex gap-3">
                       <Info size={20} className="text-blue-500 shrink-0" />
                       <p className="text-[10px] text-blue-700 leading-relaxed font-medium">
                          El porcentaje indica cuántos alumnos marcaron la respuesta correcta. Rojo significa pregunta muy difícil.
                       </p>
                   </div>
                </div>
             </div>
          </div>
        </div>
      ) : selectedExamId ? (
        <div className="bg-white border-2 border-dashed border-gray-200 rounded-3xl p-20 text-center space-y-4">
           <div className="w-20 h-20 bg-gray-50 rounded-full flex items-center justify-center mx-auto text-gray-300">
              <AlertTriangle size={40} />
           </div>
           <h3 className="text-xl font-bold text-gray-800">No hay datos para mostrar</h3>
           <p className="text-gray-500 max-w-sm mx-auto">Este examen no tiene hojas escaneadas o confirmadas todavía. Ve al paso 3 para subir fotos.</p>
        </div>
      ) : (
        <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-3xl p-32 text-center">
          <p className="text-gray-400 font-bold text-lg">Selecciona un examen de la lista superior para ver el análisis completo.</p>
        </div>
      )}
    </div>
  );
}
