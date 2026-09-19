// Mock math tests to see exactly how GH is calculated
const spectrum = Array(10).fill(1.5);
const xMean = Array(10).fill(1.4);
const W = Array.from({length: 10}, () => Array(3).fill(0.1));
const T_inv_var = [2, 1.5, 1];

const M = xMean.length;
const xc = new Array(M);
for(let i=0; i<M; i++) {
    xc[i] = (spectrum[i] || 0) - xMean[i];
}

let hDist = 0;
const numComponents = T_inv_var.length;
            
for (let a = 0; a < numComponents; a++) {
    let ta = 0;
    for (let i = 0; i < M; i++) {
        ta += xc[i] * W[i][a];
    }
    hDist += (ta * ta) * T_inv_var[a];
}

console.log("hDist:", hDist);
// Current logic: gh = Math.sqrt(hDist * (numComponents || 1) * 10); 
console.log("Current GH:", Math.sqrt(hDist * (numComponents || 1) * 10));
// Let's print out what WinISI / Standard Chemometrics GH calculation looks like
// Global Mahalanobis GH = hDist
console.log("Standard Global GH:", hDist);
