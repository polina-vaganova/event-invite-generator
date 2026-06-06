import { fetchEvent } from "@/lib/afisha";
import CardStudio from "@/components/CardStudio";

const AFISHA_URL = process.env.NEXT_PUBLIC_AFISHA_URL ?? "http://localhost:3000";

export default async function CreatePage(props: PageProps<"/create">) {
  const { event: eventParam } = await props.searchParams;
  const id = Array.isArray(eventParam) ? eventParam[0] : eventParam;

  // Нет ID — просим выбрать событие на Афише.
  if (!id) {
    return (
      <Notice
        title="Сначала выберите событие"
        text="Откройте событие на Афише и нажмите «Позвать друга»."
        href={AFISHA_URL}
        cta="Перейти на Афишу"
      />
    );
  }

  // Получаем данные события по ID — НЕ парсим, а берём из API Афиши.
  const event = await fetchEvent(id);

  if (!event) {
    return (
      <Notice
        title="Событие не найдено"
        text="Не удалось получить данные события. Проверьте, что мини-Афиша запущена, и попробуйте снова."
        href={AFISHA_URL}
        cta="Выбрать другое событие"
      />
    );
  }

  return (
    <>
      <CardStudio event={event} />
      <FeatureStrip />
    </>
  );
}

const FEATURES = [
  {
    emoji: "🎯",
    title: "Учитывает событие",
    text: "ИИ подбирает тон под концерт, выставку или вечеринку",
  },
  {
    emoji: "🧩",
    title: "Помнит о деталях",
    text: "Добавьте важное — и оно сделает приглашение личным",
  },
  {
    emoji: "🎉",
    title: "Создаёт атмосферу",
    text: "Такое приглашение хочется читать, пересылать и принимать",
  },
  {
    emoji: "⚡",
    title: "Работает в пару кликов",
    text: "Открытка за 30 секунд — и отправляйте любым способом",
  },
];

function FeatureStrip() {
  return (
    <section className="border-t border-border bg-card">
      <div className="mx-auto max-w-6xl px-4 py-8">
        <h2 className="font-bold">ИИ-приглашения — новый способ звать друзей</h2>
        <div className="mt-4 grid gap-5 sm:grid-cols-2 lg:grid-cols-4">
          {FEATURES.map((f) => (
            <div key={f.title}>
              <div className="text-2xl">{f.emoji}</div>
              <div className="mt-1 font-semibold">{f.title}</div>
              <div className="text-sm text-muted">{f.text}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Notice({
  title,
  text,
  href,
  cta,
}: {
  title: string;
  text: string;
  href: string;
  cta: string;
}) {
  return (
    <div className="mx-auto max-w-md px-4 py-24 text-center">
      <h1 className="text-2xl font-bold">{title}</h1>
      <p className="mt-2 text-muted">{text}</p>
      <a
        href={href}
        className="brand-gradient mt-6 inline-block rounded-full px-6 py-3 font-semibold text-white"
      >
        {cta}
      </a>
    </div>
  );
}
