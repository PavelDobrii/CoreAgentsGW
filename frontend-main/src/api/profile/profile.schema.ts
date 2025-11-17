import { array, mixed, object, string } from 'yup';
import { Gender, type ProfileData } from '@/api/profile';

export const onboardingSchema = object().shape({
    gender: mixed().oneOf(Object.values(Gender))
        .required('Укажи пол'),
    travelStyle: string()
        .required('Укажи стиль'),
    interests: array().of(string())
        .min(2, 'Надо минимум 2 для лучшей персонализации')
        .required('Укажи интересы'),
    language: string().required('Укажи язык')
})

export type OnboardingSchema = Pick<ProfileData, 'gender' | 'travelStyle' | 'interests' | 'language'>


export const profileSchema = object().shape({
    travelStyle: string()
        .required('Укажи стиль'),
    interests: array().of(string())
        .min(2, 'Надо минимум 2 для лучшей персонализации')
        .required('Укажи интересы'),
    language: string().required('Укажи язык')
})

export type ProfileSchema = Pick<ProfileData, 'gender' | 'travelStyle' | 'interests' | 'language'>

