import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  metadataBase: new URL("https://ai-job-exposure.setiyaputra.me"),
  title: "TaskFolio - See which tasks AI will automate in your job",
  description: "Task-level AI exposure analysis for 361 Australian occupations. See exactly which parts of your job AI will affect, when it will happen, and how much impact it will have. Built with data from 1M real AI conversations.",
  keywords: ["AI job impact", "automation", "task analysis", "Australian jobs", "ANZSCO", "job automation", "AI exposure"],
  icons: {
    icon: [
      { url: "/favicon.ico", sizes: "any" },
      { url: "/favicon-32.png", sizes: "32x32", type: "image/png" },
      { url: "/favicon-16.png", sizes: "16x16", type: "image/png" },
    ],
    apple: "/apple-touch-icon.png",
  },
  openGraph: {
    title: "TaskFolio - Task-level AI exposure for Australian jobs",
    description: "See which specific tasks in your job AI will automate, and when. 361 occupations, 6,690 tasks analyzed.",
    type: "website",
    url: "https://ai-job-exposure.setiyaputra.me",
    images: [
      {
        url: "/preview.png",
        width: 1200,
        height: 630,
        alt: "TaskFolio - See which tasks AI will automate",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "TaskFolio - See which tasks AI will automate",
    description: "Task-level AI impact analysis for 361 Australian occupations. Built with 1M real AI conversations.",
    images: ["/preview.png"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Theme script - runs before React to prevent flash */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  var d = document.documentElement;
                  var theme = localStorage.getItem('theme');
                  if (theme === 'dark') {
                    d.classList.add('dark');
                    d.classList.remove('light');
                  } else if (theme === 'light') {
                    d.classList.add('light');
                    d.classList.remove('dark');
                  } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
                    d.classList.add('dark');
                    d.classList.remove('light');
                  } else {
                    d.classList.add('light');
                    d.classList.remove('dark');
                  }
                } catch (e) {}
              })();
            `,
          }}
        />
        <script
          async
          src="https://www.googletagmanager.com/gtag/js?id=G-QFQSVC8FCK"
        />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-QFQSVC8FCK');
            `,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
