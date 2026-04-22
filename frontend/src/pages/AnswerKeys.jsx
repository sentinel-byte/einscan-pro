import React, { useState, useEffect } from 'react';
import { Save, Loader2, Check } from 'lucide-react';
import axios from 'axios';

export default function AnswerKeys() {
  const [exams, setExams] = useState([]);
  const [selectedExam, setSelectedExam] = useState(null);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    axios.get('/api/exams/').then(res => setExams(res.data));
  }, []);

  const handleExamSelect = async (id) => {
    const exam = exams.find(e => e.id === parseInt(id));
    setSelectedExam(exam);
    setLoading(true);
    try {
      const res = await axios.get(`/api/exams/${id}/answers`);
      const ansMap = {};
      res.data.forEach(a => {
        ansMap[a.question_number] = a.correct_answer;
      });
      setAnswers(ansMap);
    } catch (e) {
      setAnswers({});
    } finally {
      setLoading(false);
    }
  };

  const toggleAnswer = (q, letter) => {
    setAnswers(prev => ({
      ...prev,
      [q]: prev[q] === letter ? null : letter
    }));
  };

  const handleSave = async () => {
    if (!selectedExam) return;
    setSaving(true);
    const payload = Object.entries(answers)
      .filter(([_, ans]) => ans !== null)
      .map(([q, ans]) => ({
        question_number: parseInt(q),
        correct_answer: ans,
        points: 1.0
      }));
    
    try {
      await axios.post(`/api/exams/${selectedExam.id}/answers`, payload);
      alert("Clave guardada con éxito.");
    } catch (e) {
      alert("Error al guardar clave.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="p-8 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Configurar Claves de Respuestas</h1>
          <p className="text-gray-500">Define las respuestas correctas para calificar automáticamente.</p>
        </div>
        {selectedExam && (
          <button 
            onClick={handleSave}
            disabled={saving}
            className="bg-primary text-white px-6 py-2 rounded-lg font-bold flex items-center gap-2 hover:bg-primary-dark transition-colors"
          >
            {saving ? <Loader2 className="animate-spin" size={18} /> : <Save size={18} />}
            Guardar Clave
          </button>
        )}
      </div>

      <div className="bg-white p-6 rounded-xl border border-gray-200 mb-8">
        <label className="block text-sm font-medium text-gray-700 mb-2">Seleccionar Examen</label>
        <select 
          className="w-full md:w-1/2 px-4 py-2 border border-gray-300 rounded-lg"
          onChange={e => handleExamSelect(e.target.value)}
        >
          <option value="">-- Selecciona --</option>
          {exams.map(e => <option key={e.id} value={e.id}>{e.name}</option>)}
        </select>
      </div>

      {loading ? (
        <div className="text-center py-20"><Loader2 className="animate-spin mx-auto text-primary" size={40} /></div>
      ) : selectedExam ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: selectedExam.num_questions }, (_, i) => i + 1).map(q => (
            <div key={q} className="bg-white p-4 rounded-lg border border-gray-200 flex items-center justify-between">
              <span className="font-bold text-gray-600 w-8">{q}.</span>
              <div className="flex gap-2">
                {['A', 'B', 'C', 'D', 'E'].slice(0, selectedExam.options_per_question).map(letter => (
                  <button
                    key={letter}
                    onClick={() => toggleAnswer(q, letter)}
                    className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                      answers[q] === letter 
                        ? 'bg-primary text-white shadow-md transform scale-110' 
                        : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
                    }`}
                  >
                    {letter}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-gray-50 border-2 border-dashed border-gray-200 rounded-2xl p-20 text-center">
          <p className="text-gray-400">Selecciona un examen para empezar a configurar las respuestas.</p>
        </div>
      )}
    </div>
  );
}
