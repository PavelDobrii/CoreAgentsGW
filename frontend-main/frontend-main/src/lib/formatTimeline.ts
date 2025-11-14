export const formatTimeline = (time: number) => {
    if (Number.isNaN(time) || time === 0) {
        return '';
    }

    return `${Math.floor(time / 60)
        .toString()
        .padStart(2, '0')}:${Math.floor(time % 60)
        .toString()
        .padStart(2, '0')}`;
}