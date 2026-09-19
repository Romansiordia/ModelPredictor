import os

with open('src/components/PreprocessingEditor.tsx', 'w') as f:
    f.write("""import React from 'react';
import Card from './Card';
import Button from './Button';
import { PreprocessingStep } from '../types';

interface PreprocessingEditorProps {
    steps: PreprocessingStep[];
    setSteps: React.Dispatch<React.SetStateAction<PreprocessingStep[]>>;
    onVisualize: () => void;
    disabled: boolean;
}

const PREPROCESSING_METHODS = {
    'none': { name: 'Ninguno', params: [] },
    'savgol': {
        name: 'Savitzky-Golay',
        params: [
            { id: 'derivative', name: 'Orden Derivada', type: 'number', default: 1 },
            { id: 'windowSize', name: 'Tamaño Ventana (impar)', type: 'number', default: 5 },
            { id: 'polynomialOrder', name: 'Orden Polinomio', type: 'number', default: 2 },
        ],
    },
    'snv': { name: 'Standard Normal Variate (SNV)', params: [] },
    'msc': { name: 'Multiplicative Scatter Correction (MSC)', params: [] },
    'detrend': { name: 'Detrend', params: [] },
};

const VisualizeIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.14 10.28-9.23-9.23a1.5 1.5 0 0 0-2.12 0l-9.23 9.23a1.5 1.5 0 0 0 0 2.12l9.23 9.23a1.5 1.5 0 0 0 2.12 0l9.23-9.23a1.5 1.5 0 0 0 0-2.12z"></path><path d="M12 22V2"></path></svg>
);
const AddIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
);
const RemoveIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
);

const PreprocessingEditor: React.FC<PreprocessingEditorProps> = ({ steps, setSteps, onVisualize, disabled }) => {
    
    const addStep = () => {
        const newStep: PreprocessingStep = { method: 'savgol', params: {} };
        PREPROCESSING_METHODS['savgol'].params.forEach(p => newStep.params[p.id] = p.default);
        setSteps([...steps, newStep]);
    };

    const removeStep = (index: number) => {
        setSteps(steps.filter((_, i) => i !== index));
    };

    const handleMethodChange = (index: number, newMethod: PreprocessingStep['method']) => {
        const newSteps = [...steps];
        newSteps[index].method = newMethod;
        newSteps[index].params = {};
        (PREPROCESSING_METHODS[newMethod].params as any[]).forEach(p => {
            newSteps[index].params[p.id] = p.default;
        });
        setSteps(newSteps);
    };

    const handleParamChange = (stepIndex: number, paramId: string, value: string) => {
        const newSteps = [...steps];
        newSteps[stepIndex].params[paramId] = parseFloat(value);
        setSteps(newSteps);
    };

    return (
        <Card className="h-full">
            <div className="flex flex-col h-full">
                <div className="flex items-center justify-between gap-3 mb-4 border-b border-slate-200 pb-3">
                    <div className="flex items-center gap-3">
                        <div className="h-7 w-7 bg-brand-50 text-brand-600 border border-brand-100 rounded-lg flex items-center justify-center text-sm font-bold shadow-sm">2</div>
                        <h3 className="text-lg font-bold text-slate-800">Pre-procesamiento</h3>
                    </div>
                    <Button onClick={onVisualize} disabled={disabled} size="sm" variant="primary">
                        <VisualizeIcon />
                        Visualizar
                    </Button>
                </div>
                
                <div className="flex-1 space-y-3 overflow-y-auto custom-scrollbar pr-2 min-h-[8rem]">
                    {steps.map((step, index) => {
                        const methodInfo = PREPROCESSING_METHODS[step.method];
                        return (
                            <div key={index} className="p-3 border border-slate-200 rounded-lg bg-slate-50 shadow-sm">
                                <div className="flex items-center justify-between">
                                    <select
                                        value={step.method}
                                        onChange={(e) => handleMethodChange(index, e.target.value as PreprocessingStep['method'])}
                                        className="w-full bg-white border border-slate-300 text-slate-700 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 shadow-sm"
                                    >
                                        {Object.entries(PREPROCESSING_METHODS).map(([key, value]) => (
                                            <option key={key} value={key}>{value.name}</option>
                                        ))}
                                    </select>
                                    <button onClick={() => removeStep(index)} className="ml-2 p-1 text-slate-400 hover:text-red-500 transition-colors">
                                        <RemoveIcon />
                                    </button>
                                </div>
                                
                                {methodInfo.params.length > 0 && (
                                    <div className="grid grid-cols-3 gap-3 mt-3">
                                        {(methodInfo.params as any[]).map(param => (
                                            <div key={param.id} className="text-xs">
                                                <label htmlFor={`${param.id}-${index}`} className="text-slate-500 font-medium mb-1 block">{param.name}</label>
                                                <input
                                                    type={param.type}
                                                    id={`${param.id}-${index}`}
                                                    value={step.params[param.id] || ''}
                                                    onChange={(e) => handleParamChange(index, param.id, e.target.value)}
                                                    className="w-full bg-white border border-slate-300 text-slate-700 rounded-md px-2 py-1 text-xs focus:outline-none focus:ring-2 focus:ring-brand-500"
                                                />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
                
                <div className="pt-4">
                    <Button variant="secondary" onClick={addStep} disabled={disabled} className="w-full">
                        <AddIcon />Añadir Paso
                    </Button>
                </div>
            </div>
        </Card>
    );
};
export default PreprocessingEditor;
""")

