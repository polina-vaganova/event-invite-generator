import type { NextRequest } from "next/server";
import { parseAfishaEvent, isAfishaUrl, eventIdFromUrl } from "@/lib/parser";
import { addEvent, getEvent } from "@/lib/store";

/**
 * POST /api/parse — добавить новое событие в каталог по ссылке afisha.ru.
 *
 * Это «наполнение базы Афиши» в прототипе: пользователь вставляет ссылку,
 * парсер достаёт данные, событие появляется в каталоге как настоящее.
 *
 * Тело запроса: { url: string }
 */
export async function POST(req: NextRequest) {
  let url: unknown;
  try {
    ({ url } = await req.json());
  } catch {
    return Response.json({ error: "Ожидается JSON с полем url" }, { status: 400 });
  }

  if (typeof url !== "string" || !isAfishaUrl(url)) {
    return Response.json(
      { error: "Нужна корректная ссылка на событие afisha.ru" },
      { status: 400 },
    );
  }

  // Кэш-первый: если событие уже в каталоге — отдаём его, не дёргая Афишу.
  // Это бережёт лимиты Афиши и защищает от блокировок.
  const cached = await getEvent(eventIdFromUrl(url));
  if (cached) {
    return Response.json(cached, { status: 200 });
  }

  try {
    const event = await addEvent(await parseAfishaEvent(url));
    return Response.json(event, { status: 201 });
  } catch (err) {
    return Response.json(
      { error: (err as Error).message || "Не удалось разобрать страницу" },
      { status: 502 },
    );
  }
}
