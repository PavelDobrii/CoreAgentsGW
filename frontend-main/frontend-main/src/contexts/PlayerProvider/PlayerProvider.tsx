import { type ReactNode, createContext, useContext, useState, useRef, useCallback } from 'react';
import type { PlayerContextValue, SongItem, Songs } from '@/contexts';
import { useAudioTime } from '@/contexts';

const PlayerContext = createContext<PlayerContextValue | null>(null);

export const PlayerProvider = ({ children }: { children: ReactNode }) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [songs, initPlayer] = useState<Songs>([]);

    const [currentSong, setCurrentSong] = useState<SongItem | null>(null);

    const changeTrack = useCallback((direction: 1 | -1) => {
        if (!currentSong) return;

        const index = songs.findIndex((s) => s.id === currentSong.id);
        const nextSong = songs[index + direction];

        if (nextSong) {
            onPlay(nextSong);
        } else {
            audioRef.current?.pause()
            setCurrentSong(null);
            setIsPlaying(false);
        }
    }, [currentSong, songs]);

    const handleNext = useCallback(() => changeTrack(1), [changeTrack]);
    const handlePrev = useCallback(() => changeTrack(-1), [changeTrack]);

    const { duration, currentTime } = useAudioTime({
        audioRef,
        currentSong,
        handleNext
    });

    const onPlay = (song: SongItem) => {
        if (!audioRef.current) return;

        audioRef.current.currentTime = 0;
        setCurrentSong(song);
        setIsPlaying(true);
    };

    const handlePlay = () => {
        audioRef.current?.play();
        setIsPlaying(true);
    };

    const handlePause = () => {
        audioRef.current?.pause();
        setIsPlaying(false);
    };

    const handleSeek = (percent: number) => {
        const audio = audioRef.current;
        if (!audio) return;
        audio.currentTime = percent * audio.duration;
    };

    const handleSkip = (amount: number) => {
        const audio = audioRef.current;
        if (!audio) return;
        audio.currentTime = Math.min(Math.max(audio.currentTime + amount, 0), duration);
    };

    const timeline = {
        currentTime,
        duration,
    };

    const context: PlayerContextValue = {
        initPlayer,
        songs,
        currentSong,
        isPlaying,
        onPlay,
        handlePlay,
        handlePause,
        handleSeek,
        handleSkip,
        handleNext,
        handlePrev,
        timeline,
    };

    return (
        <PlayerContext.Provider value={context}>
            <audio ref={audioRef} src={currentSong?.audioSrc} preload="metadata" />

            {children}
        </PlayerContext.Provider>
    );
};

export const usePlayerContext = (): PlayerContextValue => {
    const context = useContext(PlayerContext);

    if (context === null || context === undefined) {
        throw new Error('usePlayerContext must be used within a PlayerProvider');
    }

    return context;
};
