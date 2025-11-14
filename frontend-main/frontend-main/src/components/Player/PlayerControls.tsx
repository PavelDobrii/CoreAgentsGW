import { usePlayerContext } from '@/contexts';
import { ChevronFirst, ChevronLast, Pause, Play, RotateCcw, RotateCw } from 'lucide-react';
import { ActionIcon, Flex } from '@mantine/core';

export const PlayerControls = () => {
    const { isPlaying, handlePlay, handlePause, handleSkip, handleNext, handlePrev } = usePlayerContext();

    const togglePlay = isPlaying ? handlePause : handlePlay;

    return (
        <Flex justify="space-between" align="center" gap="md">
            <ActionIcon size="36px" variant="light" color="dark" onClick={() => handleSkip(-10)}>
                <RotateCcw size={16} />
            </ActionIcon>
            <ActionIcon size="40px" variant="light"  color="dark" onClick={handlePrev}>
                <ChevronFirst size={20} />
            </ActionIcon>
            <ActionIcon size="48px" variant="light" color="dark" onClick={togglePlay}>
                {isPlaying
                    ? <Pause size={24} />
                    : <Play size={24} />
                }
            </ActionIcon>
            <ActionIcon size="40px" variant="light"  color="dark" onClick={handleNext}>
                <ChevronLast size={20} />
            </ActionIcon>
            <ActionIcon size="36px" variant="light"  color="dark" onClick={() => handleSkip(10)}>
                <RotateCw size={16} />
            </ActionIcon>
        </Flex>
    );
};