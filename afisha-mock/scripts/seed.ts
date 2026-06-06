/**
 * Наполняет каталог мини-Афиши из готового снимка prisma/seed-data.json.
 *
 * Запуск: npx tsx scripts/seed.ts
 *
 * НЕ обращается к Афише — берёт заранее сохранённые события из файла.
 * Это команда для setup'а: быстро, надёжно, без риска блокировок.
 * Чтобы обновить каталог из Афиши, см. scripts/refresh-catalog.ts.
 */
import fs from "node:fs";
import path from "node:path";
import { addEvent } from "../src/lib/store";
import { prisma } from "../src/lib/prisma";
import type { AfishaEvent } from "../src/lib/types";

async function main() {
  const file = path.join(process.cwd(), "prisma", "seed-data.json");
  const events = JSON.parse(fs.readFileSync(file, "utf-8")) as AfishaEvent[];

  for (const event of events) {
    await addEvent(event);
    console.log(`✓ [${event.category}] ${event.title}`);
  }

  console.log(`\nЗагружено ${events.length} событий из seed-data.json (без обращения к Афише)`);
  await prisma.$disconnect();
}

main();
