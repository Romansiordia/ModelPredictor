import React from 'react';
import Header from './components/Header';
import ModelPredictor from './components/ModelPredictor';

const App: React.FC = () => {
    return (
        <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800 font-sans">
            <Header />
            <main className="flex-grow p-4 lg:p-6">
                <div className="max-w-5xl mx-auto animate-fade-in pt-8">
                    <div className="mb-8 text-center">
                        <h2 className="text-3xl font-bold text-slate-800">Módulo de Predicción</h2>
                        <p className="text-slate-500 mt-3 text-lg">Cargue un modelo previamente entrenado (.json) y un nuevo archivo de espectros (.csv) para calcular propiedades.</p>
                    </div>
                    <ModelPredictor />
                </div>
            </main>
        </div>
    );
};

export default App;
