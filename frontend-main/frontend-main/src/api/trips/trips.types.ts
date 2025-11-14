import type { Place } from '@/api/places';

export enum TripStatus {
    Created = 'created', // только создали отдали Id
    Draft = 'draft', // генерация точек закончилась
    InProgress = 'inProgress', // начинаем генерить маршрут
    Success = 'success', // после генерации маршрута
    Failed = 'failed' // после генерации маршрута
}

export type Waypoint = Place & {
    description?: string;
    audioSrc?: string;
    posterSrc?: string;
    text?: string;
    order?: number;
}

export type TripResponse = {
    id: string;
    name: string;
    description: string;
    startWaypoint: Waypoint;
    endWaypoint: Waypoint;
    status: TripStatus;
    encodedPolyline: string;
    distance: number;
    rating: number;
    waypoints: Array<Waypoint> | null;
    createdAt: string;
    updatedAt: string;
}

export type GenerateTripOptions = { id: string; waypoints: Array<string>; places: Array<string> }
export type GenerateTripResponse = { message: string }

export type TripListResponse = Array<TripResponse>

export type TripListParams = {
    limit?: number;
    offset?: number;
    include?: 'waypoints'
}
