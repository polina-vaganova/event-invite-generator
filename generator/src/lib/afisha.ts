import type { AfishaEvent } from "./types";

/**
 * Доступ к данным события через API Афиши.
 *
 * Ключевой момент архитектуры: генератор НЕ парсит страницы — он получает
 * готовые данные события по ID, как было бы при реальном внедрении в Афишу.
 * В проде нужно лишь заменить AFISHA_API_URL на внутренний API Афиши.
 */
const AFISHA_API_URL = process.env.AFISHA_API_URL ?? "http://localhost:3000";

/** Запрашивает событие по ID. Возвращает null, если не найдено или API недоступно. */
export async function fetchEvent(id: string): Promise<AfishaEvent | null> {
  try {
    const res = await fetch(`${AFISHA_API_URL}/api/event/${encodeURIComponent(id)}`, {
      // событие может меняться — не кэшируем жёстко
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as AfishaEvent;
  } catch {
    return null;
  }
}
