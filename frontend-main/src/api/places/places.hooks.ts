import { useQuery } from '@tanstack/react-query';
import { type PlacesResponse, type PlacesParams, PlacesApi } from '@/api/places';

export const usePlaces = (params?: PlacesParams) => {
    const hasParams = Boolean(params?.query || params?.lat && params?.lng)

    return useQuery<PlacesResponse>({
        queryKey: ['places', params],
        queryFn: () => PlacesApi.getPlaces(params),
        enabled: hasParams
    });
}
