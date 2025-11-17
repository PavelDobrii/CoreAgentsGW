import { useEffect } from 'react';
import { type HeaderConfig, useHeaderContext } from '@/contexts';

export const useHeader = (headerConfig: HeaderConfig) => {
    const headerContext = useHeaderContext();

    useEffect(() => {
        headerContext.setHeaderConfig(headerConfig);
        return () => headerContext.resetHeader();
    }, []);
};