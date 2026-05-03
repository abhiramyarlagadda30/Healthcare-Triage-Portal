import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const vitalLabels = {
  bp:   'Blood Pressure',
  hr:   'Heart Rate',
  temp: 'Temperature',
  spo2: 'SpO2',
  rr:   'Resp. Rate',
};

function App() {
  const [vitals, setVitals] = useState({
    age: '', systolicBP: '', diastolicBP: '', heartRate: '', temperature: ''
  });
  const [riskResult, setRiskResult]   = useState(null);
  const [loading, setLoading]         = useState(false);
  const [transcript, setTranscript]   = useState('');
  const [report, setReport]           = useState(null);
  const [summarizing, setSummarizing] = useState(false);

  const handleVitalsChange = (e) =>
    setVitals({ ...vitals, [e.target.name]: e.target.value });

  const handleTriage = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/triage`, {
        age:         parseInt(vitals.age),
        systolicBP:  parseInt(vitals.systolicBP),
        diastolicBP: parseInt(vitals.diastolicBP),
        heartRate:   parseInt(vitals.heartRate),
        temperature: parseFloat(vitals.temperature),
      });
      setRiskResult(res.data);
    } catch (err) {
      console.error('Triage error:', err);
      alert('Error processing vitals. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!transcript.trim()) { alert('Please enter clinical notes'); return; }
    setSummarizing(true);
    try {
      const res = await axios.post(`${API_BASE_URL}/summarize`, { transcript });
      setReport(res.data);
    } catch (err) {
      console.error('Summarization error:', err);
      alert('Error processing transcript. Please try again.');
    } finally {
      setSummarizing(false);
    }
  };

  const riskClass = (risk) => (risk ? risk.toLowerCase() : '');

  return (
    <div className="App">

      {/* ── Header ── */}
      <header className="app-header">
        <div className="header-badge">
          <span className="header-dot" />
          AI-Powered Healthcare System
        </div>
        <h1>Intelligent Triage Portal</h1>
        <p>Real-time Risk Assessment &amp; Clinical Notes Processing</p>
      </header>

      <div className="container">

        {/* ── Left: Vitals ── */}
        <div className="card">
          <div className="card-title">
            <div className="card-icon">📊</div>
            <h2>Patient Vitals Assessment</h2>
          </div>

          <form onSubmit={handleTriage}>
            <div className="form-group">
              <label>Age (years)</label>
              <input type="number" name="age" value={vitals.age}
                onChange={handleVitalsChange} required min="0" max="150"
                placeholder="e.g. 45" />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Systolic BP (mmHg)</label>
                <input type="number" name="systolicBP" value={vitals.systolicBP}
                  onChange={handleVitalsChange} required placeholder="e.g. 120" />
              </div>
              <div className="form-group">
                <label>Diastolic BP (mmHg)</label>
                <input type="number" name="diastolicBP" value={vitals.diastolicBP}
                  onChange={handleVitalsChange} required placeholder="e.g. 80" />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Heart Rate (bpm)</label>
                <input type="number" name="heartRate" value={vitals.heartRate}
                  onChange={handleVitalsChange} required placeholder="e.g. 72" />
              </div>
              <div className="form-group">
                <label>Temperature (°F)</label>
                <input type="number" name="temperature" value={vitals.temperature}
                  onChange={handleVitalsChange} step="0.1" required
                  placeholder="e.g. 98.6" />
              </div>
            </div>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : '⚡ Predict Risk Level'}
            </button>
          </form>

          {riskResult && (
            <div className={`risk-indicator ${riskClass(riskResult.risk_level)}`}>
              <div className="risk-header">
                <div>
                  <div className="risk-label">Risk Assessment Result</div>
                  <div className={`risk-level-text ${riskClass(riskResult.risk_level)}`}>
                    {riskResult.risk_level} Risk
                  </div>
                </div>
                <span className={`risk-score-badge ${riskClass(riskResult.risk_level)}`}>
                  {riskResult.risk_score}/3
                </span>
              </div>

              <div className="vitals-grid">
                <div className="vital-chip">
                  <div className="vital-chip-label">Blood Pressure</div>
                  <div className="vital-chip-val">{riskResult.vital_signs_summary.blood_pressure}</div>
                </div>
                <div className="vital-chip">
                  <div className="vital-chip-label">Heart Rate</div>
                  <div className="vital-chip-val">{riskResult.vital_signs_summary.heart_rate} bpm</div>
                </div>
                <div className="vital-chip">
                  <div className="vital-chip-label">Temperature</div>
                  <div className="vital-chip-val">{riskResult.vital_signs_summary.temperature} °F</div>
                </div>
                <div className="vital-chip">
                  <div className="vital-chip-label">Patient Age</div>
                  <div className="vital-chip-val">{riskResult.vital_signs_summary.age} yrs</div>
                </div>
              </div>

              <div className="rec-title">Clinical Recommendations</div>
              <ul className="rec-list">
                {riskResult.recommendations.map((rec, i) => (
                  <li key={i}>{rec}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* ── Right: Clinical Notes ── */}
        <div className="card">
          <div className="card-title">
            <div className="card-icon">📝</div>
            <h2>Clinical Notes Parser</h2>
          </div>

          <div className="form-group">
            <label>Doctor's Voice-to-Text Transcript</label>
            <textarea
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              placeholder="Paste transcript — e.g. 'Patient has chest pain and fever, BP 130/85, HR 92, prescribe ibuprofen 400mg and aspirin 75mg, diagnosis hypertension, follow up in 7 days'"
            />
          </div>
          <button className="btn-primary" onClick={handleSummarize} disabled={summarizing}>
            {summarizing ? 'Processing...' : '🧠 Generate Structured Report'}
          </button>

          {report && (
            <div className="structured-report">
              <div className="report-header">
                <div className="report-header-dot" />
                <h3>Structured Medical Report</h3>
              </div>

              <div className="report-body">

                <div className="report-field">
                  <div className="report-field-label">Symptoms</div>
                  {report.symptoms && report.symptoms.length > 0 ? (
                    <div className="tags">
                      {report.symptoms.map((s, i) => <span key={i} className="tag">{s}</span>)}
                    </div>
                  ) : (
                    <p className="empty-field">No symptoms recorded</p>
                  )}
                </div>

                <div className="report-field">
                  <div className="report-field-label">Vitals</div>
                  {report.vitals && Object.entries(report.vitals).filter(([, v]) => v && v.trim() !== '').length > 0 ? (
                    <div className="vitals-table">
                      {Object.entries(report.vitals)
                        .filter(([, v]) => v && v.trim() !== '')
                        .map(([k, v]) => (
                          <div key={k} className="vitals-row">
                            <span className="vital-key">
                              {vitalLabels[k.toLowerCase()] || k.toUpperCase()}
                            </span>
                            <span className="vital-val">{v}</span>
                          </div>
                        ))}
                    </div>
                  ) : (
                    <p className="empty-field">No vitals recorded</p>
                  )}
                </div>

                {report.diagnosis && report.diagnosis.trim() !== '' && (
                  <div className="report-field">
                    <div className="report-field-label">Diagnosis</div>
                    <div className="report-field-value">{report.diagnosis}</div>
                  </div>
                )}

                <div className="report-field">
                  <div className="report-field-label">Treatment Plan</div>
                  <div className="report-field-value">{report.plan || 'Not specified'}</div>
                </div>

                {report.medications && report.medications.length > 0 && (
                  <div className="report-field">
                    <div className="report-field-label">Medications</div>
                    <ul className="med-list">
                      {report.medications.map((m, i) => <li key={i}>{m}</li>)}
                    </ul>
                  </div>
                )}

                <div className="report-field">
                  <div className="report-field-label">Follow-up</div>
                  <div className="report-field-value">{report.follow_up || 'Not specified'}</div>
                </div>

              </div>
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default App;