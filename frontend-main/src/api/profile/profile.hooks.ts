import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { ProfileApi, type ProfileData, type ProfileResponse } from '@/api/profile';

export const useProfile = () => {
    return useQuery<ProfileResponse>({
        queryKey: ['profile'],
        queryFn: () => ProfileApi.getProfile(),
    });
}

export const useUpdateProfile = () => {
    const queryClient = useQueryClient();
    return useMutation<ProfileResponse, Error, ProfileData>({
        mutationFn: ProfileApi.updateProfile,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['profile'] });
        },
    });
};