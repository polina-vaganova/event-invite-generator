/**
 * Адрес сервиса-генератора открыток (наш продукт).
 * В проде это была бы встроенная фича Афиши; в прототипе — отдельное приложение.
 */
export const GENERATOR_URL =
  process.env.NEXT_PUBLIC_GENERATOR_URL ?? "http://localhost:3001";

/** Ссылка «Позвать друга» — открывает генератор с выбранным событием по ID. */
export function inviteUrl(eventId: string): string {
  return `${GENERATOR_URL}/create?event=${encodeURIComponent(eventId)}`;
}
