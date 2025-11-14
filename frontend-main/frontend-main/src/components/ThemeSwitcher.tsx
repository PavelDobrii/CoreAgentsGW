import { type MantineColorScheme, Select, useMantineColorScheme } from '@mantine/core';
import { ThemeType } from '@/App.tsx';

export const ThemeSwitcher = () => {
    const { colorScheme, setColorScheme } = useMantineColorScheme();

    return (
        <Select
            label="Тема"
            value={colorScheme}
            onChange={(value) => setColorScheme(value as MantineColorScheme)}
            allowDeselect={false}
            data={[
                {
                    value: ThemeType.Light,
                    label: 'Светлая'
                },
                {
                    value: ThemeType.Dark,
                    label: 'Темная'
                },
                {
                    value: ThemeType.Auto,
                    label: 'Системная'
                },
            ]}
        />
    );
};
