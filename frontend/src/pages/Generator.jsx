import React, { useState } from 'react';
import { FileText, Download, Loader2, CheckCircle, Eye, ArrowLeft } from 'lucide-react';
import axios from 'axios';

export default function Generator() {
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    num_questions: 60,
    options_per_question: 5,
    scoring_formula: 'simple'
  });
  const [loading, setLoading] = useState(false);
  const [generatedPdf, setGeneratedPdf] = useState(null);
  const [showPreview, setShowPreview] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const examRes = await axios.post('/api/exams/', formData);
      const examId = examRes.data.id;
      
      const genRes = await axios.post(`/api/generator/generate/${examId}`);
      setGeneratedPdf({
        id: examId,
        url: genRes.data.pdf_url
      });
      setShowPreview(true);
    } catch (error) {
      console.error("Error generating exam:", error);
      alert("Hubo un error al generar el examen.");
    } finally {
      setLoading(false);
    }
  };

  if (showPreview && generatedPdf) {
    return (
      <div className="p-8 h-[calc(100vh-64px)] flex flex-col">
        <div className="flex justify-between items-center mb-4">
          <button 
            onClick={() => setShowPreview(false)}
            className="flex items-center gap-2 text-gray-600 hover:text-primary font-medium transition-colors"
          >
            <ArrowLeft size={20} /> Volver a editar
          </button>
          <div className="flex gap-4">
             <div className="flex items-center gap-2 text-green-600 font-bold bg-green-50 px-4 py-2 rounded-lg border border-green-200">
               <CheckCircle size={18} /> ¡Generado con éxito!
             </div>
             <a 
              href={generatedPdf.url}
              download={`ficha_${formData.name}.pdf`}
              className="bg-primary text-white px-8 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-primary-dark shadow-lg shadow-red-200 transition-all"
            >
              <Download size={20} /> Descargar PDF
            </a>
          </div>
        </div>
        
        <div className="flex-1 bg-gray-800 rounded-xl overflow-hidden border-4 border-gray-900 shadow-2xl">
           <iframe 
             src={generatedPdf.url} 
             className="w-full h-full border-none"
             title="Vista Previa PDF"
           />
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 text-center">1. Crear Examen y Ficha</h1>
        <p className="text-gray-500 text-center mt-1">Configura los parámetros para crear tu ficha OMR profesional.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-start">
        {/* Formulario */}
        <div className="bg-white p-8 rounded-2xl border border-gray-200 shadow-xl">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Nombre del Examen</label>
              <input 
                type="text" 
                required
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none"
                placeholder="Ej: Simulacro Admisión"
                value={formData.name}
                onChange={e => setFormData({...formData, name: e.target.value})}
              />
            </div>
            <div>
              <label className="block text-xs font-bold text-gray-400 uppercase mb-1">Asignatura / Materia</label>
              <input 
                type="text" 
                required
                className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition-all outline-none"
                placeholder="Ej: Matemáticas"
                value={formData.subject}
                onChange={e => setFormData({...formData, subject: e.target.value})}
              />
            </div>
            
            <div className="bg-gray-50 p-4 rounded-xl space-y-2 border border-gray-100">
               <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Número de preguntas:</span>
                  <span className="font-bold text-gray-900">60 preguntas</span>
               </div>
               <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Alternativas por pregunta:</span>
                  <span className="font-bold text-gray-900">5 opciones (A, B, C, D, E)</span>
               </div>
               <div className="flex justify-between text-sm">
                  <span className="text-gray-500">Formato de hoja:</span>
                  <span className="font-bold text-gray-900">A4 Horizontal</span>
               </div>
            </div>

            <button 
              type="submit"
              disabled={loading}
              className="w-full bg-primary text-white py-4 rounded-xl font-bold hover:bg-primary-dark transition-all flex items-center justify-center gap-2 shadow-lg shadow-red-100 disabled:opacity-50"
            >
              {loading ? <Loader2 className="animate-spin" /> : <Eye size={20} />}
              {loading ? 'Procesando diseño...' : 'Generar Examen y Ver Ficha'}
            </button>
          </form>
        </div>

        {/* Información / Ayuda */}
        <div className="space-y-6">
          <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-8 flex flex-col items-center text-center">
             <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center shadow-sm mb-4">
               <FileText size={32} className="text-primary" />
             </div>
             <h4 className="font-bold text-gray-800 text-lg">Formato Oficial Único</h4>
             <p className="text-sm text-gray-500 mt-2">
               El sistema generará una ficha profesional dividida en Identificación (izquierda) y Respuestas (derecha) optimizada para el Colegio Albert Einstein.
             </p>
          </div>
          
          <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
            <h4 className="font-bold text-blue-900 flex items-center gap-2 mb-2">
              💡 Información OMR
            </h4>
            <ul className="text-xs text-blue-800 space-y-2 list-disc ml-4">
              <li>Configuración fija de 60 preguntas para máxima precisión.</li>
              <li>Imprime siempre en tamaño <b>A4 Real (100%)</b>.</li>
              <li>No cambies el diseño del PDF después de imprimirlo.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
