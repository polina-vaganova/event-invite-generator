import * as cheerio from "cheerio";
import type { AfishaEvent } from "./types";

/**
 * Парсер событий afisha.ru.
 *
 * Достаёт данные из СТАБИЛЬНЫХ источников страницы, а не из случайной вёрстки:
 *   1. OpenGraph-теги (og:title, og:image, og:description) — есть почти везде,
 *      потому что нужны для превью при шаринге;
 *   2. JSON-LD (schema.org) — структурированные поля: жанр, дата, длительность и т.д.
 *
 * Это «костыль прототипа»: в реальном внедрении данные приходили бы из
 * внутреннего API Афиши. Здесь парсер играет роль наполнителя каталога.
 */

const USER_AGENT =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36";

/** Проверяет, что ссылка действительно ведёт на afisha.ru. */
export function isAfishaUrl(url: string): boolean {
  try {
    const host = new URL(url).hostname.replace(/^www\./, "");
    // afisha.ru и любые её поддомены (рестораны, спецпроекты и т.п.)
    return host === "afisha.ru" || host.endsWith(".afisha.ru");
  } catch {
    return false;
  }
}

/** Извлекает { id, slug, category } из пути URL афиши. */
function parseUrlParts(url: string): { id: string; slug: string; category: string } {
  const { pathname } = new URL(url);
  const segments = pathname.split("/").filter(Boolean);
  // напр. ["movie", "pobeg-iz-volshebnogo-izmereniya-1003341"]
  const category = segments[0] ?? "event";
  const last = segments[segments.length - 1] ?? "";
  const idMatch = last.match(/(\d+)$/);
  const id = idMatch ? idMatch[1] : last;
  const slug = last.replace(/-?\d+$/, "") || last;
  return { id, slug, category };
}

/** Достаёт ID события из ссылки afisha.ru (без сетевого запроса). */
export function eventIdFromUrl(url: string): string {
  return parseUrlParts(url).id;
}

/** Собирает все JSON-LD объекты со страницы в плоский список. */
function extractJsonLd($: cheerio.CheerioAPI): Record<string, unknown>[] {
  const blocks: Record<string, unknown>[] = [];
  $('script[type="application/ld+json"]').each((_, el) => {
    const raw = $(el).contents().text();
    if (!raw) return;
    try {
      const parsed = JSON.parse(raw);
      const items = Array.isArray(parsed) ? parsed : [parsed];
      for (const item of items) {
        if (item && typeof item === "object") {
          // @graph — частый контейнер в schema.org
          if (Array.isArray((item as Record<string, unknown>)["@graph"])) {
            blocks.push(
              ...((item as Record<string, unknown>)["@graph"] as Record<string, unknown>[]),
            );
          } else {
            blocks.push(item as Record<string, unknown>);
          }
        }
      }
    } catch {
      // битый JSON-LD молча пропускаем
    }
  });
  return blocks;
}

/** Возвращает массив строк-типов JSON-LD блока (@type бывает строкой или массивом). */
function ldTypes(block: Record<string, unknown>): string[] {
  const t = block["@type"];
  const arr = Array.isArray(t) ? t : [t];
  return arr.filter((x): x is string => typeof x === "string");
}

// Типы schema.org, которые описывают «событие/место, куда можно пойти».
// Покрывает кино, концерты, спектакли, выставки, рестораны, фестивали.
const EVENT_TYPE_RE =
  /Movie|Event|Theater|Theatre|Music|Exhibition|Screening|Festival|Comedy|Dance|Play|Visual|Sports|Restaurant|FoodEstablishment|Place|CreativeWork|Product/i;

// Служебные типы, которые НИКОГДА не являются самим событием.
const SERVICE_TYPE_RE = /BreadcrumbList|WebSite|WebPage|Organization|SearchAction/i;

/**
 * Выбирает главный JSON-LD блок страницы — описание самого события.
 * 1) сначала ищем блок с «событийным» типом;
 * 2) если нет — первый осмысленный блок с названием (не служебный).
 * Парсер остаётся универсальным для любой категории Афиши, а не только кино.
 */
