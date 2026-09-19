import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# 1. State Addition
state_old = """    // Webhook / Apps Script State
    const [webhookUrl, setWebhookUrl] = useState(() => localStorage.getItem('agribalance_webhook_url') || '');
    const [isSaving, setIsSaving] = useState(false);
    const [showWebhookSettings, setShowWebhookSettings] = useState(false);"""

state_new = """    // Webhook / Apps Script State
    const [webhookUrl, setWebhookUrl] = useState(() => localStorage.getItem('agribalance_webhook_url') || '');
    const [sheetName, setSheetName] = useState(() => localStorage.getItem('agribalance_sheet_name') || 'Resultados');
    const [isSaving, setIsSaving] = useState(false);
    const [showWebhookSettings, setShowWebhookSettings] = useState(false);

    const handleSheetNameChange = (val: string) => {
        setSheetName(val);
        localStorage.setItem('agribalance_sheet_name', val);
    };"""
content = content.replace(state_old, state_new)


# 2. Payload Addition
payload_old = """            const payload = {
                headers: headers,
                data: rows
            };"""

payload_new = """            const payload = {
                sheetName: sheetName || 'Resultados',
                headers: headers,
                data: rows
            };"""
content = content.replace(payload_old, payload_new)


# 3. UI Addition
ui_old = """                                <div className="flex items-center gap-2">
                                    <button 
                                        onClick={() => setShowWebhookSettings(!showWebhookSettings)}"""

ui_new = """                                <div className="flex items-center gap-2">
                                    <input 
                                        type="text" 
                                        value={sheetName} 
                                        onChange={(e) => handleSheetNameChange(e.target.value)}
                                        placeholder="Pestaña (ej. Viavi)"
                                        className="text-sm px-2 py-1 h-8 border border-slate-300 rounded shadow-sm w-36 focus:outline-none focus:ring-1 focus:ring-green-500 text-slate-700 bg-white"
                                        title="Nombre de la hoja en Google Sheets (ej. Viavi, Foss)"
                                    />
                                    <button 
                                        onClick={() => setShowWebhookSettings(!showWebhookSettings)}"""
content = content.replace(ui_old, ui_new)

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
