import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "cyrillic"],
});

export const metadata: Metadata = {
  title: "Афиша — события Москвы",
  description: "Кино, концерты, спектакли и выставки",
};

const NAV = [
  { label: "Кино", href: "/" },
  { label: "Концерты", href: "/" },
  { label: "Спектакли", href: "/" },
  { label: "Выставки", href: "/" },
];

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ru" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-background text-foreground">
        <header className="border-b border-border sticky top-0 z-20 bg-background/90 backdrop-blur">
          <div className="mx-auto max-w-6xl px-4 h-16 flex items-center gap-6">
            <Link href="/" className="text-2xl font-extrabold tracking-tight text-accent">
              Афиша
            </Link>
            <nav className="hidden md:flex items-center gap-5 text-sm text-muted">
              {NAV.map((item, i) => (
                <Link key={i} href={item.href} className="hover:text-foreground transition">
                  {item.label}
                </Link>
              ))}
            </nav>
            <Link
              href="/add"
              className="ml-auto text-sm font-medium rounded-full border border-border px-4 py-2 hover:border-accent hover:text-accent transition"
            >
              + Добавить событие
            </Link>
          </div>
        </header>

        <main className="flex-1">{children}</main>

        <footer className="border-t border-border mt-16">
          <div className="mx-auto max-w-6xl px-4 py-8 text-xs text-muted leading-relaxed">
            Прототип для хакатона «Креаторы и Кодеры». Данные о событиях получены из
            публичных страниц afisha.ru в учебных целях. Это не официальный сайт Афиши.
          </div>
        </footer>
      </body>
    </html>
  );
}
