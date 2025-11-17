import { useEffect, useState } from 'react';

type Coords = {
    lat: number,
    lng: number,
}
export const useGeolocationWatcher = () => {
    const [userCoords, setUserCoords] = useState<Coords | null>(null);
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (!navigator.geolocation) {
            setError('Geolocation is not supported by your browser')
            return
        }

        const watcher = navigator.geolocation.watchPosition(
            (position) => {
                setUserCoords({
                    lat: Number(position.coords.latitude.toFixed(7)),
                    lng: Number(position.coords.longitude.toFixed(7))
                })
                setError(null)
            },
            (error) => {
                setError('Error receiving coordinates: ' + error.message)
            },
            {
                enableHighAccuracy: true,
                maximumAge: 10000,
                timeout: 10000,
            }
        )

        return () => navigator.geolocation.clearWatch(watcher)
    }, [])

    return {
        userCoords,
        error
    }
}