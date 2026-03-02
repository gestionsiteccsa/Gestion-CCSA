/**
 * Configuration Tailwind CSS - CCSA Connect
 * 
 * Ce fichier contient la configuration personnalisée de Tailwind CSS
 * pour l'application CCSA Connect.
 * 
 * @see https://tailwindcss.com/docs/configuration
 */

tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#E6F2FF',
                    100: '#CCE5FF',
                    200: '#99CBFF',
                    300: '#66B0FF',
                    400: '#3396FF',
                    500: '#0066CC',
                    600: '#0052A3',
                    700: '#003D7A',
                    800: '#002952',
                    900: '#001429',
                },
                secondary: {
                    50: '#E6F7F0',
                    100: '#CCEFE1',
                    200: '#99DFC3',
                    300: '#66CFA5',
                    400: '#33BF87',
                    500: '#00A86B',
                    600: '#008656',
                    700: '#006540',
                    800: '#00432B',
                    900: '#002215',
                },
                accent: {
                    50: '#F0FBE6',
                    100: '#E1F7CC',
                    200: '#C3EF99',
                    300: '#A5E766',
                    400: '#87DF33',
                    500: '#7ED321',
                    600: '#65A91A',
                    700: '#4C7F14',
                    800: '#32550D',
                    900: '#192A07',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            },
        },
    },
}
