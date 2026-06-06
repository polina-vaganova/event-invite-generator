/**
 * Обновляет каталог из Афиши: парсит список ссылок и пишет события в БД.
 *
 * Запуск: npx tsx scripts/refresh-catalog.ts
 *
 * ⚠️ Обращается к afisha.ru — запускать редко и одному человеку.
 * После обновления сделайте снимок: npx tsx scripts/export-catalog.ts
 * и закоммитьте обновлённый prisma/seed-data.json.
 *
 * Идемпотентный: события, которые уже есть в каталоге, пропускаются.
 */
import { parseAfishaEvent, eventIdFromUrl } from "../src/lib/parser";
import { addEvent, getEvent } from "../src/lib/store";
import { prisma } from "../src/lib/prisma";

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
  console.log("Не забудьте: npx tsx scripts/export-catalog.ts — обновить seed-data.json");
  await prisma.$disconnect();
}

main();
