/**
 * Ручная проверка парсера на реальных страницах afisha.ru.
 * Запуск: npx tsx scripts/test-parser.ts [url1] [url2] ...
 */
import { parseAfishaEvent } from "../src/lib/parser";

const DEFAULT_URLS = [
  "https://www.afisha.ru/movie/pobeg-iz-volshebnogo-izmereniya-1003341/",
];

async function main() {
  const urls = process.argv.slice(2);
  const targets = urls.length ? urls : DEFAULT_URLS;

  for (const url of targets) {
    console.log("\n========================================");
    console.log("URL:", url);
    try {
      const event = await parseAfishaEvent(url);
      console.log(JSON.stringify(event, null, 2));
    } catch (err) {
      console.error("ОШИБКА:", (err as Error).message);
    }
  }
}

main();
