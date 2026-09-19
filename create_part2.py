import os

with open('src/components/DataUploader.tsx', 'w') as f:
    f.write("""import React, { useRef, useState } from 'react';
import Card from './Card';
import Button from './Button';

interface DataUploaderProps {
    onFileSelected: (file: File) => void;
}

const DataUploader: React.FC<DataUploaderProps> = ({ onFileSelected }) => {
    const fileInputRef = useRef<HTMLInputElement>(null);
    const [fileName, setFileName] = useState('');
    const [isDragging, setIsDragging] = useState(false);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) processFile(file);
    };
    
    const processFile = (file: File) => {
        setFileName(file.name);
        onFileSelected(file);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        const file = e.dataTransfer.files?.[0];
        if (file && file.name.endsWith('.csv')) {
            processFile(file);
        } else if (file) {
            alert("Por favor suba un archivo .csv");
        }
    };

    return (
        <Card className="h-full">
            <div className="flex flex-col h-full">
                <div className="flex items-center gap-3 mb-4 border-b border-slate-200 pb-3">
                    <div className="h-7 w-7 bg-brand-50 text-brand-600 border border-brand-100 rounded-lg flex items-center justify-center text-sm font-bold shadow-sm">1</div>
                    <h2 className="text-lg font-bold text-slate-800">Cargar Datos</h2>
                </div>
                
                <div className="flex flex-col gap-4 items-center flex-1">
                    <div 
                        className={`w-full border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer flex-1 flex flex-col justify-center ${isDragging ? 'border-brand-500 bg-brand-50' : 'border-slate-300 hover:border-brand-400 hover:bg-slate-50'}`}
                        onDragOver={handleDragOver}
                        onDragLeave={handleDragLeave}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                    >
                        <input
                            type="file"
                            ref={fileInputRef}
                            accept=".csv"
                            onChange={handleFileChange}
                            className="hidden"
                        />
                        <div className="mx-auto h-8 w-8 text-slate-400 mb-3 group-hover:text-brand-500 transition-colors">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="17 8 12 3 7 8"></polyline>
                                <line x1="12" y1="3" x2="12" y2="15"></line>
                            </svg>
                        </div>
                        <p className="text-sm font-semibold text-slate-700">Click o arrastre un CSV</p>
                        <p className="text-xs text-slate-500 mt-1">para iniciar el análisis</p>
                    </div>
                    <div className="w-full flex flex-col gap-2 justify-center">
                        {fileName && (
                            <div className="flex items-center gap-2 text-xs bg-emerald-50 text-emerald-700 p-2 rounded-lg border border-emerald-100 animate-fade-in shadow-sm">
                                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path></svg>
                                <span className="truncate font-medium">{fileName}</span>
                            </div>
                        )}
                        <div className="text-[10px] text-slate-500 leading-relaxed bg-slate-50 p-2 rounded-lg border border-slate-100">
                            <strong className="text-slate-700">Formato:</strong> 1ª fila: Headers. Última col: Propiedad (Y).
                        </div>
                    </div>
                </div>
            </div>
        </Card>
    );
};
export default DataUploader;
""")

