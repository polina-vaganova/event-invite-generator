/**
 * Контракт данных события, который генератор получает от API Афиши.
 * Совпадает с моделью мини-Афиши — в проде это был бы внутренний API Афиши.
 */
export interface AfishaEvent {
  id: string;
  slug: string;
  sourceUrl: string;
  category: string;
  title: string;
  originalTitle?: string;
  image?: string;
  description?: string;
  genres?: string[];
  date?: string;
  country?: string;
  duration?: string;
  ageRating?: string;
  director?: string;
  venue?: string;
  price?: string;
  rating?: string;
  parsedAt: string;
}
