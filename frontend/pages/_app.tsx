/**
 * pages/_app.tsx
 * Next.js custom App – global styles + layout wrapper.
 */
import type { AppProps } from "next/app";
import "@/styles/globals.css";

export default function App({ Component, pageProps }: AppProps) {
  return <Component {...pageProps} />;
}
