with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write("""import React, { useState, useRef } from 'react';
import Card from './Card';
import Button from './Button';
import { PreprocessingStep } from '../types';
import { applyPreprocessingLogic } from '../services/chemometrics';

declare var Papa: any;

interface SavedModel {
    id: string;
    filename: string;
    analyticalProperty: string;
    metrics: {
        plsIntercept: number;
        coefficients: number[];
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
    const [predictions, setPredictions] = useState<{id: string, values: Record<string, number>}[]>([]);
    
    const modelInputRef = useRef<HTMLInputElement>(null);
    const csvInputRef = useRef<HTMLInputElement>(null);

    const handleModelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        if (files.length === 0) return;

        const newModels: SavedModel[] = [];
        let errors = 0;

        const promises = files.map(file => {
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

        Papa.parse(file, {
            header: false,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: (results: { data: any[][] }) => {
                const data = results.data;
                if (data.length < 2) return;

                const newPredictions: {id: string, values: Record<string, number>}[] = [];
                
                // Saltar header
                for (let i = 1; i < data.length; i++) {
                    const row = data[i];
                    const id = String(row[0]);
                    
                    const values: Record<string, number> = {};

                    for (const model of models) {
                        const spectralValues = row.slice(1, 1 + model.metrics.coefficients.length);
                        
                        if (spectralValues.length !== model.metrics.coefficients.length || spectralValues.some((v: any) => typeof v !== 'number')) {
                            continue;
                        }

                        const processed = applyPreprocessingLogic(spectralValues as number[], model.preprocessing);

                        let yPred = model.metrics.plsIntercept;
                        for(let k=0; k<processed.length; k++) {
                            yPred += processed[k] * model.metrics.coefficients[k];
                        }

                        values[model.id] = yPred;
                    }

                    if (Object.keys(values).length > 0) {
                        newPredictions.push({ id, values });
                    }
                }

                setPredictions(newPredictions);
                
                if (csvInputRef.current) {
                    csvInputRef.current.value = '';
                }
            }
        });
    };

    const handleDownloadCSV = () => {
        const headers = ["ID", ...models.map(m => m.analyticalProperty)];
        const rows = predictions.map(p => {
            return [p.id, ...models.map(m => p.values[m.id] !== undefined ? p.values[m.id] : '')];
        });
        
        const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\\n');
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
                            <h3 className="text-sm font-bold text-slate-700 mb-2">2. Cargar Muestras (.csv)</h3>
                            <p className="text-[11px] text-slate-500 mb-4">El CSV debe tener IDs en la col 1 y datos espectrales a continuación.</p>
                        </div>
                        
                        <div className="mt-auto">
                            <input type="file" ref={csvInputRef} onChange={handleDataUpload} accept=".csv" className="hidden" />
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
                            <Button size="sm" variant="secondary" onClick={handleDownloadCSV}>
                                Descargar Tabla (.csv)
                            </Button>
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
                                                <td key={m.id} className="px-6 py-3 text-right font-mono text-slate-800 font-bold text-base">
                                                    {p.values[m.id] !== undefined ? p.values[m.id].toFixed(4) : <span className="text-slate-300">-</span>}
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
""")
