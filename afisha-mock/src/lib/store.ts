import type { Event as EventRow } from "@prisma/client";
import { prisma } from "./prisma";
import type { AfishaEvent } from "./types";

/**
 * Хранилище каталога событий на Postgres (через Prisma).
 *
 * Имитирует базу данных Афиши: хранит спарсенные события и позволяет добавлять
 * новые (фича «добавить по ссылке»). Интерфейс — `getAllEvents/getEvent/addEvent`;
 * благодаря этому остальной код (API, страницы, генератор) не зависит от того,
 * что под капотом — раньше был JSON-файл, теперь настоящая БД.
 */

/** Строка БД → контракт AfishaEvent (null → undefined, дата → ISO-строка). */
function toEvent(row: EventRow): AfishaEvent {
  return {
    id: row.id,
    slug: row.slug,
    sourceUrl: row.sourceUrl,
    category: row.category,
    title: row.title,
    originalTitle: row.originalTitle ?? undefined,
    image: row.image ?? undefined,
    description: row.description ?? undefined,
    genres: row.genres.length ? row.genres : undefined,
    date: row.date ?? undefined,
    country: row.country ?? undefined,
    duration: row.duration ?? undefined,
    ageRating: row.ageRating ?? undefined,
    director: row.director ?? undefined,
    venue: row.venue ?? undefined,
    price: row.price ?? undefined,
    rating: row.rating ?? undefined,
    parsedAt: row.parsedAt.toISOString(),
  };
}

/** Поля события для записи в БД (без id и служебных дат). */
function toRowData(event: AfishaEvent) {
  return {
    slug: event.slug,
    sourceUrl: event.sourceUrl,
    category: event.category,
    title: event.title,
    originalTitle: event.originalTitle ?? null,
    image: event.image ?? null,
    description: event.description ?? null,
    genres: event.genres ?? [],
    date: event.date ?? null,
    country: event.country ?? null,
    duration: event.duration ?? null,
    ageRating: event.ageRating ?? null,
    director: event.director ?? null,
    venue: event.venue ?? null,
    price: event.price ?? null,
    rating: event.rating ?? null,
    parsedAt: new Date(event.parsedAt),
  };
}

/** Все события каталога (новые — первыми). */
export async function getAllEvents(): Promise<AfishaEvent[]> {
  const rows = await prisma.event.findMany({ orderBy: { createdAt: "desc" } });
  return rows.map(toEvent);
}

/** Одно событие по ID или undefined. */
export async function getEvent(id: string): Promise<AfishaEvent | undefined> {
  const row = await prisma.event.findUnique({ where: { id } });
  return row ? toEvent(row) : undefined;
}

/**
 * Добавляет (или обновляет) событие в каталоге и возвращает его.
 * upsert по id — повторное добавление той же ссылки просто обновит данные.
 */
export async function addEvent(event: AfishaEvent): Promise<AfishaEvent> {
  const data = toRowData(event);
  const row = await prisma.event.upsert({
    where: { id: event.id },
    create: { id: event.id, ...data },
    update: data,
  });
  return toEvent(row);
}