with open('src/components/ModelGenerator.tsx', 'w') as f:
    f.write("""import React, { useState } from 'react';
import Card from './Card';
import Button from './Button';
import { runPlsOptimization } from '../services/chemometrics';
import { Sample, PreprocessingStep } from '../types';

export type ModelParams = 
    | { type: 'pls'; nComponents: number };

interface ModelGeneratorProps {
    onRunModel: (params: ModelParams) => void;
    disabled: boolean;
    activeSamples?: Sample[];
    preprocessingSteps?: PreprocessingStep[];
}

const RunIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="5 3 19 12 5 21 5 3"></polygon>
    </svg>
);

const OptimizeIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>
    </svg>
);

const ModelGenerator: React.FC<ModelGeneratorProps> = ({ onRunModel, disabled, activeSamples, preprocessingSteps }) => {
    const [nComponents, setNComponents] = useState('5');
    const [isOptimizing, setIsOptimizing] = useState(false);
    const [suggestedLV, setSuggestedLV] = useState<number | null>(null);

    const handleRun = () => {
        const lv = parseInt(nComponents);
        if (!isNaN(lv) && lv > 0 && lv <= 20) {
            onRunModel({ type: 'pls', nComponents: lv });
        } else {
            alert('Por favor, introduzca un número válido de variables latentes (1-20).');
        }
    };

    const handleOptimize = async () => {
        if (!activeSamples || !preprocessingSteps || activeSamples.length < 3) {
            alert("Se requieren al menos 3 muestras activas para optimizar.");
            return;
        }
        
        setIsOptimizing(true);
        setSuggestedLV(null);
        
        setTimeout(() => {
            try {
                const maxLVs = Math.min(15, activeSamples.length - 1);
                const results = runPlsOptimization(activeSamples, preprocessingSteps, maxLVs);
                
                if (results.length > 0) {
                    const bestResult = results.reduce((prev, curr) => curr.secv < prev.secv ? curr : prev);
                    setSuggestedLV(bestResult.components);
                    setNComponents(bestResult.components.toString());
                } else {
                    alert("No se pudo determinar un valor óptimo.");
                }
            } catch (e) {
                console.error(e);
                alert("Error durante la optimización.");
            } finally {
                setIsOptimizing(false);
            }
        }, 50);
    };

    return (
        <Card className="h-full">
            <div className="flex flex-col h-full">
                <div className="flex items-center gap-3 mb-4 border-b border-slate-200 pb-3">
                    <div className="h-7 w-7 bg-brand-50 text-brand-600 border border-brand-100 rounded-lg flex items-center justify-center text-sm font-bold shadow-sm">3</div>
                    <h3 className="text-lg font-bold text-slate-800">Generación de Modelo (PLS)</h3>
                </div>
                
                {/* Scrollable Content Area */}
                <div className="flex-1 space-y-4 overflow-y-auto custom-scrollbar pr-2 pb-2 min-h-0">
                    <div className="grid grid-cols-2 gap-4 items-end">
                        <div>
                             <label htmlFor="lv-input" className="block text-xs font-bold text-slate-500 mb-1">Variables Latentes (LV)</label>
                            <input
                                type="number"
                                id="lv-input"
                                value={nComponents}
                                onChange={(e) => setNComponents(e.target.value)}
                                min="1"
                                max="20"
                                className="w-full bg-white border border-slate-300 text-slate-800 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 shadow-sm"
                            />
                        </div>
                        <Button variant="secondary" onClick={handleOptimize} disabled={disabled || isOptimizing} className="h-[38px] text-xs">
                            {isOptimizing ? 'Analizando...' : (
                                <>
                                    <OptimizeIcon /> Analizar Componentes
                                </>
                            )}
                        </Button>
                    </div>
                    
                    {suggestedLV !== null && (
                         <div className="border border-green-200 rounded-lg p-3 bg-green-50 animate-fade-in shadow-inner text-center">
                            <p className="text-sm text-green-800">
                                <span className="font-bold">✨ Sugerencia:</span> El valor óptimo de LVs es <strong>{suggestedLV}</strong>.
                            </p>
                            <p className="text-xs text-green-600 mt-1">
                                El campo de entrada ha sido actualizado.
                            </p>
                        </div>
                    )}
                </div>

                {/* Static Footer with Final Button */}
                <div className="pt-4 border-t border-slate-200">
                    <Button onClick={handleRun} disabled={disabled} className="w-full">
                        <RunIcon />
                        Generar Modelo PLS Final
                    </Button>
                </div>
            </div>
        </Card>
    );
};
export default ModelGenerator;
""")
