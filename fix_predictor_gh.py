import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    "import { applyPreprocessingLogic } from '../services/chemometrics';",
    "import { applyPreprocessingLogic, predictPLS } from '../services/chemometrics';"
)

# 2. Update SavedModel interface to include xMean, W, T_inv_var
saved_model_old = """interface SavedModel {
    id: string;
    filename: string;
    analyticalProperty: string;
    metrics: {
        plsIntercept: number;
        coefficients: number[];
    };
    preprocessing: PreprocessingStep[];
}"""
saved_model_new = """interface SavedModel {
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
}"""
content = content.replace(saved_model_old, saved_model_new)

# 3. Update predictions state
content = content.replace(
    "const [predictions, setPredictions] = useState<{id: string, values: Record<string, number>}[]>([]);",
    "const [predictions, setPredictions] = useState<{id: string, values: Record<string, number>, ghValues: Record<string, number>}[]>([]);"
)

# 4. Update parseCSV logic block
parse_csv_old = """                const newPredictions: {id: string, values: Record<string, number>}[] = [];
                
                for (const sample of results.samples) {
                    const values: Record<string, number> = {};
                    
                    for (const model of models) {
                        // Tomamos tantos puntos del inicio como espere el modelo
                        const spectralValues = sample.values.slice(0, model.metrics.coefficients.length);
                        
                        if (spectralValues.length !== model.metrics.coefficients.length || spectralValues.some(v => isNaN(v))) {
                            continue;
                        }

                        const processed = applyPreprocessingLogic(spectralValues, model.preprocessing);

                        let yPred = model.metrics.plsIntercept;
                        for(let k=0; k<processed.length; k++) {
                            yPred += processed[k] * model.metrics.coefficients[k];
                        }

                        values[model.id] = yPred;
                    }

                    if (Object.keys(values).length > 0) {
                        newPredictions.push({ id: String(sample.id), values });
                    }
                }"""

parse_csv_new = """                const newPredictions: {id: string, values: Record<string, number>, ghValues: Record<string, number>}[] = [];
                
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
                        newPredictions.push({ id: String(sample.id), values, ghValues });
                    }
                }"""
content = content.replace(parse_csv_old, parse_csv_new)

# 5. Update FOSS parser logic block
parse_foss_old = """                        const newPredictions: {id: string, values: Record<string, number>}[] = [];
                        
                        for (const sample of result.samples) {
                            const values: Record<string, number> = {};
                            
                            for (const model of models) {
                                if (sample.values.length !== model.metrics.coefficients.length) {
                                    continue;
                                }

                                const processed = applyPreprocessingLogic(sample.values, model.preprocessing);

                                let yPred = model.metrics.plsIntercept;
                                for(let k=0; k<processed.length; k++) {
                                    yPred += processed[k] * model.metrics.coefficients[k];
                                }

                                values[model.id] = yPred;
                            }

                            if (Object.keys(values).length > 0) {
                                newPredictions.push({ id: sample.id, values });
                            }
                        }"""
parse_foss_new = """                        const newPredictions: {id: string, values: Record<string, number>, ghValues: Record<string, number>}[] = [];
                        
                        for (const sample of result.samples) {
                            const values: Record<string, number> = {};
                            const ghValues: Record<string, number> = {};
                            
                            for (const model of models) {
                                if (sample.values.length !== model.metrics.coefficients.length) {
                                    continue;
                                }

                                const processed = applyPreprocessingLogic(sample.values, model.preprocessing);
                                const { prediction, gh } = predictPLS(model.metrics, processed);

                                values[model.id] = prediction;
                                ghValues[model.id] = gh;
                            }

                            if (Object.keys(values).length > 0) {
                                newPredictions.push({ id: sample.id, values, ghValues });
                            }
                        }"""
content = content.replace(parse_foss_old, parse_foss_new)

# 6. Update handleDownloadCSV
csv_download_old = """    const handleDownloadCSV = () => {
        const headers = ["ID", ...models.map(m => m.analyticalProperty)];
        const rows = predictions.map(p => {
            return [p.id, ...models.map(m => p.values[m.id] !== undefined ? p.values[m.id] : '')];
        });"""
csv_download_new = """    const handleDownloadCSV = () => {
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
        });"""
content = content.replace(csv_download_old, csv_download_new)

# 7. Update Table rendering
table_td_old = """                                            {models.map(m => (
                                                <td key={m.id} className="px-6 py-3 text-right font-mono text-slate-800 font-bold text-base">
                                                    {p.values[m.id] !== undefined ? p.values[m.id].toFixed(4) : <span className="text-slate-300">-</span>}
                                                </td>
                                            ))}"""

table_td_new = """                                            {models.map(m => (
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
                                            ))}"""
content = content.replace(table_td_old, table_td_new)

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
