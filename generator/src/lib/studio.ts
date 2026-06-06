/**
 * Константы и заглушки студии открыток.
 *
 * Текст пока генерируется по шаблонам (draftMessage) — это ЗАГЛУШКА под ИИ.
 * Когда подключим ИИ-API, заменим только draftMessage, остальной UI не изменится.
 */

export interface Option {
  id: string;
  label: string;
  emoji: string;
}

/** Шаг 1 — визуальный стиль открытки. */
export const CARD_STYLES: Option[] = [
  { id: "festive", label: "Праздничный", emoji: "🎂" },
  { id: "minimal", label: "Минимализм", emoji: "⚪" },
  { id: "meme", label: "Мемный", emoji: "⭐" },
  { id: "tender", label: "Нежный", emoji: "☁️" },
];

/** Цвета фона открытки. light=true → фон тёмный, текст белый. */
export interface BgColor {
  id: string;
  hex: string;
  light: boolean;
}
export const BG_COLORS: BgColor[] = [
  { id: "lime", hex: "#d6f24a", light: false },
  { id: "gray", hex: "#e6e6e9", light: false },
  { id: "purple", hex: "#7c3aed", light: true },
  { id: "blue", hex: "#4f7df0", light: true },
  { id: "olive", hex: "#9aa86a", light: false },
  { id: "peach", hex: "#f3c8a6", light: false },
  { id: "lavender", hex: "#d9c9f2", light: false },
];

/** Стикеры-украшения (шаг 1). */
export const STICKERS = ["🎈", "💜", "⭐", "☁️", "🎉", "🎂", "💚", "✨", "🔥", "🥂"];

/** Шаг 2 — отношения с получателем. */
export const RELATIONSHIPS: Option[] = [
  { id: "friends", label: "Друзья", emoji: "🤝" },
  { id: "couple", label: "Пара", emoji: "💕" },
  { id: "colleagues", label: "Коллеги", emoji: "💼" },
  { id: "family", label: "Семья", emoji: "🏡" },
];

/** Шаг 2 — тон приглашения. */
export const TONES: Option[] = [
  { id: "fun", label: "Весёлый", emoji: "😄" },
  { id: "warm", label: "Тёплый", emoji: "🤗" },
  { id: "romantic", label: "Романтичный", emoji: "💕" },
  { id: "creative", label: "Креативный", emoji: "🎨" },
];

/**
 * ЗАГЛУШКА генерации текста открытки.
 * Возвращает текст под выбранный тон. В будущем здесь будет вызов ИИ,
 * который учтёт получателя, отношения, событие и доп. пожелания.
 */
export function draftMessage(opts: { recipient: string; tone: string }): string {
  const name = opts.recipient.trim() || "Привет";
  const byTone: Record<string, string> = {
    fun: `${name}! Празднуем это так, как ты любишь — громко, душевно и до утра! 🎉`,
    warm: `${name}, давно хотел позвать тебя. Будет тепло и по-нашему 💛`,
    romantic: `${name}, проведём этот вечер вдвоём? Только ты и я ✨`,
    creative: `${name}, у меня идея на вечер — и без тебя она не считается 🚀`,
  };
  return byTone[opts.tone] ?? byTone.fun;
}
