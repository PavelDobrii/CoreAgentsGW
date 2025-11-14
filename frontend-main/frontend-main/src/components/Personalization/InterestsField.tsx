import { type FC, type FocusEventHandler, type ReactNode } from 'react';
import { Chip, Group, InputError, InputLabel, Stack } from '@mantine/core';
import { INTEREST_OPTIONS } from '@/constants/personalization.ts';

type InterestsFieldProps = {
    value?: Array<string>;
    onChange: (value: Array<string>) => void;
    onBlur?: FocusEventHandler<any>;
    onFocus?: FocusEventHandler<any>;
    error?: string | ReactNode;
    label?: string;
};

export const InterestsField: FC<InterestsFieldProps> = ({ value, onChange, label, error, ...restProps }) => {
    return (
        <Stack gap={0}>
            {label && <InputLabel>{label}</InputLabel>}
            {error && <InputError mb="sm">{error}</InputError>}
            <Chip.Group value={value} onChange={onChange} {...restProps} multiple>
                <Group gap={8}>
                    {INTEREST_OPTIONS.map(({ value, label }) => (
                        <Chip key={value} value={value} variant="outline" size="sm">{label}</Chip>
                    ))}
                </Group>
            </Chip.Group>
        </Stack>
    );
};
