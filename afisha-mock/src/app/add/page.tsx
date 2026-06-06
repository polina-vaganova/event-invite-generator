"use client";

import { useState } from "react";
import Link from "next/link";
import type { AfishaEvent } from "@/lib/types";
import { categoryLabel } from "@/lib/categories";

export default function AddEventPage() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [event, setEvent] = useState<AfishaEvent | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setEvent(null);
    try {
      const res = await fetch("/api/parse", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Не удалось добавить событие");
      setEvent(data as AfishaEvent);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-10">
      <h1 className="text-3xl font-extrabold tracking-tight">Добавить событие</h1>
      <p className="mt-2 text-muted">
        Вставьте ссылку на любое событие afisha.ru — мы добавим его в каталог.
        Так сервис работает с любым событием, а не только из подборки.
      </p>

      <form onSubmit={handleSubmit} className="mt-6 flex flex-col gap-3 sm:flex-row">
        <input
          type="url"
          required
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://www.afisha.ru/concert/..."
          className="flex-1 rounded-full border border-border px-5 py-3 outline-none focus:border-accent"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-full bg-accent px-6 py-3 font-semibold text-white transition hover:bg-accent-hover disabled:opacity-60"
        >
          {loading ? "Парсим…" : "Добавить"}
        </button>
      </form>

      {error && (
        <p className="mt-4 rounded-xl bg-accent/10 px-4 py-3 text-sm text-accent">
          {error}
        </p>
      )}

      {event && (
        <div className="mt-8">
          <p className="mb-3 text-sm font-medium text-green-600">
            ✓ Событие добавлено в каталог
          </p>
          <Link
            href={`/event/${event.id}`}
            className="flex gap-4 rounded-2xl border border-border p-4 transition hover:border-accent"
          >
            {event.image && (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={event.image}
                alt={event.title}
                className="h-32 w-24 shrink-0 rounded-lg object-cover"
              />
            )}
            <div className="flex flex-col gap-1">
              <span className="text-xs text-muted">
                {categoryLabel(event.category).emoji} {categoryLabel(event.category).label}
              </span>
              <h3 className="font-semibold">{event.title}</h3>
              {event.date && <p className="text-sm text-muted">{event.date}</p>}
              {event.venue && <p className="text-sm text-muted">{event.venue}</p>}
              <span className="mt-1 text-sm text-accent">Открыть событие →</span>
            </div>
          </Link>
        </div>
      )}
    </div>
  );
}
