import type { DrawerProps } from '@mantine/core';
import type { Waypoint } from '@/api/trips';

export type MapViewerProps = DrawerProps & {
    waypoints: Array<Waypoint>;
    encodedPolyline?: string;
    defaultZoom?: number;
    onRemovePoint: (id: string) => void;
}