function selectMainLd(blocks: Record<string, unknown>[]): Record<string, unknown> {
  const byEventType = blocks.find((b) =>
    ldTypes(b).some((t) => EVENT_TYPE_RE.test(t) && !SERVICE_TYPE_RE.test(t)),
  );
  if (byEventType) return byEventType;

  const byName = blocks.find(
    (b) => typeof b.name === "string" && !ldTypes(b).some((t) => SERVICE_TYPE_RE.test(t)),
  );
  return byName ?? {};
}

/** Нормализует поле, которое может быть строкой, объектом {name} или массивом таких. */
function pickName(value: unknown): string | undefined {
  if (!value) return undefined;
  if (typeof value === "string") return value.trim() || undefined;
  if (Array.isArray(value)) {
    const names = value.map(pickName).filter(Boolean) as string[];
    return names.length ? names.join(", ") : undefined;
  }
  if (typeof value === "object") {
    const name = (value as Record<string, unknown>).name;
    return typeof name === "string" ? name.trim() || undefined : undefined;
  }
  return undefined;
}

function pickNames(value: unknown): string[] | undefined {
  if (!value) return undefined;
  const arr = Array.isArray(value) ? value : [value];
  const names = arr.map(pickName).filter(Boolean) as string[];
  return names.length ? names : undefined;
}

/** Переводит ISO-8601 длительность (PT1H53M) в человекочитаемую "1 ч 53 мин". */
function humanizeDuration(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const m = value.match(/^PT(?:(\d+)H)?(?:(\d+)M)?$/);
  if (!m) return value; // уже человекочитаемая — отдаём как есть
  const hours = m[1] ? `${m[1]} ч` : "";
  const mins = m[2] ? `${m[2]} мин` : "";
  return [hours, mins].filter(Boolean).join(" ") || undefined;
}

/** Вычищает HTML-теги и схлопывает пробелы в тексте описания. */
function stripHtml(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const text = value
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&rsquo;|&lsquo;/g, "'")
    .replace(/[ \t]+/g, " ")
    .replace(/\s*\n\s*/g, "\n")
    .trim();
  return text || undefined;
}

const MONTHS_RU = [
  "января", "февраля", "марта", "апреля", "мая", "июня",
  "июля", "августа", "сентября", "октября", "ноября", "декабря",
];

/**
 * Переводит ISO-дату ("2026-08-29T19:00:00, +03:00") в человекочитаемую
 * "29 августа 2026, 19:00". Время 00:00 опускаем (для выставок оно не значимо).
 * Разбираем строку напрямую, чтобы не зависеть от часового пояса сервера.
 */
function formatDate(value: string | undefined): string | undefined {
  if (!value) return undefined;
  const m = value.match(/(\d{4})-(\d{2})-(\d{2})(?:T(\d{2}):(\d{2}))?/);
  if (!m) return value;
  const [, year, month, day, hh, mm] = m;
  const monthName = MONTHS_RU[parseInt(month, 10) - 1] ?? month;
  const datePart = `${parseInt(day, 10)} ${monthName} ${year}`;
  const hasTime = hh && mm && !(hh === "00" && mm === "00");
  return hasTime ? `${datePart}, ${hh}:${mm}` : datePart;
}

/** Разбивает строку жанров "Живопись, Интерактивная" в массив. */
function splitGenres(value: string | undefined): string[] | undefined {
  if (!value) return undefined;
  const parts = value
    .split(/[,;/]/)
    .map((s) => s.trim())
    .filter(Boolean);
  return parts.length ? parts : undefined;
}

/** Рейтинг "0"/"0.0" значит «оценок нет» — отбрасываем. */
function cleanRating(value: unknown): string | undefined {
  if (value == null) return undefined;
  const str = String(value);
  return parseFloat(str) > 0 ? str : undefined;
}

/**
 * Распознаёт анти-бот заглушку Афиши («Один момент…») вместо настоящей страницы.
 * Признаки: служебный заголовок-проверка или подозрительно короткий HTML без данных.
 */
function looksBlocked(html: string): boolean {
  if (/<title>\s*(Один момент|Just a moment|Подождите|Проверка|Доступ)/i.test(html)) {
    return true;
  }
  return html.length < 5000 && !/og:title|application\/ld\+json/i.test(html);
}

/**
 * Загружает HTML страницы с ретраями и таймаутом.
 * Лечит и разовые сетевые сбои («fetch failed»), и анти-бот заглушку Афиши —
 * пара повторов часто пробивается на настоящую страницу.
 */
