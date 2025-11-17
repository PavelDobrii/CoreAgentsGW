import { apiClient } from '@/api';
import type { PlacesResponse, PlacesParams } from '@/api/places';

const getPlaces = async (params?: PlacesParams): Promise<PlacesResponse> => {
    const response = await apiClient.get<PlacesResponse>('places', {
        params
    });
    return response.data;
}

export const PlacesApi = {
    getPlaces,
}