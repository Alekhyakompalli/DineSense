import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Zomato AI DineSense — Sensory Intelligence",
  description:
    "AI-Powered Restaurant Recommendation System with multi-modal intent reasoning, Google Gemini synthesis, and preprocessed Zomato datasets.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin=""
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
          rel="stylesheet"
        />
      </head>
      <body className="bg-background font-body-md text-on-surface min-h-screen selection:bg-primary-container selection:text-on-primary-container">
        {children}
      </body>
    </html>
  );
}