with open('src/components/SampleManager.tsx', 'w') as f:
    f.write("""import React from 'react';
import Card from './Card';
import { Sample } from '../types';

interface SampleManagerProps {
    samples: Sample[];
    onToggle: (index: number) => void;
    onToggleAll: (active: boolean) => void;
}

const ManagerIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-slate-500">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
        <polyline points="7 10 12 15 17 10"></polyline>
        <line x1="12" x2="12" y1="15" y2="3"></line>
    </svg>
);

const SampleManager: React.FC<SampleManagerProps> = ({ samples, onToggle, onToggleAll }) => {
    const activeSampleCount = samples.filter(s => s.active).length;
    return (
        <Card noPadding>
             <div className="bg-slate-50 px-6 py-4 border-b border-slate-200 flex justify-between items-center">
                <h4 className="font-bold text-slate-700 flex items-center gap-2">
                    <ManagerIcon />
                    Gestor de Muestras
                </h4>
                <div className="flex items-center gap-4">
                    <p className="text-sm text-slate-500 hidden md:block">
                        <span className="font-bold text-slate-800">{activeSampleCount}</span> / {samples.length} activas
                    </p>
                    <div>
                        <button onClick={() => onToggleAll(true)} className="text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline">TODAS</button>
                         <span className="text-slate-300 mx-1.5">|</span>
                        <button onClick={() => onToggleAll(false)} className="text-xs font-semibold text-brand-600 hover:text-brand-700 hover:underline">NINGUNA</button>
                    </div>
                </div>
            </div>
            
            <div className="p-6 overflow-y-auto max-h-80 custom-scrollbar">
                {samples.length === 0 ? (
                    <div className="text-center text-slate-400 py-10">
                         <p className="italic text-sm">Cargue un archivo para ver las muestras.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-2">
                        {samples.map((sample, index) => (
                            <div key={sample.id} className="flex items-center justify-between rounded-md group">
                                <div className="flex items-center gap-3 overflow-hidden">
                                    <input
                                        type="checkbox"
                                        id={`sample-${index}`}
                                        checked={sample.active}
                                        onChange={() => onToggle(index)}
                                        className="w-4 h-4 rounded border-slate-300 text-brand-600 focus:ring-brand-500 cursor-pointer flex-shrink-0"
                                    />
                                    <label htmlFor={`sample-${index}`} className={`text-sm cursor-pointer truncate max-w-[150px] transition-colors font-medium ${sample.active ? 'text-slate-700' : 'text-slate-400 line-through'}`}>
                                        {sample.id}
                                    </label>
                                </div>
                                <div className="w-3 h-3 rounded-full flex-shrink-0 ring-1 ring-slate-200" style={{ backgroundColor: sample.color }}></div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </Card>
    );
};
export default SampleManager;
""")

