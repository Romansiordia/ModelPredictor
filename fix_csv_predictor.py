import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# Add import
content = content.replace("import { applyPreprocessingLogic } from '../services/chemometrics';", "import { applyPreprocessingLogic } from '../services/chemometrics';\nimport { parseCSV } from '../services/csvParser';")

# Replace Papa.parse block
old_block = """            Papa.parse(file, {
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
            });"""

new_block = """            parseCSV(file, (results) => {
                if (!results || results.samples.length === 0) {
                    if (csvInputRef.current) csvInputRef.current.value = '';
                    return;
                }

                const newPredictions: {id: string, values: Record<string, number>}[] = [];
                
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
                }

                setPredictions(newPredictions);
                
                if (csvInputRef.current) {
                    csvInputRef.current.value = '';
                }
            }, false); // hasAnalyticalProperty = false"""

content = content.replace(old_block, new_block)

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
