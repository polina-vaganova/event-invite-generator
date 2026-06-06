import Link from "next/link";

const AFISHA_URL = process.env.NEXT_PUBLIC_AFISHA_URL ?? "http://localhost:3000";

const STEPS = [
  { n: "1", title: "Выберите событие", text: "Подтягиваем данные прямо из Афиши" },
  { n: "2", title: "Стиль и получатель", text: "Романтично, по-дружески или с юмором" },
  { n: "3", title: "Открытка готова", text: "ИИ создаёт текст и визуал за секунды" },
];

export default function Home() {
  return (
    <div className="mx-auto max-w-5xl px-4 py-16">
      <section className="text-center">
        <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-card px-3 py-1 text-sm font-medium text-muted">
          <span className="font-bold text-[#ff3d2e]">Афиша</span> · встроенный сервис
        </span>
        <h1 className="mt-4 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
          Превратите <span className="brand-text-gradient">«Пойдём?»</span>
          <br />в открытку, которой делятся
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-lg text-muted">
          Сервис Афиши создаёт персональную открытку-приглашение на событие — с текстом
          и визуалом от ИИ. Отправьте её другу прямо из карточки события.
        </p>

        <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
          <a
            href={AFISHA_URL}
            className="brand-gradient rounded-full px-7 py-3 font-semibold text-white transition hover:opacity-90"
          >
            Выбрать событие на Афише →
          </a>
        </div>
        <p className="mt-3 text-sm text-muted">
          Обычно сюда попадают с карточки события на Афише по кнопке «Позвать друга»
        </p>
      </section>

      <section className="mt-16 grid gap-4 sm:grid-cols-3">
        {STEPS.map((s) => (
          <div key={s.n} className="rounded-2xl border border-border bg-card p-6">
            <div className="brand-gradient flex h-10 w-10 items-center justify-center rounded-full font-bold text-white">
              {s.n}
            </div>
            <h3 className="mt-4 font-semibold">{s.title}</h3>
            <p className="mt-1 text-sm text-muted">{s.text}</p>
          </div>
        ))}
      </section>

      <p className="mt-12 text-center text-sm text-muted">
        Демо: страница генерации открывается по ссылке вида{" "}
        <Link href="/create?event=6014552" className="text-accent underline">
          /create?event=6014552
        </Link>
      </p>
    </div>
  );
}
