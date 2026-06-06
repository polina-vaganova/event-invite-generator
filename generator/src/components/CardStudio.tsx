"use client";

import { useState } from "react";
import type { AfishaEvent } from "@/lib/types";
import {
  CARD_STYLES,
  BG_COLORS,
  STICKERS,
  RELATIONSHIPS,
  TONES,
  draftMessage,
  type BgColor,
} from "@/lib/studio";

const AFISHA_URL = process.env.NEXT_PUBLIC_AFISHA_URL ?? "http://localhost:3000";

type Step = "design" | "details" | "generating" | "done";
const STEPS: { id: Step; label: string }[] = [
  { id: "design", label: "Дизайн" },
  { id: "details", label: "Детали" },
  { id: "generating", label: "Генерация" },
  { id: "done", label: "Готово" },
];

export default function CardStudio({ event }: { event: AfishaEvent }) {
  const [step, setStep] = useState<Step>("design");

  // Шаг 1 — дизайн
  const [styleId, setStyleId] = useState(CARD_STYLES[0].id);
  const [bgId, setBgId] = useState(BG_COLORS[0].id);
  const [stickers, setStickers] = useState<string[]>(["🎈"]);

  // Шаг 2 — детали
  const [recipient, setRecipient] = useState("");
  const [relationship, setRelationship] = useState(RELATIONSHIPS[0].id);
  const [tone, setTone] = useState(TONES[0].id);
  const [details, setDetails] = useState("");
  const [extra, setExtra] = useState("");

  // Результат (заглушка ИИ)
  const [message, setMessage] = useState("");

  const bg = BG_COLORS.find((c) => c.id === bgId) ?? BG_COLORS[0];

  function toggleSticker(s: string) {
    setStickers((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s].slice(-4),
    );
  }

  function generate() {
    setStep("generating");
    // ЗАГЛУШКА: имитируем работу ИИ. В Фазе 4 здесь будет запрос к ИИ-API.
    setTimeout(() => {
      setMessage(draftMessage({ recipient, tone }));
      setStep("done");
    }, 1100);
  }

  const activeIndex = STEPS.findIndex((s) => s.id === step);

  // На какой шаг можно перейти кликом по степперу.
  function canGoTo(id: Step): boolean {
    if (id === "generating") return false; // транзиентный шаг
    if (id === "done") return Boolean(message); // только если открытка готова
    return true; // дизайн и детали — всегда
  }
  function goTo(id: Step) {
    if (canGoTo(id)) setStep(id);
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-6">
      {/* Степпер */}
      <div className="mb-6 flex flex-wrap items-center gap-3">
        <span className="font-semibold">
          Позвать красиво <span className="brand-text-gradient">✨</span>
        </span>
        <span className="text-muted">→</span>
        <ol className="flex flex-wrap items-center gap-2">
          {STEPS.map((s, i) => {
            const done = i < activeIndex;
            const current = i === activeIndex;
            const clickable = canGoTo(s.id) && !current;
            return (
              <li key={s.id} className="flex items-center gap-2 text-sm">
                <button
                  type="button"
                  onClick={() => goTo(s.id)}
                  disabled={!clickable}
                  className={`flex items-center gap-2 ${clickable ? "cursor-pointer hover:opacity-80" : "cursor-default"}`}
                >
                  <span
                    className={`flex h-6 w-6 items-center justify-center rounded-full text-xs font-bold ${
                      current
                        ? "bg-foreground text-background"
                        : done
                          ? "bg-lime text-foreground"
                          : "bg-border text-muted"
                    }`}
                  >
                    {done ? "✓" : i + 1}
                  </span>
                  <span className={current ? "font-semibold" : "text-muted"}>{s.label}</span>
                </button>
                {i < STEPS.length - 1 && <span className="text-border">·</span>}
              </li>
            );
          })}
        </ol>
      </div>

      {/* Карточка события (контекст всегда виден) */}
      <EventChip event={event} />

      {/* Контент шага */}
      <div className="mt-4 rounded-2xl border border-border bg-card p-5 sm:p-6">
        {step === "design" && (
          <DesignStep
            styleId={styleId}
            setStyleId={setStyleId}
            bgId={bgId}
            setBgId={setBgId}
            stickers={stickers}
            toggleSticker={toggleSticker}
            onNext={() => setStep("details")}
          />
        )}

        {step === "details" && (
          <DetailsStep
            recipient={recipient}
            setRecipient={setRecipient}
            relationship={relationship}
            setRelationship={setRelationship}
            tone={tone}
            setTone={setTone}
            details={details}
            setDetails={setDetails}
            extra={extra}
            setExtra={setExtra}
            onBack={() => setStep("design")}
            onGenerate={generate}
          />
        )}

        {step === "generating" && <GeneratingStep />}

        {step === "done" && (
          <DoneStep
            event={event}
            bg={bg}
            message={message}
            stickers={stickers}
            onEdit={() => setStep("details")}
            onRegenerate={generate}
          />
        )}
      </div>
    </div>
  );
}

