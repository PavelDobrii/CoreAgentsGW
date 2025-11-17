import { type RefObject, useEffect, useState } from 'react';
import type { SongItem } from './PlayerProvider.types';

type UseAudioPlayerProps = {
    audioRef: RefObject<HTMLAudioElement | null>;
    currentSong: SongItem | null;
    handleNext: () => void;
}

export const useAudioTime = ({
    audioRef,
    currentSong,
    handleNext
}: UseAudioPlayerProps) => {
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);

    const handleTimeUpdate = () => {
        const audio = audioRef.current;
        if (!audio) return;
        setCurrentTime(audio.currentTime || 0);
        setDuration(audio.duration || 0);
    };

    useEffect(() => {
        const audio = audioRef.current;
        if (!audio) return;

        audio.addEventListener('timeupdate', handleTimeUpdate);
        audio.addEventListener('loadedmetadata', handleTimeUpdate);
        audio.addEventListener('ended', handleNext);

        return () => {
            audio.removeEventListener('timeupdate', handleTimeUpdate);
            audio.removeEventListener('loadedmetadata', handleTimeUpdate);
            audio.removeEventListener('ended', handleNext);
        };
    }, [handleNext]);

    useEffect(() => {
        const audio = audioRef.current;

        if (!audio || !currentSong) return;

        audio.src = currentSong.audioSrc;
        audio.load();

        const playAudio = async () => {
            try {
                await audio.play();
            } catch (err) {
                console.warn('Error when trying to play:', err);
            }
        };

        const handleCanPlay = () => {
            playAudio();
            audio.removeEventListener('canplay', handleCanPlay);
        };

        audio.addEventListener('canplay', handleCanPlay);

        return () => {
            audio.removeEventListener('canplay', handleCanPlay);
        };
    }, [currentSong, audioRef]);

    return {
        currentTime,
        duration,
    };
};