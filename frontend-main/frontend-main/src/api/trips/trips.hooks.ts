import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import type {
    TripSchema,
    TripListParams,
    TripListResponse,
    TripResponse,
    GenerateTripResponse,
    GenerateTripOptions,
} from '@/api/trips';
import { TripApi } from '@/api/trips';

export const useTrips = (params?: TripListParams) => {
    return useQuery<TripListResponse>({
        queryKey: ['trips', params],
        queryFn: () => TripApi.getTrips(params),
    });
}

export const useTripsById = (id?: string) => {
    return useQuery<TripResponse>({
        queryKey: ['trips', id],
        queryFn: () => TripApi.getTripById(id),
        enabled: !!id,
    });
}

export const useCreateTrip = () => {
    const queryClient = useQueryClient();
    return useMutation<Pick<TripResponse, 'id'>, Error, TripSchema>({
        mutationFn: TripApi.createTrip,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['trips'] });
        },
    });
};

export const useGenerateTrip = () => {
    const queryClient = useQueryClient();
    return useMutation<GenerateTripResponse, Error, GenerateTripOptions>({
        mutationFn: TripApi.generateTrip,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['trips'] });
        },
    });
};

export const useUpdateTrip = () => {
    const queryClient = useQueryClient();
    return useMutation<TripResponse, Error, TripSchema>({
        mutationFn: TripApi.updateTrip,
        onSuccess: (updatedCard) => {
            queryClient.invalidateQueries({ queryKey: ['trips'] });
            queryClient.invalidateQueries({ queryKey: ['trips', updatedCard.id] });
        },
    });
};