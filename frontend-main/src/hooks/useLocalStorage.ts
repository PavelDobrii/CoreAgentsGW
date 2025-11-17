import { useState, useEffect, useCallback, type Dispatch, type SetStateAction } from 'react';

export type SetValue<T> = Dispatch<SetStateAction<T>>;

export const useLocalStorage = <T>(key: string, initialValue: T): [T, SetValue<T>] => {
    const getStorageValue = useCallback((): T => {
        try {
            const item = window.localStorage.getItem(key);
            if (item === null) return initialValue;
            try {
                return JSON.parse(item) as T;
            } catch {
                return item as unknown as T;
            }
        } catch (error) {
            console.error(`Error reading localStorage key “${key}”:`, error);
            return initialValue;
        }
    }, [initialValue, key]);

    const [value, setValue] = useState<T>(getStorageValue);

    const updateValue: SetValue<T> = (val) => {
        try {
            const valueToStore = val instanceof Function ? val(value) : val;

            if (valueToStore === null) {
                window.localStorage.removeItem(key);
            } else {
                const isString = typeof valueToStore === 'string';
                const storedValue = isString ? valueToStore : JSON.stringify(valueToStore);
                window.localStorage.setItem(key, storedValue);
            }

            setValue(valueToStore);

            window.dispatchEvent(new Event('storage'));
        } catch (error) {
            console.error(`Error setting localStorage key “${key}”:`, error);
        }
    };

    const handleStorageChange = useCallback(
        (event: StorageEvent) => {
            if (!event.key || event.key === key) {
                setValue(getStorageValue());
            }
        },
        [key, getStorageValue],
    );

    useEffect(() => {
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, [handleStorageChange]);

    return [value, updateValue];
};