async function fetchHtml(url: string): Promise<{ html: string; finalUrl: string }> {
  const headers = {
    "User-Agent": USER_AGENT,
    Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9",
  };

  let lastError: unknown;
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 12000);
      const res = await fetch(url, { headers, signal: controller.signal });
      clearTimeout(timer);

      if (!res.ok) {
        throw new Error(`Афиша вернула статус ${res.status}`);
      }
      const html = await res.text();
      if (looksBlocked(html)) {
        throw new Error("Афиша показала проверку доступа");
      }
      return { html, finalUrl: res.url || url };
    } catch (err) {
      lastError = err;
      if (attempt < 4) {
        await new Promise((resolve) => setTimeout(resolve, 500 * attempt));
      }
    }
  }

  const reason = lastError instanceof Error ? lastError.message : String(lastError);
  throw new Error(
    `Не удалось получить событие с Афиши (${reason}). ` +
      `Попробуйте ещё раз или выберите событие из каталога.`,
  );
}

/**
 * Достаёт цену из schema.org: offers.price / lowPrice (концерты, спектакли)
 * или priceRange (рестораны). Возвращает строку вида "от 850 ₽".
 */
function pickPrice(eventLd: Record<string, unknown>): string | undefined {
  const range = eventLd.priceRange;
  if (typeof range === "string" && range.trim()) return range.trim();

  const offersRaw = eventLd.offers;
  const offers = Array.isArray(offersRaw) ? offersRaw : offersRaw ? [offersRaw] : [];
  const prices = offers
    .map((o) => {
      const offer = o as Record<string, unknown>;
      const p = offer.lowPrice ?? offer.price;
      const num = p != null ? parseFloat(String(p)) : NaN;
      return Number.isFinite(num) && num > 0 ? num : null;
    })
    .filter((p): p is number => p != null);

  if (!prices.length) return undefined;
  return `от ${Math.min(...prices)} ₽`;
}

function pickImage(value: unknown): string | undefined {
  if (!value) return undefined;
  if (typeof value === "string") return value;
  if (Array.isArray(value)) return pickImage(value[0]);
  if (typeof value === "object") {
    const url = (value as Record<string, unknown>).url;
    return typeof url === "string" ? url : undefined;
  }
  return undefined;
}

/**
 * Скачивает и парсит страницу события afisha.ru.
 * Бросает понятную ошибку, если ссылка чужая или страница недоступна.
 */
export async function parseAfishaEvent(url: string): Promise<AfishaEvent> {
  if (!isAfishaUrl(url)) {
    throw new Error("Ссылка должна вести на afisha.ru");
  }

  const { html, finalUrl } = await fetchHtml(url);
  const $ = cheerio.load(html);

  // --- OpenGraph (надёжная база) ---
  const og = (prop: string): string | undefined =>
    $(`meta[property="og:${prop}"]`).attr("content")?.trim() || undefined;

  // --- JSON-LD (структурированные поля) ---
  const eventLd = selectMainLd(extractJsonLd($));

  const { id, slug, category } = parseUrlParts(finalUrl);

  const title =
    pickName(eventLd.name) ??
    og("title") ??
    ($("h1").first().text().trim() || slug);

  const event: AfishaEvent = {
    id,
    slug,
    sourceUrl: finalUrl,
    category,
    title,
    // alternateName у фильмов = оригинальное название, у событий = жанр/тип
    originalTitle: category === "movie" ? pickName(eventLd.alternateName) : undefined,
    image: pickImage(eventLd.image) ?? og("image"),
    description: stripHtml(pickName(eventLd.description) ?? og("description")),
    genres:
      pickNames(eventLd.genre) ??
      (category !== "movie" ? splitGenres(pickName(eventLd.alternateName)) : undefined),
    date: formatDate(pickName(eventLd.startDate ?? eventLd.datePublished)),
    country: pickName(eventLd.countryOfOrigin),
    duration: humanizeDuration(pickName(eventLd.duration)),
    ageRating: pickName(eventLd.contentRating ?? eventLd.typicalAgeRange),
    director: pickName(eventLd.director ?? eventLd.organizer ?? eventLd.author),
    venue: pickName(eventLd.location),
    price: pickPrice(eventLd),
    rating: cleanRating(
      (eventLd.aggregateRating as Record<string, unknown> | undefined)?.ratingValue,
    ),
    parsedAt: new Date().toISOString(),
  };

  return event;
}