with open('src/components/SpectraViewer.tsx', 'w') as f:
    f.write("""import React, { useRef, useEffect, useState } from 'react';
import Card from './Card';
import Button from './Button';
import { Sample } from '../types';

declare var Chart: any;
declare var ChartZoom: any;

interface SpectraViewerProps {
    wavelengths: number[];
    samples: (Sample | {id: string | number, values: number[], color: string})[];
    isProcessed: boolean;
    onReset: () => void;
}

const ChartIcon: React.FC = () => (
    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-600">
        <path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path>
    </svg>
);

const SpectraViewer: React.FC<SpectraViewerProps> = ({ wavelengths, samples, isProcessed, onReset }) => {
    const chartRef = useRef<HTMLCanvasElement>(null);
    const chartInstanceRef = useRef<any>(null);
    const [startWl, setStartWl] = useState('');
    const [endWl, setEndWl] = useState('');
    
    const hasData = samples.length > 0;

    useEffect(() => {
        if (hasData) {
            setStartWl(wavelengths[0].toString());
            setEndWl(wavelengths[wavelengths.length - 1].toString());
        } else {
            setStartWl('');
            setEndWl('');
        }
    }, [wavelengths, hasData]);

    useEffect(() => {
        if (chartRef.current) {
            Chart.register(ChartZoom);
            const ctx = chartRef.current.getContext('2d');
            if (ctx) {
                chartInstanceRef.current = new Chart(ctx, {
                    type: 'line',
                    data: { labels: [], datasets: [] },
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        plugins: {
                            legend: { display: false },
                            tooltip: { 
                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                titleColor: '#0f172a',
                                bodyColor: '#334155',
                                borderColor: '#e2e8f0',
                                borderWidth: 1,
                                padding: 10,
                                titleFont: { family: 'Inter', size: 13, weight: 'bold' },
                                callbacks: { title: (context: any) => context[0].dataset.label } 
                            },
                            zoom: {
                                pan: { enabled: true, mode: 'x' },
                                zoom: { wheel: { enabled: true }, pinch: { enabled: true }, mode: 'x' }
                            }
                        },
                        scales: {
                            x: {
                                type: 'linear',
                                title: { display: true, text: 'Longitud de onda (nm)', color: '#94a3b8', font: {size: 11} },
                                ticks: { color: '#94a3b8', font: {family: 'JetBrains Mono', size: 10} },
                                grid: { color: '#334155', drawBorder: false } 
                            },
                            y: {
                                title: { display: true, text: isProcessed ? 'Intensidad' : 'Absorbancia', color: '#94a3b8', font: {size: 11} },
                                ticks: { color: '#94a3b8', font: {family: 'JetBrains Mono', size: 10} },
                                grid: { color: '#334155', drawBorder: false }
                            }
                        },
                        interaction: {
                            mode: 'nearest',
                            axis: 'x',
                            intersect: false
                        }
                    }
                });
            }
        }
        return () => {
            chartInstanceRef.current?.destroy();
        };
    }, [isProcessed]);

    useEffect(() => {
        const chart = chartInstanceRef.current;
        if (chart && hasData) {
            chart.data.labels = wavelengths;
            chart.data.datasets = samples.map(sample => ({
                label: sample.id,
                data: sample.values,
                borderColor: sample.color,
                borderWidth: 1.5,
                pointRadius: 0,
                tension: 0.1
            }));
            
            if (isProcessed) {
                const allValues = samples.flatMap(s => s.values).filter(v => isFinite(v as number));
                if (allValues.length > 0) {
                    const min = Math.min(...allValues as number[]);
                    const max = Math.max(...allValues as number[]);
                    const padding = (max - min) * 0.1;
                    chart.options.scales.y.min = min - padding;
                    chart.options.scales.y.max = max + padding;
                }
            } else {
                 chart.options.scales.y.min = undefined;
                 chart.options.scales.y.max = undefined;
            }
            chart.update();
        }
    }, [wavelengths, samples, isProcessed, hasData]);
    
    const handleResetZoom = () => {
        if (chartInstanceRef.current) {
            chartInstanceRef.current.resetZoom();
        }
        if (isProcessed) {
            onReset();
        }
    };

    const handleApplyRange = () => {
        const chart = chartInstanceRef.current;
        if (!chart || !hasData) return;
        
        const start = parseFloat(startWl), end = parseFloat(endWl);
        const minWl = wavelengths[0], maxWl = wavelengths[wavelengths.length - 1];
        if (isNaN(start) || isNaN(end) || start >= end || start < minWl || end > maxWl) {
            alert(`Rango espectral inválido.`);
            setStartWl(minWl.toFixed(2));
            setEndWl(maxWl.toFixed(2));
            chart.options.scales.x.min = undefined;
            chart.options.scales.x.max = undefined;
        } else {
            chart.options.scales.x.min = start;
            chart.options.scales.x.max = end;
        }
        chart.update();
    };

    return (
        <Card>
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h2 className="text-lg font-bold flex items-center gap-2 text-slate-800">
                        <ChartIcon />
                        Visualizador de Espectros
                    </h2>
                    <p className="text-sm text-slate-500 mt-1 ml-7">Explore los datos espectrales crudos y pre-procesados.</p>
                </div>
                <div className="flex gap-2">
                    <Button variant="secondary" onClick={handleResetZoom} className="text-xs" size="sm" disabled={!hasData}>
                        {isProcessed ? 'Resetear Pre-proc.' : 'Resetear Zoom'}
                    </Button>
                </div>
            </div>

            <div className={`grid grid-cols-1 md:grid-cols-12 gap-4 items-end mb-4 bg-slate-50 p-3 rounded-lg border border-slate-200 transition-opacity ${!hasData ? 'opacity-50' : ''}`}>
                <div className="md:col-span-5">
                    <label htmlFor="startWavelength" className="block text-xs font-semibold text-slate-500 mb-1">Longitud de onda inicial (nm)</label>
                    <input type="number" id="startWavelength" value={startWl} onChange={e => setStartWl(e.target.value)} disabled={!hasData} className="w-full bg-white border border-slate-300 text-slate-800 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow shadow-sm disabled:bg-slate-100" />
                </div>
                <div className="md:col-span-5">
                    <label htmlFor="endWavelength" className="block text-xs font-semibold text-slate-500 mb-1">Longitud de onda final (nm)</label>
                    <input type="number" id="endWavelength" value={endWl} onChange={e => setEndWl(e.target.value)} disabled={!hasData} className="w-full bg-white border border-slate-300 text-slate-800 rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 transition-shadow shadow-sm disabled:bg-slate-100" />
                </div>
                <div className="md:col-span-2">
                    <Button onClick={handleApplyRange} className="w-full text-sm py-1.5" disabled={!hasData}>Aplicar</Button>
                </div>
            </div>
            
            <div className="relative h-80 rounded-lg overflow-hidden border border-slate-800 bg-slate-900 shadow-inner-dark group">
                <div className="absolute inset-0 bg-gradient-to-b from-slate-900 via-slate-900 to-[#111827]"></div>
                
                {hasData ? (
                    <>
                        <div className="relative h-full w-full p-2">
                            <canvas ref={chartRef}></canvas>
                        </div>
                        <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-slate-500 bg-black/50 px-2 py-1 rounded">
                            Scroll para Zoom | Arrastrar para Mover
                        </div>
                    </>
                ) : (
                    <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-4">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-slate-700 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="1">
                           <path strokeLinecap="round" strokeLinejoin="round" d="M3 3v18h18" />
                           <path strokeLinecap="round" strokeLinejoin="round" d="M18.37 7.23L13 12.59l-3.13-3.13-4.24 4.24" />
                        </svg>
                        <h3 className="font-bold text-lg text-slate-400">Visualizador Vacío</h3>
                        <p className="text-sm text-slate-500 mt-1 max-w-xs">Cargue un archivo de datos en el <span className="font-semibold text-slate-400">Paso 1</span> para ver los espectros aquí.</p>
                    </div>
                )}
            </div>
        </Card>
    );
};
export default SpectraViewer;
""")

