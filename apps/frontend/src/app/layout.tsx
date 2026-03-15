import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Nav } from "@/components/Nav";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Discursiva",
  description: "Correção assíncrona de respostas discursivas",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" className={inter.className}>
      <body className="min-h-screen bg-slate-50 text-gray-900">
        <header className=" top-0 z-30">
          <div className="mx-auto max-w-4xl pl-3 pr-4 sm:pr-6 py-3 flex items-center justify-between">
            <Nav />
          </div>
        </header>
        <main className="mx-auto max-w-4xl px-4 sm:px-6 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
