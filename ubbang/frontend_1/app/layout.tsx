import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: "WhaT's your Feeling",
  description: 'Created with Ubbang',
  generator: 'team Ubbang',
  icons: {
    icon: '/favicon.ico', // ✅ public 경로 기준
  },
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  )
}
