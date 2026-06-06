import type { NextRequest } from "next/server";
import { getEvent } from "@/lib/store";

/**
 * GET /api/event/[id] — одно событие по ID.
 *
 * Ключевая точка интеграции: генератор открыток дёргает именно этот эндпоинт,
 * чтобы получить данные события — как было бы с настоящим API Афиши.
 */
export async function GET(_req: NextRequest, ctx: RouteContext<"/api/event/[id]">) {
  const { id } = await ctx.params;
  const event = await getEvent(id);

  if (!event) {
    return Response.json({ error: "Событие не найдено" }, { status: 404 });
  }

  return Response.json(event);
}
