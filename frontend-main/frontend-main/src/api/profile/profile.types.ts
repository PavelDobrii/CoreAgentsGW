export type ProfileResponse = {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    phone: string;
    country: string;
    city: string;
    isActive: boolean;
    language: string;

    gender?: Gender;
    age?: number;
    region?: string;
    interests?: Array<string>;
    travelStyle?: string;
}

export enum Gender {
    Male = 'male',
    Female = 'female',
}

export type ProfileData = {
    gender?: Gender;
    age?: number;
    city?: string;
    language?: string;
    region?: string; // country code
    interests?: Array<string>;
    travelStyle?: string;
}