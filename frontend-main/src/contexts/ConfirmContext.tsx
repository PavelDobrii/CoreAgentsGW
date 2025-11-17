import { type ReactNode, createContext, useContext, useState } from 'react';
import { Modal, Button, Group, Text, Stack } from '@mantine/core';

type ConfirmOptions = {
    modalTitle?: string;
    modalText?: string;
    cancelLabel?: string;
    confirmLabel?: string;
    confirmColor?: string;
}

type ConfirmContextValue =  {
    confirmAction: (options: ConfirmOptions) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextValue | null>(null);

export const ConfirmProvider = ({ children }: { children: ReactNode }) => {
    const [opened, setOpened] = useState(false);
    const [options, setOptions] = useState<ConfirmOptions>({});
    const [resolver, setResolver] = useState<(result: boolean) => void>(() => () => {});

    const confirmAction = (opts: ConfirmOptions) => {
        setOptions(opts);
        setOpened(true);
        return new Promise<boolean>((resolve) => setResolver(() => resolve));
    };

    const handleConfirm = () => {
        resolver(true);
        setOpened(false);
    };

    const handleCancel = () => {
        resolver(false);
        setOpened(false);
    };

    return (
        <ConfirmContext.Provider value={{ confirmAction }}>
            {children}

            <Modal
                opened={opened}
                onClose={handleCancel}
                title={options.modalTitle || 'Подтвердите действие'}
                centered
            >
                <Stack>
                    <Text size="sm">
                        {options.modalText || 'Вы уверены, что хотите выполнить это действие?'}
                    </Text>

                    <Group justify="flex-end">
                        <Button variant="default" onClick={handleCancel}>
                            {options.cancelLabel || 'Отмена'}
                        </Button>
                        <Button color={options.confirmColor || 'red'} onClick={handleConfirm}>
                            {options.confirmLabel || 'Подтвердить'}
                        </Button>
                    </Group>
                </Stack>
            </Modal>
        </ConfirmContext.Provider>
    );
}

export const useConfirmation = () => {
    const context = useContext(ConfirmContext);

    if (!context) throw new Error('useConfirm must be used within ConfirmProvider');

    return { confirmAction: context.confirmAction };
}
