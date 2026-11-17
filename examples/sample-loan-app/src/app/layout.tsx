export default function Root({children}) {
  return (<html><head>
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXX"></script>
    <script dangerouslySetInnerHTML={{__html:`fbq('init','123');`}} />
    <script src="https://static.hotjar.com/c/hotjar-123.js"></script>
  </head><body>{children}</body></html>);
}
