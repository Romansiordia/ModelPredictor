import React, { useState, useRef } from 'react';
import Card from './Card';
import Button from './Button';
import { PreprocessingStep } from '../types';
import { applyPreprocessingLogic, predictPLS } from '../services/chemometrics';
import { parseCSV } from '../services/csvParser';

declare var Papa: any;

interface SavedModel {
    id: string;
    filename: string;
    analyticalProperty: string;
    metrics: {
        plsIntercept: number;
        coefficients: number[];
        xMean?: number[];
        W?: number[][];
        T_inv_var?: number[];
    };
    preprocessing: PreprocessingStep[];
}

const PredictIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-600">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
    </svg>
);

const TrashIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M3 6h18"></path><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"></path><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"></path>
    </svg>
);

const ModelPredictor: React.FC = () => {
    const [models, setModels] = useState<SavedModel[]>([]);
    const [predictions, setPredictions] = useState<{id: string, values: Record<string, number>, ghValues: Record<string, number>, rawSpectrum?: number[], wavelengths?: number[]}[]>([]);
    
    // Webhook / Apps Script State
    const [webhookUrl, setWebhookUrl] = useState(() => localStorage.getItem('agribalance_webhook_url') || '');
    const [sheetName, setSheetName] = useState(() => localStorage.getItem('agribalance_sheet_name') || 'Resultados');
    const [isSaving, setIsSaving] = useState(false);
    

    const handleSheetNameChange = (val: string) => {
        setSheetName(val);
        localStorage.setItem('agribalance_sheet_name', val);
    };

    const handleSaveWebhook = (url: string) => {
        setWebhookUrl(url);
        localStorage.setItem('agribalance_webhook_url', url);
    };

    const handleSendToWebhook = async () => {
        if (!webhookUrl) {
            alert("Por favor, pega la URL de conexión a Google Sheets en el recuadro superior.");
            return;
        }

        if (predictions.length === 0) return;
        
        setIsSaving(true);
        try {
            const timestamp = new Date().toLocaleString();
            
            // 1. Cabeceras base
            const baseHeaders = ["Fecha", "ID Muestra"];
            models.forEach(m => {
                baseHeaders.push(m.analyticalProperty);
                baseHeaders.push(`${m.analyticalProperty} GH`);
            });

            // 2. Cabeceras de longitudes de onda
            let waveHeaders: string[] = [];
            if (predictions[0].wavelengths && predictions[0].wavelengths.length > 0) {
                waveHeaders = predictions[0].wavelengths.map(w => String(w));
            } else if (predictions[0].rawSpectrum) {
                waveHeaders = predictions[0].rawSpectrum.map((_, i) => `Col_${i+1}`);
            }

            const headers = [...baseHeaders, ...waveHeaders];

            // 3. Construir filas integrando los espectros
            const rows = predictions.map(p => {
                const row: any[] = [timestamp, p.id];
                models.forEach(m => {
                    row.push(p.values[m.id] !== undefined ? p.values[m.id] : '');
                    row.push(p.ghValues[m.id] !== undefined ? p.ghValues[m.id] : '');
                });
                if (p.rawSpectrum) {
                    p.rawSpectrum.forEach(val => row.push(val));
                }
                return row;
            });

            const payload = {
                sheetName: sheetName || 'Resultados',
                headers: headers,
                data: rows
            };

            const response = await fetch(webhookUrl, {
                method: 'POST',
                mode: 'no-cors',
                headers: {
                    'Content-Type': 'text/plain;charset=utf-8',
                },
                body: JSON.stringify(payload)
            });

            alert("✅ Datos enviados exitosamente a Google Sheets.");
            
        } catch (e: any) {
            console.error("Error enviando al Webhook:", e);
            alert(`Error al enviar los datos: ${e.message}`);
        } finally {
            setIsSaving(false);
        }
    };
    
    const modelInputRef = useRef<HTMLInputElement>(null);
    const csvInputRef = useRef<HTMLInputElement>(null);

    const handleModelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        const newModels: SavedModel[] = [];
        let errors = 0;

        const promises = files.map((file: File) => {
            return new Promise<void>((resolve) => {
                const reader = new FileReader();
                reader.onload = (ev) => {
                    try {
                        const json = JSON.parse(ev.target?.result as string);
                        if (!json.metrics || !json.metrics.coefficients || json.metrics.plsIntercept === undefined) {
                            errors++;
                        } else {
                            newModels.push({
                                id: Math.random().toString(36).substring(7),
                                filename: file.name,
                                ...json
                            });
                        }
                    } catch (err) {
                        errors++;
                    }
                    resolve();
                };
                reader.readAsText(file);
            });
        });

        Promise.all(promises).then(() => {
            if (errors > 0) {
                alert(`Hubo un error al leer ${errors} archivo(s). Asegúrese de que son modelos válidos.`);
            }
            if (newModels.length > 0) {
                setModels(prev => [...prev, ...newModels]);
                setPredictions([]);
            }
            if (modelInputRef.current) {
                modelInputRef.current.value = '';
            }
        });
    };

    const handleRemoveModel = (idToRemove: string) => {
        setModels(prev => prev.filter(m => m.id !== idToRemove));
        setPredictions([]);
    };

    const handleDataUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || models.length === 0) return;

        if (file.name.toLowerCase().endsWith('.csv')) {
            parseCSV(file, (results) => {
                if (!results || results.samples.length === 0) {
                    if (csvInputRef.current) csvInputRef.current.value = '';
                    return;
                }

                const newPredictions: {id: string, values: Record<string, number>, ghValues: Record<string, number>, rawSpectrum?: number[], wavelengths?: number[]}[] = [];
                
                for (const sample of results.samples) {
                    const values: Record<string, number> = {};
                    const ghValues: Record<string, number> = {};
                    
                    for (const model of models) {
                        const spectralValues = sample.values.slice(0, model.metrics.coefficients.length);
                        
                        if (spectralValues.length !== model.metrics.coefficients.length || spectralValues.some(v => isNaN(v))) {
                            continue;
                        }

                        const processed = applyPreprocessingLogic(spectralValues, model.preprocessing);
                        const { prediction, gh } = predictPLS(model.metrics, processed);

                        values[model.id] = prediction;
                        ghValues[model.id] = gh;
                    }

                    if (Object.keys(values).length > 0) {
                        newPredictions.push({ 
                            id: String(sample.id), 
                            values, 
                            ghValues,
                            rawSpectrum: sample.values,
                            wavelengths: results.wavelengths
                        });
                    }
                }

                setPredictions(newPredictions);
                
                if (csvInputRef.current) {
                    csvInputRef.current.value = '';
                }
            }, false); // hasAnalyticalProperty = false
        } else {
            const reader = new FileReader();
            reader.onload = (ev) => {
                if (!ev.target?.result) return;
                
                import('../services/fossParser').then(({ parseFOSS }) => {
                    parseFOSS(ev.target!.result as ArrayBuffer, (result) => {
                        if (!result) {
                            alert("No se pudo analizar el archivo espectral. Asegúrese de que es un formato FOSS compatible.");
                            if (csvInputRef.current) csvInputRef.current.value = '';
                            return;
                        }

                        const newPredictions: {id: string, values: Record<string, number>, ghValues: Record<string, number>, rawSpectrum?: number[], wavelengths?: number[]}[] = [];
                        
                        for (const sample of result.samples) {
                            const values: Record<string, number> = {};
                            const ghValues: Record<string, number> = {};
                            
                            for (const model of models) {
                                // Extract the exact number of wavelengths needed by the model
                                // to handle cases where the .nir file contains slightly more/less padded points
                                const spectralValues = sample.values.slice(0, model.metrics.coefficients.length);
                                
                                if (spectralValues.length !== model.metrics.coefficients.length || spectralValues.some(v => isNaN(v))) {
                                    console.warn(`[FOSS] Mismatch for ${sample.id} vs Model ${model.analyticalProperty}. Model needs ${model.metrics.coefficients.length}, got ${spectralValues.length}`);
                                    continue;
                                }

                                const processed = applyPreprocessingLogic(spectralValues, model.preprocessing);
                                const { prediction, gh } = predictPLS(model.metrics, processed);

                                values[model.id] = prediction;
                                ghValues[model.id] = gh;
                            }

                            if (Object.keys(values).length > 0) {
                                newPredictions.push({ 
                                    id: sample.id, 
                                    values, 
                                    ghValues,
                                    rawSpectrum: sample.values,
                                    wavelengths: result.wavelengths
                                });
                            }
                        }

                        setPredictions(newPredictions);
                        if (csvInputRef.current) csvInputRef.current.value = '';
                    }, file.name);
                });
            };
            reader.readAsArrayBuffer(file);
        }
    };

    const handleDownloadCSV = () => {
        const headers = ["ID"];
        models.forEach(m => {
            headers.push(m.analyticalProperty);
            headers.push(`${m.analyticalProperty}_GH`);
        });
        const rows = predictions.map(p => {
            const row = [p.id];
            models.forEach(m => {
                row.push(p.values[m.id] !== undefined ? p.values[m.id].toString() : '');
                row.push(p.ghValues[m.id] !== undefined ? p.ghValues[m.id].toFixed(4) : '');
            });
            return row;
        });
        
        const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "predicciones.csv";
        a.click();
    };

    return (
        <Card>
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                <PredictIcon />
                Predictor Multiparamétrico
            </h2>

            <div className="space-y-6">
                
                {/* Global Webhook Settings */}
                <div className="bg-green-50/50 p-4 rounded-xl border border-green-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <h3 className="text-sm font-bold text-green-800">Conexión Automática a Google Sheets</h3>
                        <p className="text-xs text-green-700">Pega aquí la URL de tu Webhook para sincronizar los resultados y espectros.</p>
                    </div>
                    <div className="flex w-full md:w-auto items-center gap-2">
                        <input 
                            type="url" 
                            placeholder="https://script.google.com/macros/s/.../exec"
                            className="flex-grow md:w-80 text-sm px-3 py-1.5 border border-green-200 rounded focus:outline-none focus:ring-1 focus:ring-green-500 bg-white shadow-sm"
                            value={webhookUrl}
                            onChange={(e) => setWebhookUrl(e.target.value)}
                            onBlur={(e) => handleSaveWebhook(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSaveWebhook(e.currentTarget.value)}
                        />
                        <button 
                            onClick={() => handleSaveWebhook(webhookUrl)}
                            className="px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 text-white rounded font-medium shadow-sm transition-colors"
                        >
                            Guardar
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Panel 1: Modelos */}
                    <div className="p-4 border border-slate-200 rounded-lg bg-slate-50 flex flex-col h-full">
                        <div className="flex-grow">
                            <h3 className="text-sm font-bold text-slate-700 mb-2">1. Cargar Modelos (.json)</h3>
                            <p className="text-[11px] text-slate-500 mb-4">Puede seleccionar varios modelos a la vez.</p>
                            
                            {models.length > 0 && (
                                <div className="space-y-2 mb-4">
                                    {models.map(m => (
                                        <div key={m.id} className="flex items-center justify-between bg-white border border-slate-200 p-2 rounded-md text-xs shadow-sm">
                                            <div className="overflow-hidden">
                                                <div className="font-bold text-brand-700 truncate">{m.analyticalProperty}</div>
                                                <div className="text-slate-500 truncate" title={m.filename}>{m.filename}</div>
                                            </div>
                                            <button 
                                                onClick={() => handleRemoveModel(m.id)}
                                                className="p-1.5 text-slate-400 hover:text-red-500 hover:bg-red-50 rounded transition-colors ml-2 flex-shrink-0"
                                                title="Eliminar modelo"
                                            >
                                                <TrashIcon />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                        
                        <div className="mt-auto">
                            <input type="file" ref={modelInputRef} onChange={handleModelUpload} accept=".json" multiple className="hidden" />
                            <Button variant="secondary" onClick={() => modelInputRef.current?.click()} size="sm" className="w-full">
                                {models.length > 0 ? "Agregar más modelos..." : "Seleccionar Archivos JSON"}
                            </Button>
                        </div>
                    </div>

                    {/* Panel 2: CSV */}
                    <div className={`p-4 border border-slate-200 rounded-lg bg-slate-50 flex flex-col h-full ${models.length === 0 ? 'opacity-50 pointer-events-none' : ''}`}>
                        <div className="flex-grow">
                            <h3 className="text-sm font-bold text-slate-700 mb-2">2. Cargar Muestras (.csv, .nir, .txt)</h3>
                            <p className="text-[11px] text-slate-500 mb-4">Soporta CSV de espectros, o archivos nativos/texto de instrumentos FOSS (.nir, .txt).</p>
                        </div>
                        
                        <div className="mt-auto">
                            <input type="file" ref={csvInputRef} onChange={handleDataUpload} accept=".csv,.nir,.txt" className="hidden" />
                            <Button onClick={() => csvInputRef.current?.click()} size="sm" className="w-full" disabled={models.length === 0}>
                                Predecir con {models.length} modelo{models.length !== 1 ? 's' : ''}
                            </Button>
                        </div>
                    </div>
                </div>

                {predictions.length > 0 && (
                    <div className="animate-fade-in mt-6 pt-6 border-t border-slate-100">
                        <div className="flex justify-between items-end mb-3">
                            <h3 className="text-sm font-bold text-slate-800">Resultados de Predicción ({predictions.length} muestras)</h3>
                            <div className="flex gap-3 items-center flex-wrap justify-end">
                                <Button size="sm" variant="secondary" onClick={handleDownloadCSV}>
                                    Descargar CSV
                                </Button>
                                
                                <div className="flex items-center gap-2">
                                    <select 
                                        value={sheetName} 
                                        onChange={(e) => handleSheetNameChange(e.target.value)}
                                        className="text-sm px-2 py-1 h-8 border border-slate-300 rounded shadow-sm focus:outline-none focus:ring-1 focus:ring-green-500 text-slate-700 bg-white font-medium"
                                        title="Selecciona el instrumento (Pestaña en Google Sheets)"
                                    >
                                        <option value="Viavi">Instrumento: Viavi</option>
                                        <option value="Foss">Instrumento: Foss</option>
                                        <option value="Bruker">Instrumento: Bruker</option>
                                        <option value="MicroNIR">Instrumento: MicroNIR</option>
                                        <option value="Resultados">General</option>
                                    </select>
                                    
                                    <Button 
                                        size="sm" 
                                        onClick={handleSendToWebhook} 
                                        disabled={isSaving}
                                        className="bg-green-600 hover:bg-green-700 text-white border-transparent flex items-center gap-2"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                                        {isSaving ? 'Enviando...' : 'Enviar a Sheets'}
                                    </Button>
                                </div>
                            </div>
                        </div>


                        
                        <div className="max-h-[500px] overflow-x-auto overflow-y-auto custom-scrollbar border border-slate-200 rounded-lg bg-white shadow-inner">
                            <table className="w-full text-sm text-left whitespace-nowrap">
                                <thead className="text-xs text-slate-500 uppercase bg-slate-100 sticky top-0 shadow-sm z-10">
                                    <tr>
                                        <th className="px-6 py-3 font-bold border-b border-slate-200 border-r bg-slate-100 sticky left-0 z-20">ID Muestra</th>
                                        {models.map(m => (
                                            <th key={m.id} className="px-6 py-3 text-right font-bold border-b border-slate-200 min-w-[140px]">
                                                <div className="flex flex-col items-end">
                                                    <span className="text-brand-700">{m.analyticalProperty}</span>
                                                    <span className="text-[9px] font-normal text-slate-400 truncate w-full max-w-[120px]" title={m.filename}>
                                                        {m.filename}
                                                    </span>
                                                </div>
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {predictions.map((p, idx) => (
                                        <tr key={idx} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-3 font-medium text-slate-700 border-r bg-white sticky left-0 z-10">{p.id}</td>
                                            {models.map(m => (
                                                <td key={m.id} className="px-6 py-3 text-right font-mono">
                                                    <div className="text-slate-800 font-bold text-base">
                                                        {p.values[m.id] !== undefined ? p.values[m.id].toFixed(4) : <span className="text-slate-300">-</span>}
                                                    </div>
                                                    {p.ghValues[m.id] !== undefined && p.ghValues[m.id] > 0 && (
                                                        <div className={`text-[11px] ${p.ghValues[m.id] > 3.0 ? 'text-red-600 font-bold' : 'text-slate-500'}`} title="Mahalanobis Distance (GH)">
                                                            GH: {p.ghValues[m.id].toFixed(2)}
                                                            {p.ghValues[m.id] > 3.0 && ' ⚠️'}
                                                        </div>
                                                    )}
                                                </td>
                                            ))}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                )}
            </div>
        </Card>
    );
};
export default ModelPredictor;
