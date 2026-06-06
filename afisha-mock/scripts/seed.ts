/**
 * Наполняет каталог мини-Афиши реальными событиями afisha.ru.
 *
 * Запуск: npx tsx scripts/seed.ts
 *
 * Идемпотентный: события, которые уже есть в каталоге, пропускаются — парсятся
 * только недостающие. Между запросами держим паузу. Так повторный прогон не
 * бомбит Афишу лишними запросами и не вызывает блокировок.
 */
import { parseAfishaEvent, eventIdFromUrl } from "../src/lib/parser";
import { addEvent, getEvent } from "../src/lib/store";
import { prisma } from "../src/lib/prisma";

// Курируемый список разнообразных событий (кино, концерты, спектакли, выставки).
const SEED_URLS = [
  "https://www.afisha.ru/movie/pobeg-iz-volshebnogo-izmereniya-1003341/",
  "https://www.afisha.ru/concert/basta-6014552/",
  "https://www.afisha.ru/concert/shoumen-sergey-lazarev-6003723/",
  "https://www.afisha.ru/concert/piknik-afishi-h-sber-moskva-6016262/",
  "https://www.afisha.ru/performance/nash-klass-1006219/",
  "https://www.afisha.ru/performance/opus-48-ostrovskiy-1004230/",
  "https://www.afisha.ru/exhibition/zagadochnye-miry-ieronima-bosha-frida-kalo-neslomlennaya-1009037/",
  "https://www.afisha.ru/exhibition/dom-21-v-gostyah-u-hudozhnikov-1009362/",
];

const DELAY_MS = 1500; // вежливая пауза между запросами к Афише
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

async function main() {
  let added = 0;
  let skipped = 0;
  let failed = 0;

  for (const url of SEED_URLS) {
    // Уже в каталоге — не дёргаем Афишу повторно.
    if (await getEvent(eventIdFromUrl(url))) {
      skipped++;
      console.log(`• уже в каталоге: ${eventIdFromUrl(url)}`);
      continue;
    }
    try {
      const event = await addEvent(await parseAfishaEvent(url));
      added++;
      console.log(`✓ [${event.category}] ${event.title}`);
      await sleep(DELAY_MS);
    } catch (err) {
      failed++;
      console.error(`✗ ${url}\n  ${(err as Error).message}`);
    }
  }

  console.log(`\nДобавлено: ${added}, пропущено: ${skipped}, ошибок: ${failed}`);
  await prisma.$disconnect();
}

main();
