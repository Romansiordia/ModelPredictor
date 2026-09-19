with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

content = content.replace("const promises = files.map(file => {", "const promises = files.map((file: File) => {")

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
