import type { FC, FocusEventHandler, ReactNode } from 'react';
import { Group, Radio } from '@mantine/core';
import { TRAVEL_STYLE_OPTIONS } from '@/constants/personalization.ts';

type TravelStyleFieldProps = {
    value?: string;
    onChange: (value: string) => void;
    onBlur?: FocusEventHandler<any>;
    onFocus?: FocusEventHandler<any>;
    error?: string | ReactNode;
    label?: string;
};

export const TravelStyleField: FC<TravelStyleFieldProps> = ({ value, onChange, ...restProps }) => {
    return (
        <Radio.Group value={value} onChange={onChange} {...restProps}>
            <Group gap={8}>
                {TRAVEL_STYLE_OPTIONS.map(({ value, label }) => (
                    <Radio key={value} value={value} label={label} />
                ))}
            </Group>
        </Radio.Group>
    );
};
