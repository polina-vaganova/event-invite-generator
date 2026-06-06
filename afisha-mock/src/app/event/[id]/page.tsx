import Link from "next/link";
import { notFound } from "next/navigation";
import { getEvent } from "@/lib/store";
import { categoryLabel } from "@/lib/categories";
import { inviteUrl } from "@/lib/config";

export async function generateMetadata(props: PageProps<"/event/[id]">) {
  const { id } = await props.params;
  const event = await getEvent(id);
  return { title: event ? `${event.title} — Афиша` : "Событие не найдено" };
}

export default async function EventPage(props: PageProps<"/event/[id]">) {
  const { id } = await props.params;
  const event = await getEvent(id);
  if (!event) notFound();

  const { label, emoji } = categoryLabel(event.category);

  // Поля для блока характеристик — показываем только заполненные.
  const facts: [string, string | undefined][] = [
    ["Дата", event.date],
    ["Место", event.venue],
    ["Жанр", event.genres?.join(", ")],
    ["Длительность", event.duration],
    ["Страна", event.country],
    ["Возраст", event.ageRating],
    ["Режиссёр", event.director],
    ["Оригинал", event.originalTitle],
  ];

  return (
    <div className="mx-auto max-w-5xl px-4 py-8">
      <Link href="/" className="text-sm text-muted hover:text-foreground">
        ← Все события
      </Link>

      <div className="mt-4 grid gap-8 md:grid-cols-[320px_1fr]">
        {/* Постер */}
        <div className="overflow-hidden rounded-2xl border border-border bg-border">
          {event.image ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={event.image}
              alt={event.title}
              className="aspect-[3/4] w-full object-cover"
            />
          ) : (
            <div className="flex aspect-[3/4] items-center justify-center text-6xl">
              {emoji}
            </div>
          )}
        </div>

        {/* Инфо */}
        <div className="flex flex-col">
          <span className="mb-2 inline-flex w-fit items-center gap-1 rounded-full bg-border px-3 py-1 text-sm">
            {emoji} {label}
            {event.rating && (
              <span className="ml-2 font-bold text-accent">★ {event.rating}</span>
            )}
          </span>

          <h1 className="text-3xl font-extrabold leading-tight tracking-tight">
            {event.title}
          </h1>

          {event.price && (
            <p className="mt-3 text-lg font-semibold">{event.price}</p>
          )}

          {event.description && (
            <p className="mt-4 whitespace-pre-line text-[15px] leading-relaxed text-foreground/80">
              {event.description}
            </p>
          )}

          <dl className="mt-6 grid grid-cols-1 gap-x-8 gap-y-2 sm:grid-cols-2">
            {facts
              .filter(([, value]) => value)
              .map(([key, value]) => (
                <div key={key} className="flex justify-between gap-4 border-b border-border py-2 text-sm">
                  <dt className="text-muted">{key}</dt>
                  <dd className="text-right font-medium">{value}</dd>
                </div>
              ))}
          </dl>

          {/* Главный CTA — точка входа в наш продукт */}
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <a
              href={inviteUrl(event.id)}
              className="inline-flex items-center justify-center gap-2 rounded-full bg-accent px-6 py-3 font-semibold text-white transition hover:bg-accent-hover"
            >
              ✨ Позвать друга
            </a>
            <a
              href={event.sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center rounded-full border border-border px-6 py-3 font-medium transition hover:border-foreground"
            >
              Купить билеты
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
