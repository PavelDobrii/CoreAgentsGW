import { Badge, Loader } from '@mantine/core';
import { TripStatus } from '@/api/trips';
import { Check, CircleSlash, FilePlus2, Pencil } from 'lucide-react';

export const StatusField = ({ status }: { status: TripStatus }) => {
    const activeBadge = BADGE_COLOR_MAP[status]
    return (
        <Badge
            autoContrast
            size="xs"
            leftSection={activeBadge.icon}
            color={activeBadge.color}
        >{activeBadge.label}</Badge>
    );
};

const BADGE_COLOR_MAP = {
    [TripStatus.Created]: {
        color: 'gray.6',
        icon: <FilePlus2 size={14} />,
        label: 'Создание'
    },
    [TripStatus.Draft]: {
        color: 'gray.6',
        icon: <Pencil size={14} />,
        label: 'Черновик'
    },
    [TripStatus.InProgress]: {
        color: 'blue.6',
        icon: <Loader color="gray.1" size={12} />,
        label: 'Генерируется'
    },
    [TripStatus.Success]: {
        color: 'green.6',
        icon: <Check size={14} />,
        label: 'Готово'
    },
    [TripStatus.Failed]: {
        color: 'red.6',
        icon: <CircleSlash size={12} />,
        label: 'Ошибка'
    },
}
