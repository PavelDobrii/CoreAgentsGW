export type SongItem = {
    id: string;
    title: string;
    audioSrc: string;
    posterSrc: string;
    duration?: string;
    address?: string;
    text?: string;
    order?: number;
    location?: { lat: number; lng: number }
}

export type Songs = Array<SongItem>

export type PlayerContextValue = {
    songs: Songs;
    initPlayer: (songs: Songs) => void;
    currentSong: SongItem | null;
    onPlay: (song: SongItem) => void;
    isPlaying: boolean;
    handlePlay: () => void;
    handlePause: () => void;
    handleSeek: (percent: number) => void;
    handleSkip: (amount: number) => void;
    handleNext: () => void;
    handlePrev: () => void;

    timeline: {
        duration: number;
        currentTime: number;
    }
}
