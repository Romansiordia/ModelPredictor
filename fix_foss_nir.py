import re

with open('src/components/ModelPredictor.tsx', 'r') as f:
    content = f.read()

old_foss_loop = """                            for (const model of models) {
                                if (sample.values.length !== model.metrics.coefficients.length) {
                                    continue;
                                }

                                const processed = applyPreprocessingLogic(sample.values, model.preprocessing);
                                const { prediction, gh } = predictPLS(model.metrics, processed);

                                values[model.id] = prediction;
                                ghValues[model.id] = gh;
                            }"""

new_foss_loop = """                            for (const model of models) {
                                // Extract the exact number of wavelengths needed by the model
                                // to handle cases where the .nir file contains slightly more/less padded points
                                const spectralValues = sample.values.slice(0, model.metrics.coefficients.length);
                                
                                if (spectralValues.length !== model.metrics.coefficients.length || spectralValues.some(v => isNaN(v))) {
                                    console.warn(`[FOSS] Mismatch for ${sample.id} vs Model ${model.analyticalProperty}. Model needs ${model.metrics.coefficients.length}, got ${spectralValues.length}`);
                                    continue;
                                }

                                const processed = applyPreprocessingLogic(spectralValues, model.preprocessing);
                                const { prediction, gh } = predictPLS(model.metrics, processed);

                                values[model.id] = prediction;
                                ghValues[model.id] = gh;
                            }"""

content = content.replace(old_foss_loop, new_foss_loop)

with open('src/components/ModelPredictor.tsx', 'w') as f:
    f.write(content)
