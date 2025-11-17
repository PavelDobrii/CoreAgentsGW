import type { Waypoint } from '@/api/trips';
import type { DrawerProps } from '@mantine/core';

export type MapPlayerProps = DrawerProps & {
    startWaypoint: Waypoint;
    waypoints: Array<Waypoint>;
    encodedPolyline: string;
    defaultZoom?: number;
    onPlaySong: (waypoint: Waypoint) => void;
}