/* ---------- Карточка события ---------- */
function EventChip({ event }: { event: AfishaEvent }) {
  const meta = [event.date, event.venue].filter(Boolean).join(" · ");
  return (
    <div className="flex items-center gap-4 rounded-2xl border border-border bg-card p-4">
      {event.image && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          src={event.image}
          alt={event.title}
          className="h-16 w-16 shrink-0 rounded-xl object-cover"
        />
      )}
      <div className="min-w-0">
        <div className="text-xs uppercase tracking-wide text-muted">Событие</div>
        <div className="truncate font-semibold">{event.title}</div>
        {meta && <div className="truncate text-sm text-muted">{meta}</div>}
      </div>
      <a
        href={AFISHA_URL}
        className="ml-auto shrink-0 text-sm text-accent hover:underline"
      >
        Изменить
      </a>
    </div>
  );
}

/* ---------- Шаг 1: Дизайн ---------- */
function DesignStep(props: {
  styleId: string;
  setStyleId: (v: string) => void;
  bgId: string;
  setBgId: (v: string) => void;
  stickers: string[];
  toggleSticker: (s: string) => void;
  onNext: () => void;
}) {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h2 className="font-semibold">1. Выберите стиль открытки</h2>
        <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
          {CARD_STYLES.map((s) => {
            const active = s.id === props.styleId;
            return (
              <button
                key={s.id}
                onClick={() => props.setStyleId(s.id)}
                className={`flex flex-col items-center gap-1 rounded-xl border p-4 transition ${
                  active
                    ? "border-foreground ring-1 ring-foreground"
                    : "border-border hover:border-foreground/40"
                }`}
              >
                <span className="text-2xl">{s.emoji}</span>
                <span className="text-sm font-medium">{s.label}</span>
              </button>
            );
          })}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold">Цвет фона</h3>
        <div className="mt-2 flex flex-wrap gap-3">
          {BG_COLORS.map((c) => (
            <button
              key={c.id}
              onClick={() => props.setBgId(c.id)}
              style={{ backgroundColor: c.hex, width: 40, height: 40 }}
              className={`shrink-0 rounded-full border transition ${
                c.id === props.bgId
                  ? "border-foreground ring-2 ring-foreground ring-offset-2"
                  : "border-black/10"
              }`}
              aria-label={c.id}
            />
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold">Дополните дизайн</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {STICKERS.map((s) => {
            const active = props.stickers.includes(s);
            return (
              <button
                key={s}
                onClick={() => props.toggleSticker(s)}
                style={{ width: 44, height: 44 }}
                className={`flex shrink-0 items-center justify-center rounded-full text-xl transition ${
                  active ? "bg-lime ring-2 ring-foreground" : "bg-background hover:bg-border"
                }`}
              >
                {s}
              </button>
            );
          })}
        </div>
      </div>

      <button
        onClick={props.onNext}
        className="w-full rounded-full bg-foreground py-3 font-semibold text-background transition hover:opacity-90"
      >
        Далее
      </button>
    </div>
  );
}

