with open('src/components/ResultsViewer.tsx', 'r') as f:
    content = f.read()
content = content.replace("].join('\n');", "].join('\\n');")
with open('src/components/ResultsViewer.tsx', 'w') as f:
    f.write(content)
