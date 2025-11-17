import { TimeOfDate } from '@/api/trips';

export const TIME_OF_DAY_OPTIONS = [
    { value: TimeOfDate.morning, label: 'Утро' },
    { value: TimeOfDate.day, label: 'День' },
    { value: TimeOfDate.evening, label: 'Вечер' },
    { value: TimeOfDate.night, label: 'Ночь' },
]

export const DURATION_OPTIONS = [
    { value: 'one', label: '1 час' },
    { value: 'two', label: '2-3 часа' },
    { value: 'four', label: '4+ часа' },
]

export const MOOD_OPTIONS = [
    { value: 'romantic', label: 'Романтичное' },
    { value: 'inspiring', label: 'Вдохновляющее' },
    { value: 'curious', label: 'Любознательное' },
    { value: 'peaceful', label: 'Спокойное' },
    { value: 'exploratory', label: 'Исследовательское' },
    { value: 'mystical', label: 'Мистическое' },
];