/* ---------- Шаг 2: Детали ---------- */
function DetailsStep(props: {
  recipient: string;
  setRecipient: (v: string) => void;
  relationship: string;
  setRelationship: (v: string) => void;
  tone: string;
  setTone: (v: string) => void;
  details: string;
  setDetails: (v: string) => void;
  extra: string;
  setExtra: (v: string) => void;
  onBack: () => void;
  onGenerate: () => void;
}) {
  return (
    <div className="flex flex-col gap-5">
      <h2 className="font-semibold">2. Расскажите о получателе</h2>

      <Field label="Кого приглашаете?">
        <input
          value={props.recipient}
          onChange={(e) => props.setRecipient(e.target.value)}
          placeholder="Имя получателя"
          className="w-full rounded-xl border border-border px-4 py-3 outline-none focus:border-foreground"
        />
      </Field>

      <Field label="Ваши отношения">
        <ChipRow options={RELATIONSHIPS} value={props.relationship} onChange={props.setRelationship} />
      </Field>

      <Field label="Тон приглашения">
        <ChipRow options={TONES} value={props.tone} onChange={props.setTone} />
      </Field>

      <Field label="Что добавить в открытку?">
        <textarea
          value={props.details}
          onChange={(e) => props.setDetails(e.target.value)}
          placeholder="Напомни, что это будет лучший вечер месяца 🎉"
          rows={2}
          className="w-full resize-none rounded-xl border border-border px-4 py-3 outline-none focus:border-foreground"
        />
      </Field>

      <Field label="Дополнительно (необязательно)">
        <textarea
          value={props.extra}
          onChange={(e) => props.setExtra(e.target.value)}
          placeholder="Любимые шутки, общие воспоминания, планы…"
          rows={2}
          className="w-full resize-none rounded-xl border border-border px-4 py-3 outline-none focus:border-foreground"
        />
      </Field>

      <div className="flex gap-3">
        <button
          onClick={props.onBack}
          className="rounded-full border border-border px-6 py-3 font-medium transition hover:border-foreground"
        >
          Назад
        </button>
        <button
          onClick={props.onGenerate}
          className="flex-1 rounded-full bg-foreground py-3 font-semibold text-background transition hover:opacity-90"
        >
          Создать открытку ✨
        </button>
      </div>
      <p className="text-center text-xs text-muted">
        🚧 Заглушка: текст генерируется по шаблону. Реальный ИИ подключим позже.
      </p>
    </div>
  );
}

/* ---------- Шаг 3: Генерация ---------- */
function GeneratingStep() {
  return (
    <div className="flex flex-col items-center gap-4 py-16 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-border border-t-foreground" />
      <p className="font-semibold">ИИ создаёт открытку…</p>
      <p className="text-sm text-muted">Подбираем текст под тон и событие</p>
    </div>
  );
}

/* ---------- Шаг 4: Готово ---------- */
function DoneStep(props: {
  event: AfishaEvent;
  bg: BgColor;
  message: string;
  stickers: string[];
  onEdit: () => void;
  onRegenerate: () => void;
}) {
  const { event, bg, message, stickers } = props;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">3. Ваша открытка готова!</h2>
        <button onClick={props.onRegenerate} className="text-sm text-accent hover:underline">
          ↻ Сгенерировать заново
        </button>
      </div>

      <CardPreview event={event} bg={bg} message={message} stickers={stickers} />

      {/* Шеринг */}
      <div>
        <h3 className="text-sm font-semibold">Отправьте приглашение</h3>
        <ShareRow event={event} message={message} />
      </div>

      {/* Предпросмотр у получателя */}
      <div>
        <h3 className="text-sm font-semibold">Предпросмотр у получателя</h3>
        <div className="mt-2 rounded-2xl border border-border bg-background p-4">
          <div className="mb-2 flex items-center gap-2">
            <span className="h-8 w-8 rounded-full bg-gradient-to-br from-accent to-accent-2" />
            <div>
              <div className="text-sm font-semibold">Получатель</div>
              <div className="text-xs text-green-600">онлайн</div>
            </div>
          </div>
          <div className="max-w-xs">
            <CardPreview event={event} bg={bg} message={message} stickers={stickers} compact />
            <p className="mt-1 text-sm">Не пропусти! Будет легендарно 🔥</p>
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2 sm:flex-row">
        <button
          onClick={props.onEdit}
          className="rounded-full border border-border px-6 py-3 font-medium transition hover:border-foreground"
        >
          ← Изменить детали
        </button>
      </div>
    </div>
  );
}

