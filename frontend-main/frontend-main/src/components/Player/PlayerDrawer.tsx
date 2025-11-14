import { usePlayerContext } from '@/contexts';
import { PlayerProgressBar, PlayerControls } from '@/components/Player';
import { Drawer, type DrawerProps, Stack, Text, Image, Spoiler } from '@mantine/core';

export const PlayerDrawer = (props: DrawerProps) => {
    const { currentSong } = usePlayerContext();
    if (!currentSong) {
        return null;
    }

    const [artist, songName] = currentSong.title.split('-')

    return (
        <Drawer {...props}>
                <Image
                    radius="md"
                    src={currentSong?.posterSrc}
                    alt={currentSong?.title}
                    width="100%"
                    height={280}
                />

                <Stack gap="0">
                    <Text size="lg">{artist}</Text>
                    <Text size="sm">{songName}</Text>
                </Stack>

                <PlayerProgressBar />
                <PlayerControls />

                <Spoiler maxHeight={24} showLabel="Show more" hideLabel="Hide">
                    {currentSong.text}
                </Spoiler>
        </Drawer>
    );
};
