export type Location = {
    lat: number;
    lng: number;
}

export type Place = {
    id: string;
    name: string;
    address: string;
    location: Location;
    types?: Array<string>,
    source?: string | "google_places"
}

export type PlacesResponse = Array<Place>

// query OR lat/lng
export type PlacesParams = {
    query?: string;
    lat?: number;
    lng?: number;

    language?: string;
    type?: 'locality' | 'country'
}
