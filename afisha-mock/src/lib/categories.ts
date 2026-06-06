/** Человекочитаемые подписи категорий событий Афиши. */
const CATEGORY_LABELS: Record<string, { label: string; emoji: string }> = {
  movie: { label: "Кино", emoji: "🎬" },
  concert: { label: "Концерт", emoji: "🎵" },
  performance: { label: "Спектакль", emoji: "🎭" },
  theatre: { label: "Спектакль", emoji: "🎭" },
  exhibition: { label: "Выставка", emoji: "🖼" },
  restaurant: { label: "Ресторан", emoji: "🍽" },
};

export function categoryLabel(category: string): { label: string; emoji: string } {
  return CATEGORY_LABELS[category] ?? { label: "Событие", emoji: "✨" };
}
