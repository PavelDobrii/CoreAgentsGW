import { type FC, type MouseEvent } from 'react';
import { Flex, Progress, Text } from '@mantine/core';
import { usePlayerContext } from '@/contexts';
import { formatTimeline } from '@/lib';

type Props = {
    mini?: boolean;
    className?: string;
};

export const PlayerProgressBar: FC<Props> = ({ mini, className }) => {
    const { timeline, handleSeek } = usePlayerContext();

    const progress = timeline?.duration
        ? timeline.currentTime / timeline.duration
        : 0;

    const handleClick = (e: MouseEvent<HTMLDivElement>) => {
        if (!timeline?.duration) return;

        const rect = e.currentTarget.getBoundingClientRect();
        const clickX = e.clientX - rect.left;
        const percent = clickX / rect.width;
        handleSeek(Math.min(Math.max(percent, 0), 1));
    };

    if (mini) {
        return (
            <div className={className}>
                <Progress size={4} value={progress * 100} />
            </div>
        );
    }

    return (
        <div>
            <Progress value={progress * 100} onClick={handleClick} />

            <Flex justify="space-between">
                <Text size="sm">{formatTimeline(timeline?.currentTime)}</Text>
                <Text size="sm">{formatTimeline(timeline?.duration)}</Text>
            </Flex>
        </div>
    );
};
