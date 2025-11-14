import { apiClient } from '@/api';
import type {
    GenerateTripOptions,
    GenerateTripResponse,
    TripListParams,
    TripListResponse,
    TripResponse,
    TripSchema,
} from '@/api/trips';

const getTrips = async (params?: TripListParams): Promise<TripListResponse> => {
    const response = await apiClient.get<TripListResponse>('routes', {
        params
    });
    return response.data;
}

const getTripById = async (id?: string): Promise<TripResponse> => {
    const response = await apiClient.get<TripResponse>(`routes/${id}`);
    return response.data;
};

const createTrip = async (data: TripSchema): Promise<TripResponse> => {
    const response = await apiClient.post<TripResponse>('routes', data);
    return response.data;
}

const generateTrip = async ({ id, ...data }: GenerateTripOptions): Promise<GenerateTripResponse> => {
    const response = await apiClient.post<GenerateTripResponse>(`routes/${id}/generate`, data);
    return response.data;
}

const updateTrip = async ({ id, ...data }: TripSchema): Promise<TripResponse> => {
    const response = await apiClient.post<TripResponse>(`routes/${id}`, data);
    return response.data;
};

export const TripApi = {
    getTrips,
    getTripById,
    createTrip,
    generateTrip,
    updateTrip,
}