import { usePlayerContext } from '@/contexts';
import { PlayerProgressBar, PlayerControls } from '@/components/Player';
import { Drawer, type DrawerProps, Stack, Text, Image, Spoiler, Flex } from '@mantine/core';
import { ChevronDown, ChevronUp } from 'lucide-react';

export const PlayerDrawer = (props: DrawerProps) => {
    const { currentSong } = usePlayerContext();
    if (!currentSong) {
        return null;
    }

    const [artist, songName] = currentSong.title.split('-');

    return (
        <Drawer styles={{ body: { padding: 0 } }} {...props}>
            <Image
                src={currentSong?.posterSrc}
                alt={currentSong?.title}
                width="100%"
                height={280}
            />

            <Stack px="md">
                <Stack gap="0">
                    <Text size="lg">{artist}</Text>
                    <Text size="sm">{songName}</Text>
                </Stack>

                <PlayerProgressBar />
                <PlayerControls />

                <Spoiler
                    maxHeight={48}
                    showLabel={(
                        <Flex c="dimmed" align="center" gap={4} pb="xl">
                            <ChevronDown size={22} /><Text>Показать</Text>
                        </Flex>
                    )}
                    hideLabel={(
                        <Flex c="dimmed" align="center" gap={4} pb="xl">
                            <ChevronUp size={22} /><Text>Скрыть</Text>
                        </Flex>
                    )}
                >
                    {currentSong.text}
                </Spoiler>
            </Stack>
        </Drawer>
    );
};