/* ---------- Открытка-превью (шаблон) ---------- */
function CardPreview({
  event,
  bg,
  message,
  stickers,
  compact = false,
}: {
  event: AfishaEvent;
  bg: BgColor;
  message: string;
  stickers: string[];
  compact?: boolean;
}) {
  const textColor = bg.light ? "text-white" : "text-[#14141a]";
  return (
    <div
      style={{ background: bg.hex }}
      className={`relative overflow-hidden rounded-2xl ${textColor} ${compact ? "p-3" : "p-6"}`}
    >
      {stickers.length > 0 && (
        <div className={`absolute right-3 top-2 ${compact ? "text-sm" : "text-2xl"}`}>
          {stickers.join(" ")}
        </div>
      )}
      <div className="flex items-stretch gap-4">
        <div className="flex flex-1 flex-col">
          <p
            className={`font-handwriting leading-tight ${compact ? "text-lg" : "text-3xl sm:text-4xl"}`}
          >
            {message}
          </p>
          {!compact && (
            <div className="mt-auto pt-4 text-sm">
              {event.date && <div>{event.date}</div>}
              {event.venue && <div className="opacity-80">{event.venue}</div>}
              <div className="mt-1 font-bold">{event.title}</div>
            </div>
          )}
        </div>
        {event.image && !compact && (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={event.image}
            alt={event.title}
            className="h-40 w-32 shrink-0 rounded-xl object-cover"
          />
        )}
      </div>
    </div>
  );
}

/* ---------- Шеринг (заглушки-интенты) ---------- */
function ShareRow({ event, message }: { event: AfishaEvent; message: string }) {
  // Ссылка-заглушка на будущий лендинг открытки (Фаза 4)
  const cardUrl = `${AFISHA_URL}/card/${event.id}`;
  const text = `${message} ${event.title}`;

  const links: { label: string; href: string }[] = [
    { label: "Telegram", href: `https://t.me/share/url?url=${encodeURIComponent(cardUrl)}&text=${encodeURIComponent(text)}` },
    { label: "WhatsApp", href: `https://wa.me/?text=${encodeURIComponent(`${text} ${cardUrl}`)}` },
    { label: "VK", href: `https://vk.com/share.php?url=${encodeURIComponent(cardUrl)}` },
  ];

  function copyLink() {
    navigator.clipboard?.writeText(cardUrl);
  }

  return (
    <div className="mt-2 flex flex-wrap gap-2">
      {links.map((l) => (
        <a
          key={l.label}
          href={l.href}
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:border-foreground"
        >
          {l.label}
        </a>
      ))}
      <button
        onClick={copyLink}
        className="rounded-full border border-border px-4 py-2 text-sm font-medium transition hover:border-foreground"
      >
        Скопировать ссылку
      </button>
    </div>
  );
}

/* ---------- Мелкие хелперы ---------- */
function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block">
      <span className="text-sm font-medium">{label}</span>
      <div className="mt-2">{children}</div>
    </label>
  );
}

function ChipRow({
  options,
  value,
  onChange,
}: {
  options: { id: string; label: string; emoji: string }[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((o) => {
        const active = o.id === value;
        return (
          <button
            key={o.id}
            onClick={() => onChange(o.id)}
            className={`rounded-full border px-4 py-2 text-sm font-medium transition ${
              active
                ? "border-foreground bg-lime"
                : "border-border hover:border-foreground/40"
            }`}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
