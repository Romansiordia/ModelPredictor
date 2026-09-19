import os

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write("""import React, { useState, useRef } from 'react';
import Card from './Card';
import Button from './Button';
import { PreprocessingStep } from '../types';
import { applyPreprocessingLogic } from '../services/chemometrics';

declare var Papa: any;

interface SavedModel {
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

const ModelPredictor: React.FC = () => {
    const [model, setModel] = useState<SavedModel | null>(null);
    const [predictions, setPredictions] = useState<{id: string, value: number}[]>([]);
    
    const modelInputRef = useRef<HTMLInputElement>(null);
    const csvInputRef = useRef<HTMLInputElement>(null);

    const handleModelUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (ev) => {
            try {
                const json = JSON.parse(ev.target?.result as string);
                if (!json.metrics || !json.metrics.coefficients || json.metrics.plsIntercept === undefined) {
                    alert("El archivo JSON no parece ser un modelo válido de Spectra Pro.");
                    return;
                }
                setModel(json);
                setPredictions([]);
            } catch (err) {
                alert("Error al leer el archivo JSON.");
            }
        };
        reader.readAsText(file);
    };

    const handleDataUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || !model) return;

        Papa.parse(file, {
            header: false,
            dynamicTyping: true,
            skipEmptyLines: true,
            complete: (results: { data: any[][] }) => {
                const data = results.data;
                if (data.length < 2) return;

                // Asumimos formato: ID, w1, w2, ... (sin columna de propiedad al final necesariamente)
                // Pero debemos alinear las columnas. Por simplicidad, asumimos que el CSV de entrada
                // tiene el MISMO formato espectral que el de entrenamiento.
                
                const newPredictions: {id: string, value: number}[] = [];
                
                // Saltar header
                for (let i = 1; i < data.length; i++) {
                    const row = data[i];
                    const id = String(row[0]);

                    // Tomar valores espectrales. Asumimos que son todas las columnas excepto la primera (ID)
                    // Ojo: Si el CSV tiene columna de propiedad al final, el usuario debe saberlo.
                    // Aquí tomaremos tantas columnas como coeficientes tenga el modelo.
                    
                    const spectralValues = row.slice(1, 1 + model.metrics.coefficients.length);
                    
                    if (spectralValues.length !== model.metrics.coefficients.length) {
                        console.warn(`Muestra ${id} tiene longitud incorrecta. Se esperaban ${model.metrics.coefficients.length} puntos.`);
                        continue;
                    }
                    
                    if (spectralValues.some((v: any) => typeof v !== 'number')) continue;

                    // 1. Aplicar Pre-procesamiento guardado en el modelo
                    const processed = applyPreprocessingLogic(spectralValues as number[], model.preprocessing);

                    // 2. Aplicar Ecuación de Regresión: Y = B0 + X*B
                    let yPred = model.metrics.plsIntercept;
                    for(let k=0; k<processed.length; k++) {
                        yPred += processed[k] * model.metrics.coefficients[k];
                    }

                    newPredictions.push({ id, value: yPred });
                }

                setPredictions(newPredictions);
            }
        });
    };

    return (
        <Card>
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                <PredictIcon />
                Predictor (Nuevas Muestras)
            </h2>

            <div className="space-y-6">
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 border border-slate-200 rounded-lg bg-slate-50">
                        <h3 className="text-sm font-bold text-slate-700 mb-2">1. Cargar Modelo (.json)</h3>
                        <input type="file" ref={modelInputRef} onChange={handleModelUpload} accept=".json" className="hidden" />
                        <Button variant="secondary" onClick={() => modelInputRef.current?.click()} size="sm" className="w-full">
                            {model ? "Modelo Cargado" : "Seleccionar Archivo JSON"}
                        </Button>
                        {model && (
                            <div className="mt-2 text-xs text-green-600">
                                <div><strong>Propiedad:</strong> {model.analyticalProperty}</div>
                                <div><strong>Pre-proc:</strong> {model.preprocessing.length > 0 ? model.preprocessing.map(p => p.method).join(', ') : 'Ninguno'}</div>
                            </div>
                        )}
                    </div>

                    <div className={`p-4 border border-slate-200 rounded-lg bg-slate-50 ${!model ? 'opacity-50 pointer-events-none' : ''}`}>
                        <h3 className="text-sm font-bold text-slate-700 mb-2">2. Cargar Muestras (.csv)</h3>
                        <input type="file" ref={csvInputRef} onChange={handleDataUpload} accept=".csv" className="hidden" />
                        <Button onClick={() => csvInputRef.current?.click()} size="sm" className="w-full" disabled={!model}>
                            Predecir CSV
                        </Button>
                        <p className="text-[10px] text-slate-500 mt-2">El CSV debe tener IDs en la col 1 y datos espectrales a continuación.</p>
                    </div>
                </div>

                {predictions.length > 0 && (
                    <div className="animate-fade-in">
                        <h3 className="text-sm font-bold text-slate-800 mb-3">Resultados de Predicción</h3>
                        {/* Increased max-height from max-h-60 to max-h-[500px] for better visibility */}
                        <div className="max-h-[500px] overflow-y-auto custom-scrollbar border border-slate-200 rounded-lg bg-white shadow-inner">
                            <table className="w-full text-sm text-left">
                                <thead className="text-xs text-slate-500 uppercase bg-slate-100 sticky top-0 shadow-sm z-10">
                                    <tr>
                                        <th className="px-6 py-3 font-bold border-b border-slate-200">ID Muestra</th>
                                        <th className="px-6 py-3 text-right font-bold border-b border-slate-200">Valor Predicho</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {predictions.map((p, idx) => (
                                        <tr key={idx} className="hover:bg-slate-50 transition-colors">
                                            <td className="px-6 py-3 font-medium text-slate-700">{p.id}</td>
                                            <td className="px-6 py-3 text-right font-mono text-brand-600 font-bold text-base">{p.value.toFixed(4)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="mt-4 flex justify-end">
                             <Button size="sm" variant="secondary" onClick={() => {
                                 const csv = "ID,Predicted_Value\\n" + predictions.map(p => `${p.id},${p.value}`).join('\\n');
                                 const blob = new Blob([csv], { type: 'text/csv' });
                                 const url = URL.createObjectURL(blob);
                                 const a = document.createElement('a');
                                 a.href = url;
                                 a.download = "predicciones.csv";
                                 a.click();
                             }}>Descargar Tabla</Button>
                        </div>
                    </div>
                )}
            </div>
        </Card>
    );
};
export default ModelPredictor;
""")

