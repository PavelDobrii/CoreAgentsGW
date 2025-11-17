import { array, type InferType, mixed, number, object, string } from 'yup';

export const locationSchema = object().shape({
    lat: number().required(),
    lng: number().required(),
})

export const waypointSchema = object({
    id: string().optional(),
    name: string().required(),
    address: string().required(),
    location: locationSchema.required(),
    description: string().optional(),
}).nullable();

export type WaypointSchema = InferType<typeof waypointSchema>;


export enum TimeOfDate {
    morning = 'Morning',
    day = 'Day',
    evening = 'Evening',
    night = 'Night'
}

export const routeOptionsSchema = object({
    interests: array().of(string()).optional().min(1).required(),
    moods: array().of(string()).optional(),
    dateAt: string().optional(),
    duration: string().optional(),
    timeOfDay: mixed().oneOf(Object.values(TimeOfDate)),
}).optional();

export type RouteOptionsSchema = InferType<typeof routeOptionsSchema>;

export const tripSchema = object({
    id: string().optional(),
    title: string().optional(),
    description: string().optional(),
    localityId: string().required(),
    start: waypointSchema.nullable().optional(),
    end: waypointSchema.nullable().optional(),
    routeOptions: routeOptionsSchema,
});

export type TripSchema = {
    id?: string;
    description?: string;
    title: string;
    localityId: string | null;
    start: WaypointSchema | null;
    end: WaypointSchema | null;
    routeOptions?: RouteOptionsSchema;
};