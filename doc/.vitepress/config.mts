import {defineConfig} from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
    title: "Vmaker Document",
    description: "Tutorial video maker for Programmers. Based on Typer & FFMpeg.",
    themeConfig: {
        // https://vitepress.dev/reference/default-theme-config
        nav: [
            {text: 'Home', link: '/'},
            {text: 'Guides', link: '/guides/getting-started'},
            {text: 'API Reference', link: '/reference'}
        ],

        sidebar: [
            {
                text: 'Introduction',
                items: [
                    {text: 'Getting Started', link: '/guides/getting-started'},
                    {text: 'Basic Concepts', link: '/guides/basic-concepts'}
                ]
            }
        ],

        socialLinks: [
            {icon: 'github', link: 'https://github.com/gaojunran/vmaker'},
            {
                icon: {
                    svg: '<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"><path fill="currentColor" d="M11.427 16.615v-6.042c0-.997-.444-1.669-1.541-1.669c-.906 0-1.754.614-2.159 1.228v6.483H5.704v-6.042c0-.997-.423-1.669-1.523-1.669c-.905 0-1.734.633-2.158 1.228v6.483H0V7.351h2.023v1.247C2.428 8.04 3.642 7.12 5.068 7.12c1.386 0 2.235.69 2.543 1.688c.52-.825 1.754-1.688 3.16-1.688c1.697 0 2.68.92 2.68 2.8v6.694zM24 12.163c0-2.925-1.788-5.042-4.604-5.042c-2.777 0-4.759 2.174-4.759 4.869c0 2.945 2.079 4.888 4.913 4.89c1.476 0 2.855-.482 3.807-1.368l-.932-1.328c-.68.673-1.747 1.04-2.68 1.04c-1.768 0-2.815-1.174-2.971-2.56H24zm-7.245-.943c.077-1.116.893-2.444 2.622-2.444c1.845 0 2.602 1.347 2.66 2.444z"/></svg>'
                }, link: 'https://gaojunran.fun/'
            }
        ]
    }
})
