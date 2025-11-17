import { type MantineTheme, Button, Drawer, createTheme, Modal, InputLabel } from '@mantine/core';

export const AppTheme = createTheme({
    autoContrast: true,
    luminanceThreshold: 0.5,

    fontFamily: 'system-ui, Avenir, Helvetica, Arial, sans-serif',
    primaryColor: 'yellow',
    primaryShade: 5, // main color
    white: '#FAF9F6', // background
    black: '#212121',
    colors: {
        yellow: [
            '#FFF9E6', // 0
            '#FFF1BF', // 1
            '#FFE999', // 2
            '#FFE07A', // 3
            '#FFD859', // 4
            '#FFD207', // 5
            '#FFBF00', // 6
            '#FFAD00', // 7
            '#FF9C00', // 8
            '#FF8B00', // 9
        ],
    },
    components: {
        InputLabel: InputLabel.extend({
            defaultProps: { mb: 4 },
        }),
        Modal: Modal.extend({
            styles: () => ({ body: { padding: '20px 16px' } }),
        }),
        Button: Button.extend({
            defaultProps: {},
            styles: () => ({
                root: { fontWeight: '500' },
            }),
        }),
        Drawer: Drawer.extend({
            defaultProps: {
                position: 'bottom',
                size: '100%',
                closeButtonProps: {
                    size: 'lg',
                    radius: 'xl',
                },
            },
            styles: (theme: MantineTheme) => ({
                header: { border: 'none', borderRadius: 0 },
                body: {
                    minHeight: 'calc(100dvh - 60px)',
                    padding: `${theme.spacing.lg} ${theme.spacing.md}`,
                    display: 'flex',
                    gap: theme.spacing.md,
                    flexDirection: 'column',
                },
                close: {
                    borderRadius: theme.radius.md,
                    background: 'var(--mantine-color-dark-light-hover)',
                },
            }),
        }),
    },
    spacing: {
        xs: '8px'
    },
    fontSizes: {
        xs: '12px',
        sm: '14px',
        md: '16px',
        lg: '20px',
        xl: '28px',
    },
    radius: {
        xs: '8px',
        sm: '8px',
        md: '8px',
        lg: '8px',
        xl: '50px',
    },
    defaultRadius: 'md',
});
