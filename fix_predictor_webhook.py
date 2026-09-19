import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# 1. Eliminar importaciones de Google Sheets OAuth
content = content.replace(
    """import { applyPreprocessingLogic, predictPLS } from '../services/chemometrics';
import { initAuth, googleSignIn, getAccessToken, createSpreadsheet, appendToSpreadsheet, fetchSpreadsheets, logout } from '../services/googleSheets';
import type { User } from 'firebase/auth';""",
    "import { applyPreprocessingLogic, predictPLS } from '../services/chemometrics';"
)

# 2. Reemplazar estado de OAuth por Webhook
state_old = """    // Google Sheets Integration State
    const [user, setUser] = useState<User | null>(null);
    const [needsAuth, setNeedsAuth] = useState(false);
    const [isLoggingIn, setIsLoggingIn] = useState(false);
    const [spreadsheets, setSpreadsheets] = useState<any[]>([]);
    const [selectedSheetId, setSelectedSheetId] = useState<string>('');
    const [isSaving, setIsSaving] = useState(false);
    
    React.useEffect(() => {
        const unsubscribe = initAuth(
            (user, token) => {
                setUser(user);
                setNeedsAuth(false);
                loadSpreadsheets(token);
            },
            () => setNeedsAuth(true)
        );
        return () => unsubscribe();
    }, []);

    const loadSpreadsheets = async (token: string) => {
        try {
            const data = await fetchSpreadsheets(token);
            if (data.files) {
                setSpreadsheets(data.files);
            }
        } catch (e) {
            console.error("Failed to fetch spreadsheets:", e);
        }
    };

    const handleLogin = async () => {
        setIsLoggingIn(true);
        try {
            const result = await googleSignIn();
            if (result) {
                setUser(result.user);
                setNeedsAuth(false);
                loadSpreadsheets(result.accessToken);
            }
        } catch (err) {
            console.error('Login failed:', err);
        } finally {
            setIsLoggingIn(false);
        }
    };

    const handleLogout = async () => {
        await logout();
        setUser(null);
        setNeedsAuth(true);
        setSpreadsheets([]);
        setSelectedSheetId('');
    };

    const handleSaveToSheets = async () => {
        if (!user || predictions.length === 0) return;
        
        setIsSaving(true);
        try {
            const token = await getAccessToken();
            if (!token) throw new Error("No access token available");

            let sheetId = selectedSheetId;
            
            if (!sheetId) {
                // Create a new spreadsheet if none selected
                const dateStr = new Date().toISOString().split('T')[0];
                sheetId = await createSpreadsheet(`AgriBalance Predicciones - ${dateStr}`, token);
                
                // Add header row to new sheet
                const headers = ["Fecha", "ID Muestra"];
                models.forEach(m => {
                    headers.push(m.analyticalProperty);
                    headers.push(`${m.analyticalProperty} GH`);
                });
                
                await appendToSpreadsheet(sheetId, 'Sheet1!A1', [headers], token);
                
                // Reload list to show new file
                await loadSpreadsheets(token);
                setSelectedSheetId(sheetId);
            }

            // Prepare rows to append
            const timestamp = new Date().toLocaleString();
            const rows = predictions.map(p => {
                const row = [timestamp, p.id];
                models.forEach(m => {
                    row.push(p.values[m.id] !== undefined ? p.values[m.id] : '');
                    row.push(p.ghValues[m.id] !== undefined ? p.ghValues[m.id] : '');
                });
                return row;
            });

            await appendToSpreadsheet(sheetId, 'Sheet1!A1', rows, token);
            alert("Predicciones guardadas exitosamente en Google Sheets!");
            
        } catch (e: any) {
            console.error("Error saving to Sheets:", e);
            alert(`Error al guardar en Sheets: ${e.message}`);
        } finally {
            setIsSaving(false);
        }
    };"""

