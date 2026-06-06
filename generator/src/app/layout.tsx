import type { Metadata } from "next";
import { Inter, Caveat } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "cyrillic"],
});

// Рукописный шрифт для текста открытки
const caveat = Caveat({
  variable: "--font-caveat",
  subsets: ["latin", "cyrillic"],
});

export const metadata: Metadata = {
  title: "Позвать красиво — Афиша",
  description: "Открытка-приглашение на событие с текстом и визуалом от ИИ",
};

const NAV = ["События", "Места", "Кино", "Рестораны", "Музыка"];

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru" className={`${inter.variable} ${caveat.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        {/* Шапка в стиле Афиши — студия живёт «внутри» Афиши */}
        <header className="border-b border-border bg-background">
          <div className="mx-auto flex h-16 max-w-6xl items-center gap-7 px-4">
            <Link href="/" className="text-2xl font-black lowercase tracking-tight">
              афиша
            </Link>
            <nav className="hidden items-center gap-5 text-sm font-medium md:flex">
              {NAV.map((item) => (
                <span key={item} className="cursor-default text-foreground/70">
                  {item}
                </span>
              ))}
              <span className="cursor-default text-foreground/70">Ещё ▾</span>
            </nav>
            <div className="ml-auto flex items-center gap-4 text-sm text-foreground/70">
              <span className="hidden cursor-default sm:inline">♡ Избранное</span>
              <span className="cursor-default">⌕</span>
              <span className="h-8 w-8 rounded-full bg-gradient-to-br from-accent to-accent-2" />
            </div>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="mt-16 border-t border-border">
          <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-muted">
            Прототип для хакатона «Креаторы и Кодеры» · кейс Afisha.ru · данные событий с
            публичных страниц afisha.ru в учебных целях
          </div>
        </footer>
      </body>
    </html>
  );
}
