import { getAllEvents } from "@/lib/store";

/**
 * GET /api/events — весь каталог событий.
 * Это публичный «API Афиши», которым пользуется генератор открыток.
 */
export async function GET() {
  return Response.json(await getAllEvents());
}
