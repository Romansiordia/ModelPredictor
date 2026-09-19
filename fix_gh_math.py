import re

with open('src/services/chemometrics.ts', 'r') as f:
    content = f.read()

old_gh = "gh = Math.sqrt(hDist * (numComponents || 1) * 10);"
new_gh = "gh = hDist; // Standard Global Mahalanobis (GH) distance"

content = content.replace(old_gh, new_gh)

with open('src/services/chemometrics.ts', 'w') as f:
    f.write(content)

