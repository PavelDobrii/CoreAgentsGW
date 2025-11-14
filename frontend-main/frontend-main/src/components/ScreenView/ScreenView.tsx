import type { FC, ReactNode } from 'react';
import styles from './ScreenView.module.css';

type ContentWrapperProps = {
    children: ReactNode;
    footerOptions?: {
        centered?: boolean;
        onRender: () => ReactNode;
    };
};

export const ScreenView: FC<ContentWrapperProps> = ({ children, footerOptions }) => {
    return (
        <main className={styles.screen}>
            <div className={styles.content}>
                {children}
            </div>

            {footerOptions && (
                <div className={styles.footer}>
                    <div
                        className={
                            footerOptions.centered
                                ? `${styles.footerInner} ${styles.footerCentered}`
                                : styles.footerInner
                        }
                    >
                        {footerOptions.onRender()}
                    </div>
                </div>
            )}
        </main>
    );
};
