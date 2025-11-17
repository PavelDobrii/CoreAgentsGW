type NormalizedPlace = {
    id: string | null;
    displayName: string;
    location: { lat: number; lng: number } | null;
    formattedAddress: string;
    countryCode: string | null;
}
type FetchFieldsResult =
    | { place: google.maps.places.Place }
    | google.maps.places.Place;

export const getAutocompleteSuggestions = async (input: string) => {
    const {
        AutocompleteSessionToken,
        AutocompleteSuggestion,
    } = await google.maps.importLibrary('places') as google.maps.PlacesLibrary;

    const token = new AutocompleteSessionToken();

    const request: google.maps.places.AutocompleteRequest = {
        input,
        includedPrimaryTypes: ['country', 'locality'],
        // includedRegionCodes: ['PL', 'BY'],
        language: 'ru-RU',
        sessionToken: token,
    };

    const { suggestions } = await AutocompleteSuggestion.fetchAutocompleteSuggestions(request);
    if (!suggestions?.length) return [];

    const places = suggestions
        .map(({ placePrediction }) => placePrediction?.toPlace())
        .filter(Boolean) as any[];

    const fetchedPlaces = await Promise.all(
        places.map(p => p.fetchFields({
            fields: ['displayName', 'location', 'formattedAddress', 'addressComponents', 'photos'],
        })),
    );

    return fetchedPlaces.map((item: FetchFieldsResult): NormalizedPlace => {
        const place = (item as any).place || item;

        const id: string | null = place?.id || place?.placeId || null;

        const displayName: string = typeof place?.displayName === 'object'
            ? place.displayName?.text || ''
            : place?.displayName || '';

        const location = place?.location
            ? { lat: place.location.lat(), lng: place.location.lng() }
            : null;

        const formattedAddress: string = place?.formattedAddress || '';

        const countryCode: string | null = getCountryCode(place?.addressComponents)

        return { id, displayName, location, formattedAddress, countryCode };
    });
};

export const getCountryCode = (addressComponents?: Array<google.maps.places.AddressComponent> | null): string | null => {
    if (!Array.isArray(addressComponents) || addressComponents.length === 0) {
        return null;
    }

    const countryComponent = addressComponents.find(component =>
        Array.isArray(component.types) && component.types.includes('country'),
    );

    return countryComponent?.shortText ?? null;
};
