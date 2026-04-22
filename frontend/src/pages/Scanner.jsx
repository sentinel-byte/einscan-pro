import React, { useState, useEffect } from 'react';
import { Upload, Scan, Loader2, CheckCircle2, AlertCircle, Trash2, Eye } from 'lucide-react';
import axios from 'axios';

export default function Scanner() {
  const [exams, setExams] = useState([]);
  const [selectedExam, setSelectedExam] = useState('');
  const [files, setFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState([]);
  const [currentStep, setCurrentStep] = useState('upload');

  useEffect(() => {
    axios.get('/api/exams/').then(res => setExams(res.data));
  }, []);

  const handleUpload = async () => {
    if (!selectedExam || files.length === 0) return;
    setProcessing(true);
    setCurrentStep('processing');
    
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    
    try {
      const res = await axios.post(`/api/scanner/upload/${selectedExam}`, formData);
      // Inicializar campos editables con los datos del OCR y OMR
      const initialResults = res.data.processed.map(r => ({
        ...r,
        editableDni: r.dni || '',
        editableName: r.ocr_name || '', // Usar el nombre detectado por Tesseract
        confirmed: false
      }));
      setResults(initialResults);
      setCurrentStep('confirm');
    } catch (error) {
      alert("Error en el motor OMR. Asegúrate de que las fotos sean nítidas y tengan buena luz.");
      setCurrentStep('upload');
    } finally {
      setProcessing(false);
    }
  };

  const confirmResult = async (idx) => {
    const res = results[idx];
    if (!res.editableDni || res.editableDni.includes('?')) {
        alert("Por favor, corrige el DNI. No puede contener signos de interrogación.");
        return;
    }
    
    try {
      await axios.post(`/api/scanner/confirm/${res.scan_id}`, {
        dni: res.editableDni,
        student_name: res.editableName || `Estudiante ${res.editableDni}`
      });
      const newResults = [...results];
      newResults[idx].confirmed = true;
      setResults(newResults);
    } catch (error) {
      alert("Error al guardar la calificación.");
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">3. Escanear Hojas OMR</h1>
          <p className="text-gray-500">Sube fotos de las fichas para calificarlas automáticamente.</p>
        </div>
        {currentStep === 'confirm' && (
           <button 
             onClick={() => {setCurrentStep('upload'); setFiles([]);}}
             className="text-primary font-bold hover:underline"
           >
             + Subir más fotos
           </button>
        )}
      </div>

      {currentStep === 'upload' && (
        <div className="space-y-6 animate-in fade-in zoom-in duration-300">
          <div className="bg-white p-6 rounded-xl border-2 border-gray-100 shadow-sm">
            <label className="block text-sm font-bold text-gray-700 mb-2 uppercase tracking-wide">Selecciona el Examen Correspondiente</label>
            <select 
              className="w-full md:w-1/2 px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary outline-none"
              value={selectedExam}
              onChange={e => setSelectedExam(e.target.value)}
            >
              <option value="">-- Elige un examen de la lista --</option>
              {exams.map(ex => (
                <option key={ex.id} value={ex.id}>{ex.name} ({ex.subject})</option>
              ))}
            </select>
          </div>

          <div className="border-4 border-dashed border-gray-200 rounded-3xl p-16 bg-white text-center hover:border-primary/30 transition-colors">
            <input type="file" multiple onChange={e => setFiles(Array.from(e.target.files))} className="hidden" id="file-upload" accept="image/*" />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <div className="w-20 h-20 bg-red-50 rounded-full flex items-center justify-center mb-4">
                <Upload size={40} className="text-primary" />
              </div>
              <p className="text-xl font-bold text-gray-800">Arrastra las fotos aquí</p>
              <p className="text-gray-500 mt-2">O haz clic para buscar en tu computadora</p>
            </label>
          </div>

          {files.length > 0 && (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
               <div className="p-4 bg-gray-50 font-bold border-b text-gray-700 flex justify-between items-center">
                  <span>Archivos listos ({files.length})</span>
                  <button onClick={() => setFiles([])} className="text-xs text-red-500 hover:underline">Limpiar</button>
               </div>
               <div className="p-4 space-y-2 max-h-40 overflow-auto">
                  {files.map((f, i) => <div key={i} className="text-sm text-gray-600 flex items-center gap-2">📄 {f.name}</div>)}
               </div>
            </div>
          )}

          <button 
            onClick={handleUpload}
            disabled={!selectedExam || files.length === 0}
            className="w-full bg-primary text-white py-5 rounded-2xl font-black text-lg hover:bg-primary-dark shadow-xl shadow-red-100 disabled:opacity-50 transition-all active:scale-[0.98]"
          >
            {processing ? <Loader2 className="animate-spin inline mr-2" /> : <Scan className="inline mr-2" />}
            INICIAR CALIFICACIÓN AUTOMÁTICA
          </button>
        </div>
      )}

      {currentStep === 'processing' && (
        <div className="bg-white p-20 rounded-3xl border border-gray-100 text-center shadow-xl animate-pulse">
           <Loader2 size={64} className="mx-auto text-primary animate-spin mb-6" />
           <h3 className="text-2xl font-black text-gray-800 uppercase tracking-tighter">Analizando Imágenes...</h3>
           <p className="text-gray-500 max-w-md mx-auto mt-4 text-lg">
             El motor OMR está alineando las hojas y extrayendo los datos de DNI, tipo de examen y respuestas.
           </p>
        </div>
      )}

      {currentStep === 'confirm' && (
        <div className="grid grid-cols-1 gap-6 animate-in slide-in-from-bottom duration-500">
          {results.map((res, idx) => (
            <div key={idx} className={`bg-white p-6 rounded-2xl border-2 transition-all shadow-sm flex flex-col lg:flex-row gap-8 ${res.status === 'error' ? 'border-red-200 bg-red-50' : res.confirmed ? 'border-green-500 bg-green-50' : 'border-gray-100'}`}>
              
              {res.status === 'error' ? (
                <div className="flex-1 flex items-center gap-4 text-red-600 p-4">
                  <AlertCircle size={32} />
                  <div>
                    <p className="font-bold">Error en {res.filename}</p>
                    <p className="text-sm">{res.message}</p>
                  </div>
                </div>
              ) : (
                <>
                  {/* Miniatura */}
                  <div className="relative group w-full lg:w-48 aspect-[1.4/1] bg-gray-100 rounded-xl overflow-hidden border-2 border-gray-200">
                      <img src={`/api/scanner/view/${res.scan_id}`} className="w-full h-full object-cover" alt="Ficha" />
                      <div className="absolute top-2 right-2 bg-black/60 text-white text-[10px] px-2 py-1 rounded">DEBUG</div>
                      <a href={`/api/scanner/view/${res.scan_id}`} target="_blank" rel="noreferrer" className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity">
                        <Eye size={24} />
                      </a>
                  </div>

                  {/* Datos */}
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">DNI / Código</label>
                      <input 
                        type="text" 
                        value={res.editableDni}
                        disabled={res.confirmed}
                        onChange={e => {
                            const newRes = [...results];
                            newRes[idx].editableDni = e.target.value.replace(/[^0-9?]/g, '');
                            setResults(newRes);
                        }}
                        className={`w-full mt-1 px-4 py-3 border-2 rounded-xl font-mono text-2xl outline-none transition-all ${res.editableDni.includes('?') ? 'border-amber-400 bg-amber-50 text-amber-700' : 'border-gray-200 bg-gray-50 text-primary focus:border-primary'}`}
                      />
                      {res.editableDni.includes('?') && <p className="text-[10px] text-amber-600 font-bold mt-1 uppercase">⚠️ Corrige los caracteres desconocidos (?)</p>}
                    </div>
                    <div>
                      <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Nombre Completo (OCR)</label>
                      <input 
                        type="text" 
                        placeholder="Nombre del estudiante..."
                        value={res.editableName}
                        disabled={res.confirmed}
                        onChange={e => {
                            const newRes = [...results];
                            newRes[idx].editableName = e.target.value.toUpperCase();
                            setResults(newRes);
                        }}
                        className="w-full mt-1 px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-primary outline-none font-bold text-gray-800"
                      />
                      {!res.editableName && <p className="text-[10px] text-gray-400 mt-1 uppercase tracking-tighter italic">Tesseract no pudo leer el nombre con claridad.</p>}
                    </div>
                  </div>

                  {/* Acción */}
                  <div className="flex items-center">
                    {!res.confirmed ? (
                      <button 
                        onClick={() => confirmResult(idx)}
                        className="w-full lg:w-auto px-8 py-4 bg-gray-900 text-white rounded-xl font-black hover:bg-black transition-all shadow-lg active:scale-95"
                      >
                        CONFIRMAR NOTA
                      </button>
                    ) : (
                      <div className="flex items-center gap-3 text-green-600 font-black text-lg bg-white px-6 py-3 rounded-2xl border-2 border-green-500 shadow-sm">
                        <CheckCircle2 size={28} /> CALIFICADO
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

