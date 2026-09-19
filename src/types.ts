export interface Sample {
    id: string | number;
    values: number[];
    color: string;
    active: boolean;
    analyticalValue: number;
}
export interface PreprocessingStep {
    method: 'none' | 'savgol' | 'savgol1' | 'savgol2' | 'savgolsmooth' | 'snv' | 'msc' | 'detrend';
    params: { [key: string]: any };
}
export interface PcaResult {
    id: string | number;
    x: number;
    y: number;
    color: string;
}
export interface OptimizationResult {
    components: number;
    sec: number;
    secv: number;
}
export interface ModelResults {
    modelType: 'PLS';
    nComponents: number;
    model: {
        r: number;
        r2: number;
        q2: number;
        sec: number;
        secv: number;
        slope: number;
        offset: number;
        plsIntercept: number;
        correlation: {
            actual: number[];
            predicted: number[];
            predictedCV: number[];
        };
        residuals: {
            id: string | number;
            actual: number;
            predicted: number;
            residual: number;
            gh?: number;
        }[];
        coefficients: number[];
        processedSpectra: number[][];
        referenceSpectrum?: number[];
        xMean?: number[];
        W?: number[][];
        T_inv_var?: number[];
    };
    mahalanobis: {
        distances: {
            id: string | number;
            distance: number;
            isOutlier: boolean;
        }[];
        outlierIds: (string | number)[];
    };
}
export interface PcaScorePoint {
    id: string | number;
    pc1: number;
    pc2: number;
    pc3?: number;
    gh?: number;
    hotellingT2?: number;
    qResidual?: number;
    isOutlier?: boolean;
    outlierReason?: string;
    active?: boolean;
    color?: string;
    analyticalValue?: number;
}
export interface PcaAnalysisModel {
    scores: PcaScorePoint[];
    varianceExplained: number[];
    cumulativeVariance: number[];
    t2Limit95: number;
    t2Limit99: number;
    qLimit95: number;
    qLimit99: number;
    outlierCount: number;
    totalCount: number;
}
export interface IngredientLibrary {
    id: string;
    name: string;
    samples: { id: string | number; values: number[] }[];
    averageSpectrum: number[];
    stdDevSpectrum: number[];
    threshold: number;
}
export interface ClassificationResult {
    ingredientId: string;
    ingredientName: string;
    confidence: number;
    distance: number;
    isConforming: boolean;
    details: {
        meanDistance: number;
        threshold: number;
    };
}