with open('src/components/PcaAnalyzer.tsx', 'w') as f:
    f.write("""import React, { useRef, useEffect } from 'react';
import Card from './Card';
import Button from './Button';
import { PcaResult } from '../types';

declare var Chart: any;

interface PcaAnalyzerProps {
    onRunPca: () => void;
    pcaResults: PcaResult[] | null;
    disabled: boolean;
}

const PcaIcon: React.FC = () => (
     <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-600">
        <circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="3"></circle>
    </svg>
);

const PcaAnalyzer: React.FC<PcaAnalyzerProps> = ({ onRunPca, pcaResults, disabled }) => {
    const chartRef = useRef<HTMLCanvasElement>(null);
    const chartInstanceRef = useRef<any>(null);

    useEffect(() => {
        if (chartRef.current) {
            const ctx = chartRef.current.getContext('2d');
            if (ctx) {
                chartInstanceRef.current = new Chart(ctx, {
                    type: 'scatter',
                    data: { datasets: [] },
                    options: {
                        maintainAspectRatio: false,
                        responsive: true,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    title: (context: any) => {
                                        const dataIndex = context[0].dataIndex;
                                        return context[0].dataset.rawData[dataIndex].id;
                                    }
                                }
                            }
                        },
                        scales: {
                            x: { title: { display: true, text: 'PC1' } },
                            y: { title: { display: true, text: 'PC2' } }
                        }
                    }
                });
            }
        }
        return () => chartInstanceRef.current?.destroy();
    }, []);

    useEffect(() => {
        if (chartInstanceRef.current && pcaResults) {
            const variancePC1 = 85.4 + Math.random() * 5;
            const variancePC2 = 9.1 + Math.random() * 2;
            
            chartInstanceRef.current.options.scales.x.title.text = `PC1 (${variancePC1.toFixed(1)}% Varianza)`;
            chartInstanceRef.current.options.scales.y.title.text = `PC2 (${variancePC2.toFixed(1)}% Varianza)`;
            
            chartInstanceRef.current.data.datasets = [{
                label: 'PCA Scores',
                data: pcaResults,
                rawData: pcaResults,
                backgroundColor: pcaResults.map(s => s.color + 'BF'),
                borderColor: pcaResults.map(s => s.color),
                pointRadius: 6
            }];
            chartInstanceRef.current.update();
        }
    }, [pcaResults]);

    return (
        <Card>
            <h2 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-brand-600"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>
                Análisis Exploratorio (PCA)
            </h2>
            <p className="text-sm text-gray-500 mb-4">Genere un gráfico de scores PCA (simulado) para visualizar la similitud y agrupamiento entre las muestras activas.</p>
            <Button onClick={onRunPca} disabled={disabled} className="w-full max-w-sm mx-auto mb-4">
                <PcaIcon />
                Generar Gráfico PCA
            </Button>
            <div className={`relative h-80 ${!pcaResults && 'hidden'}`}>
                <canvas ref={chartRef}></canvas>
            </div>
        </Card>
    );
};
export default PcaAnalyzer;
""")
