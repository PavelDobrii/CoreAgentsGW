import { Fragment, type MouseEvent, useMemo } from 'react';
import { Pause, Play } from 'lucide-react';
import { usePlayerContext } from '@/contexts';
import { formatTimeline } from '@/lib';
import { PlayerProgressBar, PlayerDrawer } from '@/components/Player';
import { ActionIcon, Flex, Image, Text } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import styles from './FooterPlayer.module.css';

export const FooterPlayer = () => {
    const [opened, { open, close }] = useDisclosure(false);

    const { isPlaying, currentSong, handlePlay, handlePause, timeline } = usePlayerContext();


    const formatedTimeline = useMemo(() => {
        const currentTime = formatTimeline(timeline.currentTime)
        const duration = formatTimeline(timeline.duration)

        if (!currentTime || !duration) {
            return '00:00'
        }

        return `${currentTime} / ${duration}`;
    }, [timeline])

    if (!currentSong) return null;

    const togglePlay = (e?: MouseEvent<HTMLButtonElement>) =>{
        e?.stopPropagation();

        if (isPlaying) {
            handlePause()
            return
        }

        handlePlay()
    };

    return (
        <Fragment>
            <PlayerDrawer opened={opened} onClose={close} title={currentSong.address} />

            <div className={styles.footerPlayer} onClick={open}>
                <div className={styles.inner}>
                    <Image
                        src={currentSong.posterSrc}
                        alt={currentSong.title}
                        h={40}
                        w={40}
                        fit="cover"
                        radius="xs"
                    />

                    <Flex flex={1} direction="column" miw={0}>
                        <Text flex={1} size="sm" truncate="end">{currentSong.title}</Text>
                        {formatedTimeline && (<Text size="xs">{formatedTimeline}</Text>)}
                    </Flex>

                    <ActionIcon size="40px" variant="light" color="dark" aria-label="Toggle Play" onClick={togglePlay}>
                        {isPlaying ? <Pause size={20} /> : <Play size={20} />}
                    </ActionIcon>

                    <PlayerProgressBar mini className={styles.progressBar} />
                </div>
            </div>
        </Fragment>
    );
};