state_new = """    // Webhook / Apps Script State
    const [webhookUrl, setWebhookUrl] = useState(() => localStorage.getItem('agribalance_webhook_url') || '');
    const [isSaving, setIsSaving] = useState(false);
    const [showWebhookSettings, setShowWebhookSettings] = useState(false);

    const handleSaveWebhook = (url: string) => {
        setWebhookUrl(url);
        localStorage.setItem('agribalance_webhook_url', url);
        setShowWebhookSettings(false);
    };

    const handleSendToWebhook = async () => {
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
content = content.replace(state_old, state_new)

# 3. Reemplazar UI de los botones por la UI del Webhook
buttons_old = """                            <div className="flex gap-3 items-center flex-wrap justify-end">
                                <Button size="sm" variant="secondary" onClick={handleDownloadCSV}>
                                    Descargar CSV
                                </Button>
                                
                                {needsAuth ? (
                                    <button 
                                        onClick={handleLogin} 
                                        disabled={isLoggingIn}
                                        className="gsi-material-button bg-white text-slate-600 border border-slate-300 rounded hover:bg-slate-50 flex items-center px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-50"
                                    >
                                        <svg className="w-4 h-4 mr-2" version="1.1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">
                                            <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"></path>
                                            <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"></path>
                                            <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"></path>
                                            <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"></path>
                                            <path fill="none" d="M0 0h48v48H0z"></path>
                                        </svg>
                                        {isLoggingIn ? 'Conectando...' : 'Conectar Sheets'}
                                    </button>
                                ) : (
                                    <div className="flex items-center gap-2 bg-green-50 p-1.5 rounded-lg border border-green-200">
                                        <select 
                                            value={selectedSheetId} 
                                            onChange={(e) => setSelectedSheetId(e.target.value)}
                                            className="text-xs bg-white border border-green-200 rounded p-1.5 max-w-[150px] truncate focus:outline-none focus:ring-1 focus:ring-green-500"
                                        >
                                            <option value="">Crear nuevo archivo...</option>
                                            {spreadsheets.map(s => (
                                                <option key={s.id} value={s.id}>{s.name}</option>
                                            ))}
                                        </select>
                                        <Button 
                                            size="sm" 
                                            onClick={handleSaveToSheets} 
                                            disabled={isSaving}
                                            className="bg-green-600 hover:bg-green-700 text-white border-transparent"
                                        >
                                            {isSaving ? 'Guardando...' : 'Guardar en Sheets'}
                                        </Button>
                                        <button onClick={handleLogout} className="text-slate-400 hover:text-slate-600 px-1" title="Desconectar cuenta">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
                                        </button>
                                    </div>
                                )}
                            </div>"""

buttons_new = """                            <div className="flex gap-3 items-center flex-wrap justify-end">
                                <Button size="sm" variant="secondary" onClick={handleDownloadCSV}>
                                    Descargar CSV
                                </Button>
                                
                                <div className="flex items-center gap-2">
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
                                    </Button>
                                </div>
                            </div>
                        </div>

                        {showWebhookSettings && (
                            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg text-sm animate-fade-in">
                                <h4 className="font-bold text-green-800 mb-2">Configuración de Google Apps Script (Webhook)</h4>
                                <p className="text-green-700 mb-3 text-xs">
                                    Para guardar datos automáticamente sin iniciar sesión, pega aquí la <strong>URL de tu Aplicación Web de Apps Script</strong>.
                                </p>
                                <div className="flex gap-2">
                                    <input 
                                        type="url" 
                                        placeholder="https://script.google.com/macros/s/.../exec"
                                        className="flex-grow px-3 py-1.5 border border-green-300 rounded focus:outline-none focus:ring-1 focus:ring-green-500"
                                        defaultValue={webhookUrl}
                                        onBlur={(e) => handleSaveWebhook(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSaveWebhook(e.currentTarget.value)}
                                    />
                                    <Button size="sm" variant="secondary" onClick={() => setShowWebhookSettings(false)}>Cerrar</Button>
                                </div>
                            </div>
                        )}
                        
                        <div className="max-h-[500px] overflow-x-auto overflow-y-auto custom-scrollbar border border-slate-200 rounded-lg bg-white shadow-inner">"""
content = content.replace(buttons_old, buttons_new)

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
