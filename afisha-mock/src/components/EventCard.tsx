import Link from "next/link";
import type { AfishaEvent } from "@/lib/types";
import { categoryLabel } from "@/lib/categories";

/** Карточка события в каталоге. Ведёт на страницу события /event/[id]. */
export default function EventCard({ event }: { event: AfishaEvent }) {
  const { label, emoji } = categoryLabel(event.category);
  const meta = [event.date, event.venue].filter(Boolean).join(" · ");

  return (
    <Link
      href={`/event/${event.id}`}
      className="group flex flex-col overflow-hidden rounded-2xl border border-border bg-card transition hover:-translate-y-1 hover:shadow-lg"
    >
      <div className="relative aspect-[3/4] overflow-hidden bg-border">
        {event.image ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={event.image}
            alt={event.title}
            className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
          />
        ) : (
          <div className="flex h-full items-center justify-center text-4xl">{emoji}</div>
        )}
        <span className="absolute left-3 top-3 rounded-full bg-background/90 px-2.5 py-1 text-xs font-medium backdrop-blur">
          {emoji} {label}
        </span>
        {event.rating && (
          <span className="absolute right-3 top-3 rounded-full bg-accent px-2 py-1 text-xs font-bold text-white">
            {event.rating}
          </span>
        )}
      </div>

      <div className="flex flex-1 flex-col gap-1 p-4">
        <h3 className="line-clamp-2 font-semibold leading-snug group-hover:text-accent">
          {event.title}
        </h3>
        {meta && <p className="line-clamp-1 text-sm text-muted">{meta}</p>}
        {event.price && <p className="mt-auto pt-2 text-sm font-medium">{event.price}</p>}
      </div>
    </Link>
  );
}
