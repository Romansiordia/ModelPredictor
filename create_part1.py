import os

os.makedirs('src/components', exist_ok=True)
os.makedirs('src/services', exist_ok=True)

with open('src/types.ts', 'w') as f:
    f.write("""export interface Sample {
    id: string | number;
    values: number[];
    color: string;
    active: boolean;
    analyticalValue: number;
}
export interface PreprocessingStep {
    method: 'none' | 'savgol' | 'snv' | 'msc' | 'detrend';
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
        }[];
        coefficients: number[];
        processedSpectra: number[][];
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
""")

with open('src/components/Card.tsx', 'w') as f:
    f.write("""import React from 'react';

interface CardProps {
    children: React.ReactNode;
    className?: string;
    noPadding?: boolean;
}

const Card: React.FC<CardProps> = ({ children, className = '', noPadding = false }) => {
    return (
        <div className={`bg-white rounded-xl border border-slate-200 shadow-card overflow-hidden flex flex-col ${className}`}>
            <div className={`flex-1 ${noPadding ? '' : 'p-6'}`}>
                {children}
            </div>
        </div>
    );
};
export default Card;
""")

with open('src/components/Button.tsx', 'w') as f:
    f.write("""import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
}

const Button: React.FC<ButtonProps> = ({ variant = 'primary', size = 'md', children, className = '', ...props }) => {
    const baseClasses = 'inline-flex items-center justify-center gap-2 rounded-lg font-semibold transition-all duration-200 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed select-none focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-offset-white';
    
    const sizeClasses = {
        sm: 'px-3 py-1.5 text-xs',
        md: 'px-4 py-2 text-sm',
        lg: 'px-6 py-3 text-base',
    };
    
    const variantClasses = {
        primary: 'bg-brand-600 text-white hover:bg-brand-700 shadow-md shadow-brand-500/20 border border-transparent focus:ring-brand-500',
        secondary: 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-300 shadow-sm hover:border-slate-400 focus:ring-slate-400',
        danger: 'bg-white text-red-600 hover:bg-red-50 border border-red-200 shadow-sm hover:border-red-300 focus:ring-red-400',
        ghost: 'bg-transparent text-slate-500 hover:text-brand-600 hover:bg-slate-50 border border-transparent',
    };
    
    return (
        <button className={`${baseClasses} ${sizeClasses[size]} ${variantClasses[variant]} ${className}`} {...props}>
            {children}
        </button>
    );
};
export default Button;
""")

with open('src/components/Header.tsx', 'w') as f:
    f.write("""import React from 'react';

const Header: React.FC = () => {
    return (
        <header className="bg-white border-b border-slate-200 sticky top-0 z-30 shadow-sm backdrop-blur-sm bg-white/95">
            <div className="max-w-[1920px] mx-auto px-4 lg:px-6 h-16 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="h-9 w-9 bg-brand-600 rounded-lg flex items-center justify-center text-white shadow-md shadow-brand-500/30">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-slate-800 tracking-tight leading-none">
                            Spectra<span className="text-brand-600">Pro</span>
                        </h1>
                        <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-widest leading-none mt-1">
                            Scientific Analysis
                        </p>
                    </div>
                </div>
                
                <div className="flex items-center gap-4">
                    <span className="hidden md:inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
                        v2.3 Lab
                    </span>
                    <div className="h-9 w-9 rounded-full bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 hover:text-brand-600 hover:bg-white hover:shadow-md cursor-pointer transition-all" title="Perfil de Usuario">
                        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                    </div>
                </div>
            </div>
        </header>
    );
};
export default Header;
""")

with open('src/components/Loader.tsx', 'w') as f:
    f.write("""import React from 'react';

interface LoaderProps {
    message?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = 'Procesando, por favor espere...' }) => {
    return (
        <div className="fixed inset-0 bg-white bg-opacity-75 flex flex-col items-center justify-center z-50">
            <svg className="animate-spin h-10 w-10 text-brand-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p className="mt-4 text-lg text-gray-700">{message}</p>
        </div>
    );
};
export default Loader;
""")
