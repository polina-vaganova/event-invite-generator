import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto flex max-w-md flex-col items-center px-4 py-24 text-center">
      <div className="text-6xl font-extrabold text-accent">404</div>
      <h1 className="mt-4 text-2xl font-bold">Событие не найдено</h1>
      <p className="mt-2 text-muted">
        Возможно, ссылка устарела или событие ещё не добавлено в каталог.
      </p>
      <Link
        href="/"
        className="mt-6 rounded-full bg-accent px-6 py-3 font-semibold text-white transition hover:bg-accent-hover"
      >
        Ко всем событиям
      </Link>
    </div>
  );
}
