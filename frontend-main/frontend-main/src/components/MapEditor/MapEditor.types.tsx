import type { Place } from '@/api/places';
import type { DrawerProps } from '@mantine/core';

export type MapEditorProps = DrawerProps & {
    value: Place | null;
    onConfirm: (place: Place) => void
}