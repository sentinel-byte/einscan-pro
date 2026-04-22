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
      // Inicializar campos editables para cada resultado
      const initialResults = res.data.processed.map(r => ({
        ...r,
        editableDni: r.dni,
        editableName: '',
        confirmed: false
      }));
      setResults(initialResults);
      setCurrentStep('confirm');
    } catch (error) {
      alert("Error en el motor OMR. Asegúrate de que las fotos sean nítidas.");
      setCurrentStep('upload');
    } finally {
      setProcessing(false);
    }
  };

  const confirmResult = async (idx) => {
    const res = results[idx];
    if (!res.editableDni) {
        alert("El DNI es obligatorio");
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
        <div className="space-y-6">
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
               <div className="p-4 bg-gray-50 font-bold border-b text-gray-700">Archivos listos ({files.length})</div>
               <div className="p-4 space-y-2">
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
        <div className="bg-white p-20 rounded-3xl border border-gray-100 text-center shadow-xl">
           <Loader2 size={64} className="mx-auto text-primary animate-spin mb-6" />
           <h3 className="text-2xl font-black text-gray-800">Procesando Inteligencia Artificial...</h3>
           <p className="text-gray-500 max-w-md mx-auto mt-4 text-lg">
             Estamos alineando las imágenes, detectando las burbujas y consultando a Gemini para marcas dudosas.
           </p>
        </div>
      )}

      {currentStep === 'confirm' && (
        <div className="grid grid-cols-1 gap-6">
          {results.map((res, idx) => (
            <div key={idx} className={`bg-white p-6 rounded-2xl border-2 transition-all shadow-sm flex flex-col md:flex-row gap-8 ${res.confirmed ? 'border-green-500 bg-green-50' : 'border-gray-100'}`}>
              
              {/* Miniatura de la hoja */}
              <div className="relative group w-full md:w-48 aspect-[1.4/1] bg-gray-100 rounded-xl overflow-hidden border">
                  <img src={`/api/scanner/view/${res.scan_id}`} className="w-full h-full object-cover" alt="Ficha" />
                  <a href={`/api/scanner/view/${res.scan_id}`} target="_blank" className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 flex items-center justify-center text-white transition-opacity">
                    <Eye size={24} />
                  </a>
              </div>

              {/* Datos Detectados */}
              <div className="flex-1 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">DNI / Código Detectado</label>
                  <input 
                    type="text" 
                    value={res.editableDni}
                    disabled={res.confirmed}
                    onChange={e => {
                        const newRes = [...results];
                        newResults[idx].editableDni = e.target.value;
                        setResults(newRes);
                    }}
                    className="w-full mt-1 px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl font-mono text-2xl text-primary focus:border-primary outline-none"
                  />
                </div>
                <div>
                  <label className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Nombre del Alumno (Opcional)</label>
                  <input 
                    type="text" 
                    placeholder="Escribir nombre..."
                    value={res.editableName}
                    disabled={res.confirmed}
                    onChange={e => {
                        const newRes = [...results];
                        newResults[idx].editableName = e.target.value;
                        setResults(newRes);
                    }}
                    className="w-full mt-1 px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-xl focus:border-primary outline-none"
                  />
                </div>
              </div>

              {/* Botón de Acción */}
              <div className="flex items-center">
                {!res.confirmed ? (
                  <button 
                    onClick={() => confirmResult(idx)}
                    className="w-full md:w-auto px-8 py-4 bg-gray-900 text-white rounded-xl font-bold hover:bg-black transition-colors"
                  >
                    Confirmar Nota
                  </button>
                ) : (
                  <div className="flex items-center gap-2 text-green-600 font-black text-lg">
                    <CheckCircle2 size={28} /> CALIFICADO
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
