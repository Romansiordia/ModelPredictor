import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

# Fix strict type declarations pushing new attributes to prediction arrays inside the parser callbacks

type_old = "const newPredictions: {id: string, values: Record<string, number>, ghValues: Record<string, number>}[] = [];"
type_new = "const newPredictions: {id: string, values: Record<string, number>, ghValues: Record<string, number>, rawSpectrum?: number[], wavelengths?: number[]}[] = [];"
content = content.replace(type_old, type_new)

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
