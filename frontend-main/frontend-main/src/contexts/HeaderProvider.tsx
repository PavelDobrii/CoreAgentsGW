import { type ReactNode, createContext, useContext, useState } from 'react';

export type HeaderConfig = {
    title?: string;
    action?: ReactNode;
}

export type HeaderContextValue = {
    config: HeaderConfig;
    setHeaderConfig: (value: HeaderConfig) => void;
    resetHeader: () => void;
}

const HeaderContext = createContext<HeaderContextValue | null>(null);

export const HeaderProvider = ({ children }: { children: ReactNode }) => {
    const [config, setHeaderConfig] = useState<HeaderConfig>({});

    const resetHeader = () => {
        setHeaderConfig({})
    }

    const context: HeaderContextValue = {
        config,
        setHeaderConfig,
        resetHeader
    }

    return (
        <HeaderContext.Provider value={context}>
            {children}
        </HeaderContext.Provider>
    );
};

export const useHeaderContext = (): HeaderContextValue => {
    const context = useContext(HeaderContext);

    if (context === null || context === undefined) {
        throw new Error('useHeaderContext must be used within a HeaderProvider');
    }

    return context;
};
