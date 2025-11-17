import { apiClient } from '@/api';
import type { ProfileResponse, ProfileData } from '@/api/profile';

const getProfile = async (): Promise<ProfileResponse> => {
    const response = await apiClient.get<ProfileResponse>('profile');
    return response.data;
}

const updateProfile = async (data: ProfileData): Promise<ProfileResponse> => {
    const response = await apiClient.put<ProfileResponse>('profile', data);
    return response.data;
}

export const ProfileApi = {
    getProfile,
    updateProfile
}