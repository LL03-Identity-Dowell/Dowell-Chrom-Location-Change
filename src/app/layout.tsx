import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Location Specific Search",
  description: "seach for locations of specific things",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`flex w-screen h-screen flex-col overflow-x-hidden justify-stretch items-stretch px-36 py-20 bg-[#F3F4F6]`}>
        <main className={`grow`}>{children}</main>
      </body>
    </html>
  );
}
