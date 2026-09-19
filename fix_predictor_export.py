import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# 1. Update the state interface
state_old = "const [predictions, setPredictions] = useState<{id: string, values: Record<string, number>, ghValues: Record<string, number>}[]>([]);"
state_new = "const [predictions, setPredictions] = useState<{id: string, values: Record<string, number>, ghValues: Record<string, number>, rawSpectrum?: number[], wavelengths?: number[]}[]>([]);"
content = content.replace(state_old, state_new)

# 2. Update parseCSV push logic
parse_csv_old = """                    if (Object.keys(values).length > 0) {
                        newPredictions.push({ id: String(sample.id), values, ghValues });
                    }"""
parse_csv_new = """                    if (Object.keys(values).length > 0) {
                        newPredictions.push({ 
                            id: String(sample.id), 
                            values, 
                            ghValues,
                            rawSpectrum: sample.values,
                            wavelengths: results.wavelengths
                        });
                    }"""
content = content.replace(parse_csv_old, parse_csv_new)

# 3. Update FOSS parser push logic
parse_foss_old = """                            if (Object.keys(values).length > 0) {
                                newPredictions.push({ id: sample.id, values, ghValues });
                            }"""
parse_foss_new = """                            if (Object.keys(values).length > 0) {
                                newPredictions.push({ 
                                    id: sample.id, 
                                    values, 
                                    ghValues,
                                    rawSpectrum: sample.values,
                                    wavelengths: result.wavelengths
                                });
                            }"""
content = content.replace(parse_foss_old, parse_foss_new)


# 4. Update Webhook payload generator and UI
webhook_old = """    const handleSendToWebhook = async () => {
        if (!webhookUrl) {
            alert("Por favor, configura primero la URL del Webhook de Google Apps Script.");
            setShowWebhookSettings(true);
            return;
        }

        if (predictions.length === 0) return;
        
        setIsSaving(true);
        try {
            const timestamp = new Date().toLocaleString();
            
            // Construir cabeceras dinámicamente basadas en los modelos cargados
            const headers = ["Fecha", "ID Muestra"];
            models.forEach(m => {
                headers.push(m.analyticalProperty);
                headers.push(`${m.analyticalProperty} GH`);
            });

            // Construir filas
            const rows = predictions.map(p => {
                const row: any[] = [timestamp, p.id];
                models.forEach(m => {
                    row.push(p.values[m.id] !== undefined ? p.values[m.id] : '');
                    row.push(p.ghValues[m.id] !== undefined ? p.ghValues[m.id] : '');
                });
                return row;
            });

            const payload = {
                headers: headers,
                data: rows
            };

            const response = await fetch(webhookUrl, {
                method: 'POST',
                mode: 'no-cors', // Requerido para evitar bloqueos CORS con Google Apps Script
                headers: {
                    'Content-Type': 'text/plain;charset=utf-8', // Recomendado para Apps Script bypass
                },
                body: JSON.stringify(payload)
            });

            // Al usar no-cors, la respuesta es opaca, asumimos éxito si la red no falla.
            alert("✅ Datos enviados exitosamente a Google Sheets.");
            
        } catch (e: any) {
            console.error("Error enviando al Webhook:", e);
            alert(`Error al enviar los datos: ${e.message}`);
        } finally {
            setIsSaving(false);
        }
    };"""

webhook_new = """    const handleSendToWebhook = async () => {
        if (!webhookUrl) {
            alert("Por favor, configura primero la URL del Webhook de Google Apps Script.");
            setShowWebhookSettings(true);
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
    };"""
content = content.replace(webhook_old, webhook_new)

# 5. Fix UI inside Settings panel to add explicit Save button
ui_settings_old = """                                    <input 
                                        type="url" 
                                        placeholder="https://script.google.com/macros/s/.../exec"
                                        className="flex-grow px-3 py-1.5 border border-green-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                                        defaultValue={webhookUrl}
                                        onBlur={(e) => handleSaveWebhook(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSaveWebhook(e.currentTarget.value)}
                                    />
                                    <Button size="sm" variant="secondary" onClick={() => setShowWebhookSettings(false)}>Cerrar</Button>"""

ui_settings_new = """                                    <input 
                                        type="url" 
                                        id="webhookUrlInput"
                                        placeholder="https://script.google.com/macros/s/.../exec"
                                        className="flex-grow px-3 py-1.5 border border-green-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                                        defaultValue={webhookUrl}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSaveWebhook(e.currentTarget.value)}
                                    />
                                    <Button size="sm" onClick={() => {
                                        const input = document.getElementById('webhookUrlInput') as HTMLInputElement;
                                        if (input) handleSaveWebhook(input.value);
                                    }} className="bg-green-600 hover:bg-green-700 border-transparent text-white">Guardar URL</Button>
                                    <Button size="sm" variant="secondary" onClick={() => setShowWebhookSettings(false)}>Cerrar</Button>"""
content = content.replace(ui_settings_old, ui_settings_new)


with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)

