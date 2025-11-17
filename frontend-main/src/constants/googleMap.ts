import type { CSSProperties } from 'react';

export const MAP_LIBRARIES: ('geometry' | 'places')[] = ['geometry', 'places'];
export const FALLBACK_CENTER = { lat: 52.2296756, lng: 21.0122287 };
export const MAP_CONTAINER_STYLE = {
    // borderRadius: 'var(--mantine-radius-md)',
    width: '100%',
    minHeight: '400px',
    flex: 1
};
export const MARKER_STYLE: CSSProperties = {
    position: 'absolute',
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -100%)',
    fontSize: 24,
    pointerEvents: 'none',
};
export const GOOGLE_MAP_OPTIONS = {
    gestureHandling: 'greedy',

    // mapTypeControl: false,
    // streetViewControl: false,
    // fullscreenControl: false,
    disableDefaultUI: true,
    zoomControl: true,

    clickableIcons: false,
}

export const GOOGLE_MAP_LANGUAGES = [
    { code: 'ru', label: 'Russian', value: 'ru-RU' },
    { code: 'en', label: 'English', value: 'en-US' },
]

// export const GOOGLE_MAP_LANGUAGES = [
//     { code: 'af', label: 'Afrikaans', value: 'af-ZA' },
//     { code: 'ar', label: 'Arabic', value: 'ar-SA' },
//     { code: 'az', label: 'Azerbaijani', value: 'az-AZ' },
//     { code: 'be', label: 'Belarusian', value: 'be-BY' },
//     { code: 'bg', label: 'Bulgarian', value: 'bg-BG' },
//     { code: 'bn', label: 'Bengali', value: 'bn-BD' },
//     { code: 'bs', label: 'Bosnian', value: 'bs-BA' },
//     { code: 'ca', label: 'Catalan', value: 'ca-ES' },
//     { code: 'cs', label: 'Czech', value: 'cs-CZ' },
//     { code: 'da', label: 'Danish', value: 'da-DK' },
//     { code: 'de', label: 'German', value: 'de-DE' },
//     { code: 'el', label: 'Greek', value: 'el-GR' },
//     { code: 'en', label: 'English', value: 'en-US' },
//     { code: 'es', label: 'Spanish', value: 'es-ES' },
//     { code: 'et', label: 'Estonian', value: 'et-EE' },
//     { code: 'fa', label: 'Persian (Farsi)', value: 'fa-IR' },
//     { code: 'fi', label: 'Finnish', value: 'fi-FI' },
//     { code: 'fr', label: 'French', value: 'fr-FR' },
//     { code: 'gl', label: 'Galician', value: 'gl-ES' },
//     { code: 'gu', label: 'Gujarati', value: 'gu-IN' },
//     { code: 'he', label: 'Hebrew', value: 'he-IL' },
//     { code: 'hi', label: 'Hindi', value: 'hi-IN' },
//     { code: 'hr', label: 'Croatian', value: 'hr-HR' },
//     { code: 'hu', label: 'Hungarian', value: 'hu-HU' },
//     { code: 'id', label: 'Indonesian', value: 'id-ID' },
//     { code: 'it', label: 'Italian', value: 'it-IT' },
//     { code: 'ja', label: 'Japanese', value: 'ja-JP' },
//     { code: 'ka', label: 'Georgian', value: 'ka-GE' },
//     { code: 'kk', label: 'Kazakh', value: 'kk-KZ' },
//     { code: 'kn', label: 'Kannada', value: 'kn-IN' },
//     { code: 'ko', label: 'Korean', value: 'ko-KR' },
//     { code: 'ky', label: 'Kyrgyz', value: 'ky-KG' },
//     { code: 'lt', label: 'Lithuanian', value: 'lt-LT' },
//     { code: 'lv', label: 'Latvian', value: 'lv-LV' },
//     { code: 'mk', label: 'Macedonian', value: 'mk-MK' },
//     { code: 'ml', label: 'Malayalam', value: 'ml-IN' },
//     { code: 'mn', label: 'Mongolian', value: 'mn-MN' },
//     { code: 'mr', label: 'Marathi', value: 'mr-IN' },
//     { code: 'ms', label: 'Malay', value: 'ms-MY' },
//     { code: 'my', label: 'Burmese', value: 'my-MM' },
//     { code: 'ne', label: 'Nepali', value: 'ne-NP' },
//     { code: 'nl', label: 'Dutch', value: 'nl-NL' },
//     { code: 'no', label: 'Norwegian', value: 'no-NO' },
//     { code: 'pa', label: 'Punjabi', value: 'pa-IN' },
//     { code: 'pl', label: 'Polish', value: 'pl-PL' },
//     { code: 'pt', label: 'Portuguese', value: 'pt-PT' },
//     { code: 'ro', label: 'Romanian', value: 'ro-RO' },
//     { code: 'ru', label: 'Russian', value: 'ru-RU' },
//     { code: 'si', label: 'Sinhala', value: 'si-LK' },
//     { code: 'sk', label: 'Slovak', value: 'sk-SK' },
//     { code: 'sl', label: 'Slovenian', value: 'sl-SI' },
//     { code: 'sr', label: 'Serbian', value: 'sr-RS' },
//     { code: 'sv', label: 'Swedish', value: 'sv-SE' },
//     { code: 'ta', label: 'Tamil', value: 'ta-IN' },
//     { code: 'te', label: 'Telugu', value: 'te-IN' },
//     { code: 'th', label: 'Thai', value: 'th-TH' },
//     { code: 'tr', label: 'Turkish', value: 'tr-TR' },
//     { code: 'uk', label: 'Ukrainian', value: 'uk-UA' },
//     { code: 'uz', label: 'Uzbek', value: 'uz-UZ' },
//     { code: 'vi', label: 'Vietnamese', value: 'vi-VN' },
//     { code: 'zh-CN', label: 'Chinese (Simplified)', value: 'zh-CN' },
//     { code: 'zh-TW', label: 'Chinese (Traditional)', value: 'zh-TW' },
// ];