with open('src/App.tsx', 'w') as f:
    f.write("""import React, { useState, useCallback } from 'react';
import { Sample, PreprocessingStep, ModelResults } from './types';
import { parseCSV } from './services/csvParser';
import { applyPreprocessingLogic, runPlsAnalysis } from './services/chemometrics';
import Header from './components/Header';
import Loader from './components/Loader';
import DataUploader from './components/DataUploader';
import SampleManager from './components/SampleManager';
import SpectraViewer from './components/SpectraViewer';
import PreprocessingEditor from './components/PreprocessingEditor';
import ModelGenerator, { ModelParams } from './components/ModelGenerator';
import ResultsViewer from './components/ResultsViewer';
import ModelPredictor from './components/ModelPredictor';
import Card from './components/Card';

type AppView = 'calibration' | 'prediction';

const App: React.FC = () => {
    const [currentView, setCurrentView] = useState<AppView>('calibration');
    const [loadingMessage, setLoadingMessage] = useState<string | null>(null);
    const [wavelengths, setWavelengths] = useState<number[]>([]);
    const [samples, setSamples] = useState<Sample[]>([]);
    const [analyticalProperty, setAnalyticalProperty] = useState<string>('Propiedad');
    const [preprocessingSteps, setPreprocessingSteps] = useState<PreprocessingStep[]>([]);
    const [modelResults, setModelResults] = useState<ModelResults | null>(null);
    const [processedSpectra, setProcessedSpectra] = useState<{ id: string | number; values: number[] }[] | null>(null);

    const handleDataLoaded = (data: { wavelengths: number[]; samples: Sample[]; analyticalProperty: string }) => {
        setWavelengths(data.wavelengths);
        setSamples(data.samples);
        setAnalyticalProperty(data.analyticalProperty);
        setModelResults(null);
        setProcessedSpectra(null);
        setPreprocessingSteps([]);
    };

    const handleFileSelected = (file: File) => {
        setLoadingMessage('Cargando datos...');
        parseCSV(file, (results) => {
            handleDataLoaded(results);
            setLoadingMessage(null);
        });
    };

    const handleToggleSample = (index: number) => {
        setSamples(prev => prev.map((s, i) => i === index ? { ...s, active: !s.active } : s));
    };

    const handleToggleAllSamples = (active: boolean) => {
        setSamples(prev => prev.map(s => ({ ...s, active })));
    };

    const handleVisualizePreprocessing = () => {
        const activeSamples = samples.filter(s => s.active);
        if (activeSamples.length === 0) return;
        const processed = activeSamples.map(sample => ({
            ...sample,
            values: applyPreprocessingLogic(sample.values, preprocessingSteps)
        }));
        setProcessedSpectra(processed);
    };

    const handleResetVisualization = useCallback(() => {
        setProcessedSpectra(null);
    }, []);

    const handleRunModel = async (params: ModelParams) => {
        const activeSamples = samples.filter(s => s.active);
        if (activeSamples.length < 3) {
            alert('Se necesitan al menos 3 muestras activas para generar el modelo PLS y validación cruzada.');
            return;
        }
        setLoadingMessage(`Generando modelo ${params.type.toUpperCase()}...`);
        
        setTimeout(() => {
            try {
                const results = runPlsAnalysis(activeSamples, preprocessingSteps, params.nComponents);
                setModelResults(results);
            } catch (error) {
                console.error(`Error during ${params.type} run:`, error);
                const errorMessage = error instanceof Error ? error.message : "Ocurrió un error desconocido.";
                alert(`Ocurrió un error al generar el modelo: ${errorMessage}`);
            } finally {
                setLoadingMessage(null);
            }
        }, 100);
    };
    
    const handleDeactivateOutliers = (outlierIds: (string|number)[]) => {
         setSamples(prev => prev.map(s => outlierIds.includes(s.id) ? { ...s, active: false } : s));
         if (modelResults) {
             setTimeout(() => {
                const params: ModelParams = { type: 'pls', nComponents: modelResults.nComponents };
                handleRunModel(params);
             }, 100);
         }
    }
    
    const activeSamples = samples.filter(s => s.active);
    const spectraToDisplay = processedSpectra ? processedSpectra.map(p => {
        const originalSample = samples.find(s => s.id === p.id);
        return { ...p, color: originalSample?.color || '#000000' };
    }) : activeSamples;

    return (
        <>
            {loadingMessage && <Loader message={loadingMessage} />}
            <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800 font-sans">
                <Header />
                
                {/* Navigation Tabs */}
                <div className="bg-white border-b border-slate-200 sticky top-16 z-20">
                    <div className="max-w-[1920px] mx-auto px-4 lg:px-6 flex gap-8">
                        <button 
                            onClick={() => setCurrentView('calibration')}
                            className={`py-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${currentView === 'calibration' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h5"/><path d="M17 12h5"/><path d="M7 12a5 5 0 0 1 5-5 5 5 0 0 1 5 5 5 5 0 0 1-5 5 5 5 0 0 1-5-5Z"/></svg>
                            1. Entrenamiento & Calibración
                        </button>
                        <button 
                            onClick={() => setCurrentView('prediction')}
                            className={`py-4 text-sm font-semibold border-b-2 transition-colors flex items-center gap-2 ${currentView === 'prediction' ? 'border-brand-600 text-brand-600' : 'border-transparent text-slate-500 hover:text-slate-800'}`}
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                            2. Predicción de Nuevas Muestras
                        </button>
                    </div>
                </div>

                <main className="flex-grow p-4 lg:p-6">
                    
                    {/* VISTA DE CALIBRACIÓN */}
                    {currentView === 'calibration' && (
                        <div className="flex flex-col gap-6 animate-fade-in">
                            {/* Main Workspace: Controls & Visualization */}
                            <div className="grid grid-cols-1 lg:grid-cols-7 gap-6">
                                {/* Left Column: Workflow Steps 1, 2 & 3 */}
                                <div className="flex flex-col gap-6 lg:col-span-2">
                                    <DataUploader onFileSelected={handleFileSelected} />
                                    <PreprocessingEditor
                                        steps={preprocessingSteps}
                                        setSteps={setPreprocessingSteps}
                                        onVisualize={handleVisualizePreprocessing}
                                        disabled={activeSamples.length === 0}
                                    />
                                    <ModelGenerator 
                                        onRunModel={handleRunModel} 
                                        disabled={activeSamples.length < 3}
                                        activeSamples={activeSamples}
                                        preprocessingSteps={preprocessingSteps}
                                    />
                                </div>

                                {/* Right Column: Data Interaction */}
                                <div className="flex flex-col gap-6 lg:col-span-5">
                                    <SpectraViewer
                                        wavelengths={wavelengths}
                                        samples={spectraToDisplay}
                                        isProcessed={!!processedSpectra}
                                        onReset={handleResetVisualization}
                                    />
                                    <SampleManager
                                        samples={samples}
                                        onToggle={handleToggleSample}
                                        onToggleAll={handleToggleAllSamples}
                                    />

                                    {/* Final Step: Results (Now inside the main grid) */}
                                    <div>
                                        <div className="flex items-center gap-3 mb-4">
                                            <div className="h-7 w-7 bg-slate-100 text-slate-600 border border-slate-200 rounded-lg flex items-center justify-center text-sm font-bold shadow-sm">4</div>
                                            <h2 className="text-lg font-bold text-slate-800">Análisis de Resultados del Modelo</h2>
                                        </div>
                                        {modelResults ? (
                                            <ResultsViewer 
                                                results={modelResults}
                                                propertyName={analyticalProperty}
                                                preprocessingSteps={preprocessingSteps}
                                                activeSamples={activeSamples.map(s => s.id)}
                                                onDeactivateOutliers={handleDeactivateOutliers}
                                                wavelengths={wavelengths}
                                            />
                                        ) : (
                                            <Card>
                                                <div className="flex flex-col items-center justify-center h-64 text-slate-400 bg-slate-50/50 rounded-lg border-2 border-dashed border-slate-300">
                                                    <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                                    </svg>
                                                    <p className="font-semibold text-slate-600 text-lg">Resultados del Modelo</p>
                                                    <p className="text-sm text-slate-500 mt-1">Genere un modelo en el paso 3 para ver el análisis estadístico aquí.</p>
                                                </div>
                                            </Card>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* VISTA DE PREDICCIÓN */}
                    {currentView === 'prediction' && (
                        <div className="max-w-5xl mx-auto animate-fade-in">
                            <div className="mb-6 text-center">
                                <h2 className="text-2xl font-bold text-slate-800">Módulo de Predicción Independiente</h2>
                                <p className="text-slate-500 mt-2">Cargue un modelo previamente entrenado (.json) y un nuevo archivo de espectros (.csv) para calcular propiedades.</p>
                            </div>
                            <ModelPredictor />
                        </div>
                    )}
                </main>
            </div>
        </>
    );
};
export default App;
""")
