import { useEffect, useState } from 'react';

const fallbackCenter = { lat: 52.2296756, lng: 21.0122287 };

export const useGeolocation = () => {
    const [userCoords, setUserCoords] = useState<{ lat: number; lng: number } | null>(null);

    useEffect(() => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => setUserCoords({
                    lat: Number(position.coords.latitude.toFixed(7)),
                    lng: Number(position.coords.longitude.toFixed(7)),
                }),
                () => setUserCoords(fallbackCenter),
                { enableHighAccuracy: true, timeout: 10000 },
            );
        } else {
            setUserCoords(fallbackCenter);
        }
    }, []);

    return { userCoords };
};
