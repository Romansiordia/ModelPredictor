import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# 1. Remove state
content = content.replace("const [showWebhookSettings, setShowWebhookSettings] = useState(false);", "")

# 2. Modify handleSaveWebhook
old_save = """    const handleSaveWebhook = (url: string) => {
        setWebhookUrl(url);
        localStorage.setItem('agribalance_webhook_url', url);
        setShowWebhookSettings(false);
    };"""
new_save = """    const handleSaveWebhook = (url: string) => {
        setWebhookUrl(url);
        localStorage.setItem('agribalance_webhook_url', url);
    };"""
content = content.replace(old_save, new_save)

# 3. Add Global Card and replace return (
old_return = """    return (
        <Card>
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                <PredictIcon />
                Predictor Multiparamétrico
            </h2>

            <div className="space-y-6">
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">"""

new_return = """    return (
        <Card>
            <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-slate-800">
                <PredictIcon />
                Predictor Multiparamétrico
            </h2>

            <div className="space-y-6">
                
                {/* Global Webhook Settings */}
                <div className="bg-green-50/50 p-4 rounded-xl border border-green-100 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                    <div>
                        <h3 className="text-sm font-bold text-green-800">Conexión Automática a Google Sheets</h3>
                        <p className="text-xs text-green-700">Pega aquí la URL de tu Webhook para sincronizar los resultados y espectros.</p>
                    </div>
                    <div className="flex w-full md:w-auto items-center gap-2">
                        <input 
                            type="url" 
                            placeholder="https://script.google.com/macros/s/.../exec"
                            className="flex-grow md:w-80 text-sm px-3 py-1.5 border border-green-200 rounded focus:outline-none focus:ring-1 focus:ring-green-500 bg-white shadow-sm"
                            value={webhookUrl}
                            onChange={(e) => setWebhookUrl(e.target.value)}
                            onBlur={(e) => handleSaveWebhook(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSaveWebhook(e.currentTarget.value)}
                        />
                        <button 
                            onClick={() => handleSaveWebhook(webhookUrl)}
                            className="px-3 py-1.5 text-sm bg-green-600 hover:bg-green-700 text-white rounded font-medium shadow-sm transition-colors"
                        >
                            Guardar
                        </button>
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">"""
content = content.replace(old_return, new_return)

# 4. Remove inline webhook UI
# From: <input type="text" value={sheetName} ... /> all the way to </Button></div></div></div>
old_inline_ui = """                                    <input 
                                        type="text" 
                                        value={sheetName} 
                                        onChange={(e) => handleSheetNameChange(e.target.value)}
                                        placeholder="Pestaña (ej. Viavi)"
                                        className="text-sm px-2 py-1 h-8 border border-slate-300 rounded shadow-sm w-36 focus:outline-none focus:ring-1 focus:ring-green-500 text-slate-700 bg-white"
                                        title="Nombre de la hoja en Google Sheets (ej. Viavi, Foss)"
                                    />
                                    <button 
                                        onClick={() => setShowWebhookSettings(!showWebhookSettings)}
                                        className="p-1.5 text-slate-400 hover:text-brand-600 transition-colors"
                                        title="Configurar URL de Google Sheets"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                    </button>
                                    <Button 
                                        size="sm" 
                                        onClick={handleSendToWebhook} 
                                        disabled={isSaving}
                                        className="bg-green-600 hover:bg-green-700 text-white border-transparent flex items-center gap-2"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                                        {isSaving ? 'Enviando...' : 'Enviar a Sheets'}
                                    </Button>"""

new_inline_ui = """                                    <select 
                                        value={sheetName} 
                                        onChange={(e) => handleSheetNameChange(e.target.value)}
                                        className="text-sm px-2 py-1 h-8 border border-slate-300 rounded shadow-sm focus:outline-none focus:ring-1 focus:ring-green-500 text-slate-700 bg-white font-medium"
                                        title="Selecciona el instrumento (Pestaña en Google Sheets)"
                                    >
                                        <option value="Viavi">Instrumento: Viavi</option>
                                        <option value="Foss">Instrumento: Foss</option>
                                        <option value="Bruker">Instrumento: Bruker</option>
                                        <option value="MicroNIR">Instrumento: MicroNIR</option>
                                        <option value="Resultados">General</option>
                                    </select>
                                    
                                    <Button 
                                        size="sm" 
                                        onClick={handleSendToWebhook} 
                                        disabled={isSaving}
                                        className="bg-green-600 hover:bg-green-700 text-white border-transparent flex items-center gap-2"
                                    >
                                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>
                                        {isSaving ? 'Enviando...' : 'Enviar a Sheets'}
                                    </Button>"""
content = content.replace(old_inline_ui, new_inline_ui)


# 5. Remove the Webhook Settings block completely
old_settings_block = """                        {showWebhookSettings && (
                            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-sm animate-fade-in">
                                <h4 className="font-bold text-green-800 mb-2">Configuración de Google Apps Script (Webhook)</h4>
                                <p className="text-green-700 mb-3 text-xs">
                                    Para guardar datos automáticamente sin iniciar sesión, pega aquí la <strong>URL de tu Aplicación Web de Apps Script</strong>.
                                </p>
                                <div className="flex gap-2">
                                    <input 
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
                                    <Button size="sm" variant="secondary" onClick={() => setShowWebhookSettings(false)}>Cerrar</Button>
                                </div>
                            </div>
                        )}
                        
                        <div className="max-h-[500px] overflow-x-auto overflow-y-auto custom-scrollbar border border-slate-200 rounded-lg bg-white shadow-inner">
                        </div>"""
content = content.replace(old_settings_block, "")


# 6. Change webhook empty URL alert string
old_alert = 'alert("Por favor, configura primero la URL del Webhook de Google Apps Script.");\n            setShowWebhookSettings(true);'
new_alert = 'alert("Por favor, pega la URL de conexión a Google Sheets en el recuadro superior.");'
content = content.replace(old_alert, new_alert)


with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
