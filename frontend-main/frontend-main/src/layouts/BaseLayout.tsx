import { Link, Outlet } from 'react-router';
import { Fragment } from 'react';
import { Footer, FooterPlayer } from '@/components/Footer';
import { useHeaderContext, usePlayerContext } from '@/contexts';
import { Box, Space, Text } from '@mantine/core';
import Logo from '/logo.svg';

export const BaseLayout = () => {
    const { currentSong } = usePlayerContext();

    const { config } = useHeaderContext();
    const { action, title } = config;

    const getContent = () => {
        if (title) {
            return (
                <h1 style={{ flex: 1 }}>
                    <Text size="md" fw={700}>{title}</Text>
                </h1>
            );
        }

        return action || <Space />;
    };

    return (
        <Fragment>
            <header>
                {getContent()}

                <Link to="/trips">
                    <img src={Logo} width={60} height="auto" alt="Gowee" />
                </Link>
            </header>

            <main>
                <Box pb={currentSong ? '132px' : '80px'}>
                    <Outlet />
                </Box>
            </main>

            <FooterPlayer />
            <Footer />
        </Fragment>
    );
};
