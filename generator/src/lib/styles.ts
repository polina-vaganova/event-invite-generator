/**
 * Стили коммуникации открытки-приглашения.
 * На следующем этапе именно стиль будет задавать тон ИИ-генерации текста и визуала.
 */
export interface CommStyle {
  id: string;
  label: string;
  emoji: string;
  hint: string;
}

export const COMM_STYLES: CommStyle[] = [
  { id: "romantic", label: "Романтичный", emoji: "💕", hint: "Для второй половинки" },
  { id: "friendly", label: "Дружеский", emoji: "🤝", hint: "Для друга или компании" },
  { id: "family", label: "Семейный", emoji: "🏡", hint: "Для близких и родных" },
  { id: "funny", label: "Шуточный", emoji: "😄", hint: "С юмором и лёгкостью" },
];

export function getStyle(id: string): CommStyle | undefined {
  return COMM_STYLES.find((s) => s.id === id);
}
