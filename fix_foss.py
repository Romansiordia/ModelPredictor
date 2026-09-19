import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# Replace handleDataUpload
new_handler = """    const handleDataUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file || models.length === 0) return;

        if (file.name.toLowerCase().endsWith('.csv')) {
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

                        const newPredictions: {id: string, values: Record<string, number>}[] = [];
                        
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
                        }

                        setPredictions(newPredictions);
                        if (csvInputRef.current) csvInputRef.current.value = '';
                    }, file.name);
                });
            };
            reader.readAsArrayBuffer(file);
        }
    };"""

content = re.sub(r'    const handleDataUpload = \(e: React.ChangeEvent<HTMLInputElement>\) => \{.*?\n    \};\n', new_handler + '\n', content, flags=re.DOTALL)

# Replace other HTML text
content = content.replace("2. Cargar Muestras (.csv)", "2. Cargar Muestras (.csv, .nir, .txt)")
content = content.replace("El CSV debe tener IDs en la col 1 y datos espectrales a continuación.", "Soporta CSV de espectros, o archivos nativos/texto de instrumentos FOSS (.nir, .txt).")
content = content.replace('accept=".csv"', 'accept=".csv,.nir,.txt"')

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)

