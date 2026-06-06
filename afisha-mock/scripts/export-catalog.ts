/**
 * Снимок текущего каталога из БД в файл prisma/seed-data.json.
 *
 * Запуск: npx tsx scripts/export-catalog.ts
 *
 * Этот файл коммитится в репозиторий — из него команда наполняет БД
 * мгновенно и без обращения к Афише (см. scripts/seed.ts).
 */
import fs from "node:fs";
import path from "node:path";
import { prisma } from "../src/lib/prisma";
import type { AfishaEvent } from "../src/lib/types";

async function main() {
  const rows = await prisma.event.findMany({ orderBy: { createdAt: "asc" } });

  const events: AfishaEvent[] = rows.map((r) => ({
    id: r.id,
    slug: r.slug,
    sourceUrl: r.sourceUrl,
    category: r.category,
    title: r.title,
    originalTitle: r.originalTitle ?? undefined,
    image: r.image ?? undefined,
    description: r.description ?? undefined,
    genres: r.genres.length ? r.genres : undefined,
    date: r.date ?? undefined,
    country: r.country ?? undefined,
    duration: r.duration ?? undefined,
    ageRating: r.ageRating ?? undefined,
    director: r.director ?? undefined,
    venue: r.venue ?? undefined,
    price: r.price ?? undefined,
    rating: r.rating ?? undefined,
    parsedAt: r.parsedAt.toISOString(),
  }));

  const outFile = path.join(process.cwd(), "prisma", "seed-data.json");
  fs.writeFileSync(outFile, JSON.stringify(events, null, 2), "utf-8");
  console.log(`Экспортировано ${events.length} событий → ${outFile}`);
  await prisma.$disconnect();
}

main();
